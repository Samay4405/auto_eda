"""
CSV to JSON conversion utilities optimized for frontend visualization and analysis.
Provides multiple JSON formats optimized for different use cases.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import logging
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class CSVToJSONConverter:
    """Enhanced CSV to JSON converter with multiple output formats"""
    
    def __init__(self):
        self.supported_formats = [
            "optimized",      # Optimized for frontend charts and tables
            "plotly",         # Optimized for Plotly.js
            "d3",             # Optimized for D3.js
            "raw",            # Raw data conversion
            "analytical",     # Optimized for data analysis
            "compressed"      # Compressed format for large datasets
        ]
    
    def convert_csv_to_json(
        self, 
        csv_path: str, 
        output_format: str = "optimized",
        sample_size: Optional[int] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Convert CSV to JSON with specified format optimizations
        
        Args:
            csv_path: Path to CSV file
            output_format: Format optimization type
            sample_size: Limit number of rows (for large datasets)
            include_metadata: Include metadata about the dataset
        
        Returns:
            Dictionary containing converted data and metadata
        """
        try:
            # Load CSV with intelligent parsing
            df = self._load_csv_intelligently(csv_path, sample_size)
            
            # Generate metadata
            metadata = self._generate_metadata(df, csv_path) if include_metadata else {}
            
            # Convert based on format
            if output_format == "optimized":
                data = self._convert_optimized_format(df)
            elif output_format == "plotly":
                data = self._convert_plotly_format(df)
            elif output_format == "d3":
                data = self._convert_d3_format(df)
            elif output_format == "analytical":
                data = self._convert_analytical_format(df)
            elif output_format == "compressed":
                data = self._convert_compressed_format(df)
            else:  # raw
                data = self._convert_raw_format(df)
            
            return {
                "success": True,
                "format": output_format,
                "metadata": metadata,
                "data": data,
                "conversion_timestamp": datetime.now().isoformat(),
                "converter_version": "2.0"
            }
            
        except Exception as e:
            logger.error(f"Error converting CSV to JSON: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "format": output_format,
                "conversion_timestamp": datetime.now().isoformat()
            }
    
    def _load_csv_intelligently(self, csv_path: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """Load CSV with intelligent type detection and error handling"""
        try:
            # First, try to detect encoding
            encoding = self._detect_encoding(csv_path)
            
            # Load with pandas
            df = pd.read_csv(
                csv_path,
                encoding=encoding,
                low_memory=False,
                parse_dates=True,
                infer_datetime_format=True
            )
            
            # Sample if requested
            if sample_size and len(df) > sample_size:
                df = df.sample(n=sample_size, random_state=42).sort_index()
            
            # Optimize data types
            df = self._optimize_datatypes(df)
            
            return df
            
        except Exception as e:
            logger.warning(f"Error loading CSV with intelligent parsing: {str(e)}")
            # Fallback to basic loading
            return pd.read_csv(csv_path)
    
    def _detect_encoding(self, csv_path: str) -> str:
        """Detect file encoding"""
        try:
            import chardet
            with open(csv_path, 'rb') as file:
                sample = file.read(10000)
                result = chardet.detect(sample)
                return result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
        except ImportError:
            return 'utf-8'
        except Exception:
            return 'utf-8'
    
    def _optimize_datatypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize pandas datatypes for better JSON conversion"""
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_data = optimized_df[col]
            
            # Skip if all null
            if col_data.isnull().all():
                continue
            
            # Try to convert to numeric
            if col_data.dtype == 'object':
                # Try numeric conversion
                numeric_converted = pd.to_numeric(col_data, errors='coerce')
                if not numeric_converted.isnull().all():
                    # If most values converted successfully
                    null_ratio = numeric_converted.isnull().sum() / len(col_data)
                    if null_ratio < 0.5:  # Less than 50% failed conversion
                        optimized_df[col] = numeric_converted
                        continue
                
                # Try datetime conversion
                try:
                    datetime_converted = pd.to_datetime(col_data, errors='coerce')
                    null_ratio = datetime_converted.isnull().sum() / len(col_data)
                    if null_ratio < 0.5:  # Less than 50% failed conversion
                        optimized_df[col] = datetime_converted
                        continue
                except:
                    pass
            
            # Optimize integer types
            elif col_data.dtype in ['int64']:
                if col_data.min() >= 0 and col_data.max() <= 2**31 - 1:
                    optimized_df[col] = col_data.astype('int32')
            
            # Optimize float types
            elif col_data.dtype in ['float64']:
                if col_data.min() >= np.finfo(np.float32).min and col_data.max() <= np.finfo(np.float32).max:
                    optimized_df[col] = col_data.astype('float32')
        
        return optimized_df
    
    def _generate_metadata(self, df: pd.DataFrame, csv_path: str) -> Dict[str, Any]:
        """Generate comprehensive metadata about the dataset"""
        return {
            "source": {
                "file_path": str(csv_path),
                "file_name": Path(csv_path).name,
                "file_size_bytes": Path(csv_path).stat().st_size if Path(csv_path).exists() else 0
            },
            "structure": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "memory_usage_bytes": int(df.memory_usage(deep=True).sum())
            },
            "data_types": {
                "numerical_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                "datetime_columns": df.select_dtypes(include=['datetime64']).columns.tolist(),
                "boolean_columns": df.select_dtypes(include=['bool']).columns.tolist(),
                "column_types": df.dtypes.astype(str).to_dict()
            },
            "quality": {
                "completeness_percent": float((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100),
                "missing_values_by_column": df.isnull().sum().to_dict(),
                "duplicate_rows": int(df.duplicated().sum()),
                "unique_values_by_column": df.nunique().to_dict()
            },
            "statistics": {
                "numerical_summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
                "categorical_summary": self._get_categorical_summary(df)
            },
            "creation_info": {
                "created_at": datetime.now().isoformat(),
                "created_by": "CSVToJSONConverter",
                "conversion_id": uuid.uuid4().hex
            }
        }
    
    def _get_categorical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for categorical columns"""
        summary = {}
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            summary[col] = {
                "unique_count": int(df[col].nunique()),
                "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "top_5_values": value_counts.head(5).to_dict()
            }
        
        return summary
    
    def _convert_optimized_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to optimized format for frontend visualization"""
        return {
            "format_type": "optimized",
            "columns": self._get_column_info(df),
            "records": self._convert_to_records_optimized(df),
            "summary": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "data_types": df.dtypes.astype(str).to_dict()
            }
        }
    
    def _convert_plotly_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to format optimized for Plotly.js"""
        plotly_data = {"format_type": "plotly"}
        
        # For each column, create arrays suitable for Plotly
        for col in df.columns:
            plotly_data[col] = self._convert_series_for_plotly(df[col])
        
        # Add index as a separate array for x-axis use
        plotly_data["_index"] = list(range(len(df)))
        
        # Add column metadata
        plotly_data["_metadata"] = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "numerical_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist()
        }
        
        return plotly_data
    
    def _convert_d3_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to format optimized for D3.js"""
        return {
            "format_type": "d3",
            "data": [
                {col: self._convert_value_for_json(val) for col, val in row.items()}
                for row in df.to_dict('records')
            ],
            "columns": [
                {
                    "name": col,
                    "type": self._get_d3_column_type(df[col]),
                    "domain": self._get_column_domain(df[col])
                }
                for col in df.columns
            ],
            "dimensions": {
                "rows": len(df),
                "columns": len(df.columns)
            }
        }
    
    def _convert_analytical_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to format optimized for data analysis"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            "format_type": "analytical",
            "data": {
                "records": [
                    {col: self._convert_value_for_json(val) for col, val in row.items()}
                    for row in df.to_dict('records')
                ],
                "by_column": {col: df[col].tolist() for col in df.columns}
            },
            "analysis": {
                "numerical_analysis": {
                    col: {
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "std": float(df[col].std()),
                        "min": float(df[col].min()),
                        "max": float(df[col].max()),
                        "quartiles": [
                            float(df[col].quantile(0.25)),
                            float(df[col].quantile(0.5)),
                            float(df[col].quantile(0.75))
                        ]
                    } for col in numerical_cols
                },
                "categorical_analysis": {
                    col: {
                        "unique_count": int(df[col].nunique()),
                        "value_counts": df[col].value_counts().to_dict(),
                        "mode": str(df[col].mode().iloc[0]) if not df[col].empty else None
                    } for col in categorical_cols
                },
                "correlation_matrix": df[numerical_cols].corr().to_dict() if len(numerical_cols) > 1 else {}
            }
        }
    
    def _convert_compressed_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to compressed format for large datasets"""
        # Use column-wise storage for better compression
        compressed_data = {
            "format_type": "compressed",
            "compression_info": {
                "original_size": len(df),
                "storage_method": "columnar"
            },
            "columns": {}
        }
        
        for col in df.columns:
            col_data = df[col]
            
            # Handle different data types with compression
            if pd.api.types.is_numeric_dtype(col_data):
                # Store numerical data as arrays
                compressed_data["columns"][col] = {
                    "type": "numerical",
                    "values": col_data.tolist(),
                    "null_positions": col_data.isnull().tolist() if col_data.isnull().any() else None
                }
            elif pd.api.types.is_categorical_dtype(col_data) or col_data.nunique() < len(col_data) * 0.5:
                # Use categorical encoding for repetitive data
                categories = col_data.unique().tolist()
                indices = [categories.index(val) if pd.notna(val) else -1 for val in col_data]
                
                compressed_data["columns"][col] = {
                    "type": "categorical",
                    "categories": [self._convert_value_for_json(cat) for cat in categories],
                    "indices": indices
                }
            else:
                # Store as regular array for other types
                compressed_data["columns"][col] = {
                    "type": "string",
                    "values": [self._convert_value_for_json(val) for val in col_data]
                }
        
        return compressed_data
    
    def _convert_raw_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert to raw format with minimal processing"""
        return {
            "format_type": "raw",
            "data": [
                {col: self._convert_value_for_json(val) for col, val in row.items()}
                for row in df.to_dict('records')
            ],
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    
    def _get_column_info(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Get detailed information about each column"""
        column_info = []
        
        for col in df.columns:
            col_data = df[col]
            info = {
                "name": col,
                "display_name": col.replace('_', ' ').title(),
                "data_type": str(col_data.dtype),
                "nullable": bool(col_data.isnull().any()),
                "unique_count": int(col_data.nunique()),
                "missing_count": int(col_data.isnull().sum())
            }
            
            # Add type-specific information
            if pd.api.types.is_numeric_dtype(col_data):
                info.update({
                    "min_value": float(col_data.min()) if pd.notna(col_data.min()) else None,
                    "max_value": float(col_data.max()) if pd.notna(col_data.max()) else None,
                    "mean_value": float(col_data.mean()) if pd.notna(col_data.mean()) else None,
                    "column_category": "numerical"
                })
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                info.update({
                    "min_date": col_data.min().isoformat() if pd.notna(col_data.min()) else None,
                    "max_date": col_data.max().isoformat() if pd.notna(col_data.max()) else None,
                    "column_category": "datetime"
                })
            else:
                most_common = col_data.mode()
                info.update({
                    "most_common_value": str(most_common.iloc[0]) if len(most_common) > 0 else None,
                    "column_category": "categorical"
                })
            
            column_info.append(info)
        
        return column_info
    
    def _convert_to_records_optimized(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to optimized records format"""
        records = []
        
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                value = row[col]
                record[col] = self._convert_value_for_json(value)
            records.append(record)
        
        return records
    
    def _convert_series_for_plotly(self, series: pd.Series) -> List[Any]:
        """Convert pandas Series to format suitable for Plotly"""
        return [self._convert_value_for_json(val) for val in series]
    
    def _convert_value_for_json(self, value: Any) -> Any:
        """Convert individual value to JSON-serializable format"""
        if pd.isna(value):
            return None
        elif isinstance(value, (np.integer, int)):
            return int(value)
        elif isinstance(value, (np.floating, float)):
            return float(value)
        elif isinstance(value, np.bool_):
            return bool(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, np.ndarray):
            return value.tolist()
        else:
            return str(value)
    
    def _get_d3_column_type(self, series: pd.Series) -> str:
        """Get D3-compatible column type"""
        if pd.api.types.is_numeric_dtype(series):
            return "quantitative"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "temporal"
        else:
            return "nominal"
    
    def _get_column_domain(self, series: pd.Series) -> List[Any]:
        """Get domain (range of values) for a column"""
        if pd.api.types.is_numeric_dtype(series):
            return [float(series.min()), float(series.max())]
        elif pd.api.types.is_datetime64_any_dtype(series):
            return [series.min().isoformat(), series.max().isoformat()]
        else:
            return series.unique().tolist()[:20]  # Limit to 20 unique values
    
    def save_json_to_file(self, json_data: Dict[str, Any], output_path: str) -> bool:
        """Save JSON data to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to file: {str(e)}")
            return False
    
    def batch_convert_csvs(
        self, 
        csv_directory: str, 
        output_directory: str, 
        output_format: str = "optimized"
    ) -> Dict[str, Any]:
        """Convert multiple CSV files in a directory"""
        csv_dir = Path(csv_directory)
        output_dir = Path(output_directory)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "successful_conversions": [],
            "failed_conversions": [],
            "total_files": 0,
            "batch_id": uuid.uuid4().hex
        }
        
        csv_files = list(csv_dir.glob("*.csv"))
        results["total_files"] = len(csv_files)
        
        for csv_file in csv_files:
            try:
                # Convert CSV to JSON
                json_data = self.convert_csv_to_json(str(csv_file), output_format)
                
                if json_data["success"]:
                    # Save to output directory
                    output_file = output_dir / f"{csv_file.stem}_{output_format}.json"
                    if self.save_json_to_file(json_data, str(output_file)):
                        results["successful_conversions"].append({
                            "input_file": str(csv_file),
                            "output_file": str(output_file),
                            "format": output_format
                        })
                    else:
                        results["failed_conversions"].append({
                            "input_file": str(csv_file),
                            "error": "Failed to save JSON file"
                        })
                else:
                    results["failed_conversions"].append({
                        "input_file": str(csv_file),
                        "error": json_data.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["failed_conversions"].append({
                    "input_file": str(csv_file),
                    "error": str(e)
                })
        
        return results


# Utility functions for easy usage
def convert_csv_to_optimized_json(csv_path: str, output_path: str = None) -> Dict[str, Any]:
    """Quick utility to convert CSV to optimized JSON format"""
    converter = CSVToJSONConverter()
    result = converter.convert_csv_to_json(csv_path, "optimized")
    
    if output_path and result["success"]:
        converter.save_json_to_file(result, output_path)
    
    return result


def convert_csv_for_plotly(csv_path: str) -> Dict[str, Any]:
    """Quick utility to convert CSV for Plotly usage"""
    converter = CSVToJSONConverter()
    return converter.convert_csv_to_json(csv_path, "plotly")


def convert_csv_for_analysis(csv_path: str) -> Dict[str, Any]:
    """Quick utility to convert CSV for data analysis"""
    converter = CSVToJSONConverter()
    return converter.convert_csv_to_json(csv_path, "analytical")