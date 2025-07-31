import numpy as np
import pandas as pd
import mlflow
import dagshub
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

dagshub.init(
    repo_owner='malhar.c.prajapati',
    repo_name='Stack-overflow-survey-2024-salary-prediction',
    mlflow=True
)

print("Loading pre-processed data...")
# Assuming 'final_dataset.csv' is in a 'data/processed' subdirectory relative to the script
df = pd.read_csv('../data/processed/final_dataset.csv', index_col=0)
X = df.drop(columns=['ConvertedCompYearly'])
y = df['ConvertedCompYearly'] 

if len(X) != len(y):
    raise ValueError(
        f"Mismatch in number of samples between processed features ({len(X)}) "
        f"and target variable ({len(y)}). Please regenerate processed.csv."
    )

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Data loaded. Training on {len(X_train)} samples, testing on {len(X_test)} samples.")

models_and_params = {
    'xgb': (XGBRegressor(random_state=42, n_jobs=-1, eval_metric='mae'), {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'max_depth': [3, 5]
    }),
    'rf': (RandomForestRegressor(random_state=42, n_jobs=-1), {
        'n_estimators': [100, 200],
        'max_depth': [10, 20],
        'min_samples_leaf': [2, 4]
    }),
    'lgbm': (LGBMRegressor(random_state=42, n_jobs=-1), {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'num_leaves': [31, 60]
    }),
    'gbr': (GradientBoostingRegressor(random_state=42), {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'max_depth': [3, 5]
    })
}

for model_name, (estimator, params) in models_and_params.items():
    
    full_pipeline = Pipeline([
        ('model', estimator)
    ])
    
    grid_search = GridSearchCV(
        estimator=estimator, 
        param_grid=params, 
        cv=3,
        scoring='neg_mean_squared_error',
        verbose=1, 
        n_jobs=-1
    )
    
    print(f"\n--- Starting GridSearchCV for {model_name} ---")
    
    with mlflow.start_run(run_name=f"GridSearch_{model_name}_on_processed_data") as run:
        mlflow.log_param('model_name', model_name)
        
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        
        # The model predicts on the same scale as the training data.
        # Since 'y_train' appears to be the original salary, 'y_pred' will be too.
        y_pred = best_model.predict(X_test)
        
        # FIX: The error was caused by applying np.expm1 to the original salary values,
        # which caused a numeric overflow. The target variable 'y' is already on the
        # original scale, so we can calculate metrics directly without transformation.
        
        metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
        
        print(f"--- Results for {model_name} ---")
        print(f"Best Params: {grid_search.best_params_}")
        print(f"Metrics: {metrics}")
        
        
        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metrics(metrics)
        
        mlflow.sklearn.log_model(
            sk_model=best_model,
            artifact_path='model',
            registered_model_name=f"{model_name}_salary_predictor_processed"
        )

print("\n--- All model training experiments are complete. ---")
