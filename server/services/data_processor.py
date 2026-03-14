import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import missingno as msno
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import io
import base64

class DataProcessor:
    """Handle data cleaning, transformation, and classification operations"""
    
    def __init__(self):
        self.scaler = None
        self.encoders = {}
        
    def get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic information about the dataset"""
        
        # Basic statistics
        basic_stats = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).to_dict(),
        }
        
        # Numerical columns statistics
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numerical_cols:
            basic_stats["numerical_summary"] = df[numerical_cols].describe().to_dict()
            
        # Categorical columns statistics
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            basic_stats["categorical_summary"] = {}
            for col in categorical_cols:
                basic_stats["categorical_summary"][col] = {
                    "unique_count": df[col].nunique(),
                    "most_frequent": df[col].mode().iloc[0] if not df[col].empty else None,
                    "value_counts": df[col].value_counts().head().to_dict()
                }
        
        return basic_stats
    
    def clean_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the dataset based on specified options"""
        
        cleaned_df = df.copy()
        operations_performed = []
        
        # Remove duplicates
        if options.get("remove_duplicates", True):
            initial_shape = cleaned_df.shape
            cleaned_df = cleaned_df.drop_duplicates()
            duplicates_removed = initial_shape[0] - cleaned_df.shape[0]
            if duplicates_removed > 0:
                operations_performed.append(f"Removed {duplicates_removed} duplicate rows")
        
        # Handle missing values
        missing_strategy = options.get("missing_strategy", "drop")
        
        if missing_strategy == "drop":
            # Drop rows with missing values
            threshold = options.get("drop_threshold", 0.5)  # Drop if more than 50% missing
            cleaned_df = cleaned_df.dropna(thresh=int(len(cleaned_df.columns) * threshold))
            operations_performed.append(f"Dropped rows with more than {threshold*100}% missing values")
            
        elif missing_strategy == "impute":
            # Impute missing values
            numerical_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            categorical_cols = cleaned_df.select_dtypes(include=['object']).columns
            
            # Numerical imputation
            if len(numerical_cols) > 0:
                num_strategy = options.get("numerical_impute_strategy", "mean")
                imputer = SimpleImputer(strategy=num_strategy)
                cleaned_df[numerical_cols] = imputer.fit_transform(cleaned_df[numerical_cols])
                operations_performed.append(f"Imputed numerical columns using {num_strategy}")
            
            # Categorical imputation
            if len(categorical_cols) > 0:
                cat_strategy = options.get("categorical_impute_strategy", "most_frequent")
                imputer = SimpleImputer(strategy=cat_strategy)
                cleaned_df[categorical_cols] = imputer.fit_transform(cleaned_df[categorical_cols])
                operations_performed.append(f"Imputed categorical columns using {cat_strategy}")
        
        # Remove outliers (for numerical columns)
        if options.get("remove_outliers", False):
            numerical_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            outlier_method = options.get("outlier_method", "iqr")
            
            for col in numerical_cols:
                if outlier_method == "iqr":
                    Q1 = cleaned_df[col].quantile(0.25)
                    Q3 = cleaned_df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers_mask = (cleaned_df[col] < lower_bound) | (cleaned_df[col] > upper_bound)
                    outliers_count = outliers_mask.sum()
                    
                    if outliers_count > 0:
                        cleaned_df = cleaned_df[~outliers_mask]
                        operations_performed.append(f"Removed {outliers_count} outliers from {col}")
        
        # Data type conversions
        if options.get("convert_dtypes", False):
            # Auto-convert data types
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':
                    # Try to convert to datetime
                    try:
                        cleaned_df[col] = pd.to_datetime(cleaned_df[col])
                        operations_performed.append(f"Converted {col} to datetime")
                        continue
                    except:
                        pass
                    
                    # Try to convert to numeric
                    try:
                        cleaned_df[col] = pd.to_numeric(cleaned_df[col])
                        operations_performed.append(f"Converted {col} to numeric")
                    except:
                        pass
        
        return {
            "cleaned_data": cleaned_df.to_dict('records'),
            "shape": cleaned_df.shape,
            "operations_performed": operations_performed,
            "cleaning_summary": {
                "original_shape": df.shape,
                "cleaned_shape": cleaned_df.shape,
                "rows_removed": df.shape[0] - cleaned_df.shape[0],
                "missing_values_after": cleaned_df.isnull().sum().to_dict()
            }
        }
    
    def transform_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the dataset (scaling, encoding, feature engineering)"""
        
        transformed_df = df.copy()
        operations_performed = []
        
        # Scaling numerical features
        scaling_method = options.get("scaling_method", "none")
        
        if scaling_method != "none":
            numerical_cols = transformed_df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numerical_cols) > 0:
                if scaling_method == "standard":
                    self.scaler = StandardScaler()
                elif scaling_method == "minmax":
                    self.scaler = MinMaxScaler()
                
                transformed_df[numerical_cols] = self.scaler.fit_transform(transformed_df[numerical_cols])
                operations_performed.append(f"Applied {scaling_method} scaling to numerical columns")
        
        # Encoding categorical variables
        encoding_method = options.get("encoding_method", "none")
        
        if encoding_method != "none":
            categorical_cols = transformed_df.select_dtypes(include=['object']).columns.tolist()
            
            if len(categorical_cols) > 0:
                for col in categorical_cols:
                    if encoding_method == "label":
                        encoder = LabelEncoder()
                        transformed_df[col] = encoder.fit_transform(transformed_df[col].astype(str))
                        self.encoders[col] = encoder
                        operations_performed.append(f"Applied label encoding to {col}")
                    
                    elif encoding_method == "onehot":
                        # One-hot encoding
                        dummies = pd.get_dummies(transformed_df[col], prefix=col)
                        transformed_df = pd.concat([transformed_df.drop(col, axis=1), dummies], axis=1)
                        operations_performed.append(f"Applied one-hot encoding to {col}")
        
        # Feature engineering
        if options.get("create_features", False):
            # Create polynomial features for numerical columns
            numerical_cols = transformed_df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numerical_cols) >= 2:
                # Create interaction features between first two numerical columns
                col1, col2 = numerical_cols[0], numerical_cols[1]
                transformed_df[f"{col1}_{col2}_interaction"] = transformed_df[col1] * transformed_df[col2]
                operations_performed.append(f"Created interaction feature: {col1}_{col2}_interaction")
        
        return {
            "transformed_data": transformed_df.to_dict('records'),
            "shape": transformed_df.shape,
            "operations_performed": operations_performed,
            "new_columns": [col for col in transformed_df.columns if col not in df.columns],
            "transformation_summary": {
                "original_columns": len(df.columns),
                "transformed_columns": len(transformed_df.columns),
                "features_added": len(transformed_df.columns) - len(df.columns)
            }
        }
    
    def classify_data(self, df: pd.DataFrame, options: Dict[str, Any]) -> Dict[str, Any]:
        """Classify and analyze data types and patterns"""
        
        classification_results = {
            "column_types": {},
            "data_patterns": {},
            "recommendations": []
        }
        
        for col in df.columns:
            column_info = {
                "dtype": str(df[col].dtype),
                "unique_count": df[col].nunique(),
                "null_count": df[col].isnull().sum(),
                "null_percentage": (df[col].isnull().sum() / len(df)) * 100
            }
            
            # Classify column type
            if df[col].dtype in ['int64', 'float64']:
                column_info["category"] = "numerical"
                column_info["stats"] = {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max()
                }
                
                # Check if it could be categorical (low unique values)
                if df[col].nunique() <= 10:
                    column_info["potential_categorical"] = True
                    classification_results["recommendations"].append(
                        f"Column '{col}' might be better treated as categorical (only {df[col].nunique()} unique values)"
                    )
                
            elif df[col].dtype == 'object':
                column_info["category"] = "categorical"
                column_info["value_counts"] = df[col].value_counts().head().to_dict()
                
                # Check if it could be datetime
                try:
                    pd.to_datetime(df[col].dropna().iloc[:100])
                    column_info["potential_datetime"] = True
                    classification_results["recommendations"].append(
                        f"Column '{col}' might be a datetime column"
                    )
                except:
                    pass
                
                # Check if it could be numerical
                try:
                    pd.to_numeric(df[col].dropna())
                    column_info["potential_numerical"] = True
                    classification_results["recommendations"].append(
                        f"Column '{col}' might be convertible to numerical"
                    )
                except:
                    pass
            
            elif df[col].dtype in ['datetime64[ns]']:
                column_info["category"] = "datetime"
                column_info["date_range"] = {
                    "start": str(df[col].min()),
                    "end": str(df[col].max())
                }
            
            else:
                column_info["category"] = "other"
            
            classification_results["column_types"][col] = column_info
        
        # Analyze data quality
        quality_score = 100
        quality_issues = []
        
        # Missing values penalty
        missing_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        if missing_percentage > 0:
            quality_score -= min(missing_percentage, 30)
            quality_issues.append(f"Dataset has {missing_percentage:.2f}% missing values")
        
        # Duplicate rows penalty
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        if duplicate_percentage > 0:
            quality_score -= min(duplicate_percentage * 2, 20)
            quality_issues.append(f"Dataset has {duplicate_percentage:.2f}% duplicate rows")
        
        classification_results["data_quality"] = {
            "score": max(quality_score, 0),
            "issues": quality_issues,
            "missing_values_percentage": missing_percentage,
            "duplicate_rows_percentage": duplicate_percentage
        }
        
        return classification_results
