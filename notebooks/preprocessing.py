from sklearn.base import BaseEstimator, TransformerMixin

class YearsCodeConverter(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.special_map = {
            "Less than 1 year": 0.5,
            "More than 50 years": 51
        }

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        for col in X_copy.columns:
            if X_copy[col].dtype == 'object':
                X_copy[col] = X_copy[col].replace(self.special_map)
            X_copy[col] = pd.to_numeric(X_copy[col], errors='coerce')
        return X_copy

    def get_feature_names_out(self, input_features=None):
        return input_features