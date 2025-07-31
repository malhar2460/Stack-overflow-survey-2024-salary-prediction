import numpy as np
import pandas as pd
import mlflow
import dagshub
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    OneHotEncoder, StandardScaler, OrdinalEncoder,
    FunctionTransformer, MultiLabelBinarizer
)
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge


def split_multiselect(X):
    """Splits semicolon-separated strings into a binary matrix."""
    if not isinstance(X, pd.Series):
        X = pd.Series(X)
    lists = X.fillna('').str.split(';')
    mlb = MultiLabelBinarizer()
    return mlb.fit_transform(lists)


def build_preprocessor(column_names):
    """
    Builds a ColumnTransformer based on provided column names dict:
    {
      'num': ['YearsCodePro'],
      'ord': ['Age'],
      'cat': [...],
      'multi': {
          'LanguageHaveWorkedWith': 'lang',
          ...
      }
    }
    """
    num_pipeline = Pipeline([
        ('imp', SimpleImputer(strategy='median')),
        ('scale', StandardScaler())
    ])

    ord_age_pipeline = Pipeline([
        ('imp', SimpleImputer(strategy='constant', fill_value='Missing')),
        ('enc', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])

    cat_pipeline = Pipeline([
        ('imp', SimpleImputer(strategy='constant', fill_value='Missing')),
        ('oh', OneHotEncoder(handle_unknown='ignore'))
    ])

    multi_pipeline = Pipeline([
        ('split', FunctionTransformer(split_multiselect, validate=False))
    ])

    transformers = []
    transformers.append(('num', num_pipeline, column_names['num']))
    transformers.append(('ord', ord_age_pipeline, column_names['ord']))
    transformers.append(('cat', cat_pipeline, column_names['cat']))
    for col, name in column_names['multi'].items():
        transformers.append((name, multi_pipeline, [col]))

    preprocessor = ColumnTransformer(transformers, remainder='drop')
    return preprocessor


def main():
    # Initialize tracking
    dagshub.init(
        repo_owner='malhar.c.prajapati',
        repo_name='Stack-overflow-survey-2024-salary-prediction',
        mlflow=True
    )

    print("Loading data...")
    df = pd.read_csv('../data/processed/features_labels.csv')

    # Normalize column names: strip whitespace
    df.columns = df.columns.str.strip()
    # Rename mismatched columns
    df.rename(columns={
        # 'YearsCode': 'YearsCodePro',
        'OpSysProfessional use': 'OpSys'
    }, inplace=True)

    # Drop missing target
    df.dropna(subset=['ConvertedCompYearly'], inplace=True)

    # Split X/y
    X = df.drop(columns=['ConvertedCompYearly'])
    y = np.log1p(df['ConvertedCompYearly'])

    # Expected columns
    expected_cols = {
        'num': ['YearsCodePro'],
        'ord': ['Age'],
        'cat': ['Country','EdLevel','DevType','RemoteWork','OpSys'],
        'multi': {
            'LanguageHaveWorkedWith': 'lang',
            'WebframeHaveWorkedWith': 'web',
            'DatabaseHaveWorkedWith': 'db',
            'PlatformHaveWorkedWith': 'plat'
        }
    }
    flat_expected = expected_cols['num'] + expected_cols['ord'] + expected_cols['cat'] + list(expected_cols['multi'].keys())
    missing = [c for c in flat_expected if c not in X.columns]
    if missing:
        raise ValueError(f"Missing columns in data after rename: {missing}")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

    # Build preprocessor
    preprocessor = build_preprocessor(expected_cols)

    # Models and hyperparameters
    models_and_params = {
        'gbr': (GradientBoostingRegressor(random_state=42), {
            'model__n_estimators': [100, 200],
            'model__max_depth': [3, 5]
        }),
        'rf': (RandomForestRegressor(random_state=42), {
            'model__n_estimators': [100, 200],
            'model__max_depth': [10, 20]
        }),
        'ridge': (Ridge(), {
            'model__alpha': [0.1, 1.0, 10.0]
        })
    }

    # Loop through models
    for model_name, (estimator, params) in models_and_params.items():
        full_pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', estimator)
        ])
        grid_search = GridSearchCV(
            full_pipeline, params, cv=3,
            scoring='neg_mean_absolute_error', n_jobs=-1, verbose=1
        )

        print(f"\n--- Starting GridSearchCV for {model_name} ---")
        with mlflow.start_run(run_name=f"GridSearch_{model_name}") as run:
            mlflow.log_param("model_name", model_name)

            grid_search.fit(X_train, y_train)
            best = grid_search.best_estimator_
            y_pred = best.predict(X_test)

            metrics = {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred)
            }
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metrics(metrics)

            mlflow.sklearn.log_model(
                sk_model=best,
                artifact_path="model",
                registered_model_name=f"{model_name}_salary_predictor"
            )

            print(f"--- Results for {model_name} ---")
            print(f"Best Params: {grid_search.best_params_}")
            print(f"Metrics: {metrics}")
            print(f"MLflow Run ID: {run.info.run_id}")

    print("\n--- All models trained and logged to MLflow. ---")


if __name__ == '__main__':
    main()