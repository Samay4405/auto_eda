"""
Specialized dashboard tools for different types of dashboards.
Each tool is optimized for specific dashboard types and use cases.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ExecutiveDashboardTool:
    """Specialized tool for executive summary dashboards"""
    
    @staticmethod
    def analyze_business_metrics(df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """Extract key business metrics for executive view"""
        metrics = {
            "kpis": [],
            "trends": [],
            "performance_summary": {},
            "executive_insights": []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Generate KPIs (top 4 most important metrics)
        for col in numerical_cols[:4]:
            if df[col].count() > 0:
                current_value = float(df[col].iloc[-1]) if len(df) > 0 else 0
                avg_value = float(df[col].mean())
                total_value = float(df[col].sum())
                
                # Calculate trend (last 30% vs first 30% of data)
                split_point = max(1, len(df) // 3)
                recent_avg = float(df[col].tail(split_point).mean())
                historical_avg = float(df[col].head(split_point).mean())
                
                trend_direction = "up" if recent_avg > historical_avg else "down"
                trend_percent = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg != 0 else 0
                
                metrics["kpis"].append({
                    "name": col.replace('_', ' ').title(),
                    "current_value": current_value,
                    "total_value": total_value,
                    "average_value": avg_value,
                    "trend_direction": trend_direction,
                    "trend_percent": float(trend_percent),
                    "format": "currency" if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'price', 'cost']) else "number",
                    "priority": "high" if any(keyword in col.lower() for keyword in ['revenue', 'profit', 'sales']) else "medium"
                })
        
        # Performance summary
        metrics["performance_summary"] = {
            "total_data_points": len(df),
            "time_period_covered": "Last data analysis period",
            "data_completeness": float((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100),
            "key_performance_areas": len([col for col in numerical_cols if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'profit', 'growth'])])
        }
        
        # Executive insights based on context
        if "sales" in context.lower():
            metrics["executive_insights"].extend([
                "Sales performance metrics indicate growth opportunities",
                "Revenue trends show potential for optimization"
            ])
        if "customer" in context.lower():
            metrics["executive_insights"].extend([
                "Customer data reveals segmentation opportunities",
                "Service metrics suggest improvement areas"
            ])
        if not metrics["executive_insights"]:
            metrics["executive_insights"] = [
                "Data analysis reveals key performance indicators",
                "Strategic insights available for decision making"
            ]
        
        return metrics
    
    @staticmethod
    def generate_executive_layout() -> Dict[str, Any]:
        """Generate layout optimized for executive dashboards"""
        return {
            "type": "executive",
            "grid_structure": {
                "columns": 4,
                "rows": 3,
                "gap": "large"
            },
            "sections": [
                {
                    "id": "kpi_row",
                    "type": "kpi_cards",
                    "span": {"col": "1/-1", "row": "1"},
                    "height": "compact",
                    "style": "minimal"
                },
                {
                    "id": "primary_chart",
                    "type": "trend_analysis",
                    "span": {"col": "1/3", "row": "2"},
                    "height": "standard",
                    "chart_type": "line_with_forecast"
                },
                {
                    "id": "secondary_chart",
                    "type": "performance_gauge",
                    "span": {"col": "3/4", "row": "2"},
                    "height": "standard",
                    "chart_type": "gauge_chart"
                },
                {
                    "id": "insights_panel",
                    "type": "executive_summary",
                    "span": {"col": "1/-1", "row": "3"},
                    "height": "compact",
                    "style": "highlight_box"
                }
            ],
            "styling": {
                "color_scheme": "executive_blue",
                "font_size": "large",
                "spacing": "generous",
                "borders": "minimal"
            }
        }
    
    @staticmethod
    def create_executive_charts(df: pd.DataFrame, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create charts optimized for executive viewing"""
        charts = []
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # KPI Cards
        for kpi in metrics["kpis"]:
            charts.append({
                "id": f"kpi_{kpi['name'].lower().replace(' ', '_')}",
                "type": "kpi_card",
                "config": {
                    "value": kpi["current_value"],
                    "title": kpi["name"],
                    "trend": kpi["trend_direction"],
                    "trend_percent": kpi["trend_percent"],
                    "format": kpi["format"],
                    "color": "#1e40af" if kpi["trend_direction"] == "up" else "#dc2626"
                },
                "size": "quarter_width",
                "priority": kpi["priority"]
            })
        
        # Primary trend chart
        if numerical_cols:
            primary_col = numerical_cols[0]
            charts.append({
                "id": "primary_chart",  # Match layout section ID
                "type": "line_chart",
                "config": {
                    "x": list(range(len(df))),
                    "y": df[primary_col].tolist(),
                    "title": f"{primary_col.replace('_', ' ').title()} Trend",
                    "color": "#1e40af",
                    "show_markers": True,
                    "smooth": True
                },
                "columns": [primary_col],  # Add columns for data extraction
                "size": "two_thirds_width",
                "priority": "high"
            })
        
        # Performance gauge
        if len(numerical_cols) > 1:
            second_col = numerical_cols[1]
            max_val = df[second_col].max()
            current_val = df[second_col].iloc[-1] if len(df) > 0 else 0
            
            charts.append({
                "id": "secondary_chart",  # Match layout section ID
                "type": "gauge_chart",
                "config": {
                    "value": float(current_val),
                    "max_value": float(max_val),
                    "title": f"{second_col.replace('_', ' ').title()} Performance",
                    "color": "#059669",
                    "thresholds": [0.3 * max_val, 0.7 * max_val, max_val]
                },
                "size": "one_third_width",
                "priority": "medium"
            })
        
        return charts


class DataQualityDashboardTool:
    """Specialized tool for data quality assessment dashboards"""
    
    @staticmethod
    def analyze_data_quality_comprehensive(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality analysis"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        quality_report = {
            "overall_score": 0,
            "completeness": {},
            "consistency": {},
            "validity": {},
            "outliers": {},
            "recommendations": []
        }
        
        # Completeness Analysis
        quality_report["completeness"] = {
            "total_completeness": float((total_cells - missing_cells) / total_cells * 100),
            "column_completeness": {},
            "missing_patterns": df.isnull().sum().to_dict()
        }
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            completeness_percent = float((len(df) - missing_count) / len(df) * 100)
            quality_report["completeness"]["column_completeness"][col] = {
                "completeness_percent": completeness_percent,
                "missing_count": int(missing_count),
                "status": "good" if completeness_percent > 95 else "warning" if completeness_percent > 80 else "critical"
            }
        
        # Validity Analysis (data type consistency)
        quality_report["validity"] = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Check for negative values where they might not make sense
                negative_count = (df[col] < 0).sum()
                quality_report["validity"][col] = {
                    "data_type": str(df[col].dtype),
                    "negative_values": int(negative_count),
                    "zero_values": int((df[col] == 0).sum()),
                    "unique_values": int(df[col].nunique()),
                    "status": "good" if negative_count == 0 else "warning"
                }
            else:
                # For categorical data
                quality_report["validity"][col] = {
                    "data_type": str(df[col].dtype),
                    "unique_values": int(df[col].nunique()),
                    "most_frequent": str(df[col].mode().iloc[0]) if not df[col].empty else "N/A",
                    "status": "good"
                }
        
        # Outlier Detection
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_mask = (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
            outlier_count = outlier_mask.sum()
            
            quality_report["outliers"][col] = {
                "outlier_count": int(outlier_count),
                "outlier_percent": float((outlier_count / len(df)) * 100),
                "lower_bound": float(Q1 - 1.5 * IQR),
                "upper_bound": float(Q3 + 1.5 * IQR),
                "status": "good" if outlier_count < len(df) * 0.05 else "warning"
            }
        
        # Calculate Overall Score
        completeness_score = quality_report["completeness"]["total_completeness"]
        validity_score = sum(1 for col_validity in quality_report["validity"].values() 
                           if col_validity["status"] == "good") / len(quality_report["validity"]) * 100
        outlier_score = sum(1 for col_outlier in quality_report["outliers"].values() 
                          if col_outlier["status"] == "good") / max(1, len(quality_report["outliers"])) * 100
        
        quality_report["overall_score"] = (completeness_score + validity_score + outlier_score) / 3
        
        # Generate Recommendations
        quality_report["recommendations"] = DataQualityDashboardTool._generate_quality_recommendations(quality_report)
        
        return quality_report
    
    @staticmethod
    def _generate_quality_recommendations(quality_report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations for data quality improvement"""
        recommendations = []
        
        overall_score = quality_report["overall_score"]
        
        if overall_score < 70:
            recommendations.append("Critical: Overall data quality requires immediate attention")
        elif overall_score < 85:
            recommendations.append("Warning: Data quality has room for improvement")
        else:
            recommendations.append("Good: Data quality is acceptable for analysis")
        
        # Completeness recommendations
        poor_completeness_cols = [col for col, data in quality_report["completeness"]["column_completeness"].items() 
                                if data["status"] == "critical"]
        if poor_completeness_cols:
            recommendations.append(f"Address missing data in columns: {', '.join(poor_completeness_cols[:3])}")
        
        # Outlier recommendations
        high_outlier_cols = [col for col, data in quality_report["outliers"].items() 
                           if data["status"] == "warning"]
        if high_outlier_cols:
            recommendations.append(f"Review outliers in: {', '.join(high_outlier_cols[:3])}")
        
        return recommendations
    
    @staticmethod
    def create_quality_charts(df: pd.DataFrame, quality_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create charts for data quality dashboard"""
        charts = []
        
        # Overall Quality Score Gauge
        charts.append({
            "id": "overall_quality_score",
            "type": "gauge_chart",
            "config": {
                "value": quality_report["overall_score"],
                "max_value": 100,
                "title": "Overall Data Quality Score",
                "color": "#059669" if quality_report["overall_score"] > 80 else "#d97706" if quality_report["overall_score"] > 60 else "#dc2626",
                "thresholds": [60, 80, 100],
                "format": "percentage"
            },
            "size": "full_width",
            "priority": "high"
        })
        
        # Missing Data Heatmap
        missing_data = {col: data["missing_count"] for col, data in quality_report["completeness"]["column_completeness"].items()}
        charts.append({
            "id": "missing_data_heatmap",
            "type": "bar_chart",
            "config": {
                "x": list(missing_data.keys()),
                "y": list(missing_data.values()),
                "title": "Missing Data by Column",
                "color": "#dc2626",
                "orientation": "vertical"
            },
            "columns": list(missing_data.keys()),
            "size": "half_width",
            "priority": "high"
        })
        
        # Outlier Analysis
        if quality_report["outliers"]:
            outlier_data = {col: data["outlier_count"] for col, data in quality_report["outliers"].items()}
            charts.append({
                "id": "outlier_analysis",
                "type": "bar_chart",
                "config": {
                    "x": list(outlier_data.keys()),
                    "y": list(outlier_data.values()),
                    "title": "Outlier Count by Column",
                    "color": "#d97706",
                    "orientation": "vertical"
                },
                "columns": list(outlier_data.keys()),
                "size": "half_width",
                "priority": "medium"
            })
        
        return charts


class ExploratoryDashboardTool:
    """Specialized tool for exploratory data analysis dashboards"""
    
    @staticmethod
    def analyze_data_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive pattern analysis for exploratory purposes"""
        patterns = {
            "distributions": {},
            "correlations": {},
            "categorical_analysis": {},
            "statistical_summary": {},
            "insights": []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Distribution Analysis
        for col in numerical_cols:
            skewness = float(df[col].skew())
            kurtosis = float(df[col].kurtosis())
            
            patterns["distributions"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "skewness": skewness,
                "kurtosis": kurtosis,
                "distribution_type": ExploratoryDashboardTool._classify_distribution(skewness, kurtosis),
                "unique_values": int(df[col].nunique())
            }
        
        # Correlation Analysis
        if len(numerical_cols) > 1:
            corr_matrix = df[numerical_cols].corr()
            patterns["correlations"] = {
                "matrix": corr_matrix.to_dict(),
                "strong_correlations": ExploratoryDashboardTool._find_strong_correlations(corr_matrix),
                "correlation_insights": ExploratoryDashboardTool._analyze_correlations(corr_matrix)
            }
        
        # Categorical Analysis
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            patterns["categorical_analysis"][col] = {
                "unique_count": int(df[col].nunique()),
                "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else "N/A",
                "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "distribution_evenness": float(1 - (value_counts.iloc[0] / len(df))),  # 1 = perfectly even, 0 = all same value
                "top_categories": value_counts.head(5).to_dict()
            }
        
        # Generate insights
        patterns["insights"] = ExploratoryDashboardTool._generate_exploratory_insights(patterns, df)
        
        return patterns
    
    @staticmethod
    def _classify_distribution(skewness: float, kurtosis: float) -> str:
        """Classify distribution type based on skewness and kurtosis"""
        if abs(skewness) < 0.5 and abs(kurtosis) < 3:
            return "approximately_normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 3:
            return "heavy_tailed"
        else:
            return "light_tailed"
    
    @staticmethod
    def _find_strong_correlations(corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find strong correlations in the correlation matrix"""
        strong_corrs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) >= threshold:
                    strong_corrs.append({
                        "variable1": col1,
                        "variable2": col2,
                        "correlation": float(corr_value),
                        "strength": "strong_positive" if corr_value >= threshold else "strong_negative",
                        "interpretation": f"{col1} and {col2} are {'positively' if corr_value > 0 else 'negatively'} correlated"
                    })
        
        return strong_corrs
    
    @staticmethod
    def _analyze_correlations(corr_matrix: pd.DataFrame) -> List[str]:
        """Generate insights from correlation analysis"""
        insights = []
        
        # Find the highest correlation
        corr_values = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_values.append(abs(corr_matrix.iloc[i, j]))
        
        if corr_values:
            max_corr = max(corr_values)
            avg_corr = sum(corr_values) / len(corr_values)
            
            insights.append(f"Highest correlation strength: {max_corr:.2f}")
            insights.append(f"Average correlation strength: {avg_corr:.2f}")
            
            if max_corr > 0.8:
                insights.append("Strong correlations detected - potential multicollinearity")
            elif max_corr < 0.3:
                insights.append("Variables show relatively weak correlations")
            else:
                insights.append("Moderate correlations present - good for modeling")
        
        return insights
    
    @staticmethod
    def _generate_exploratory_insights(patterns: Dict[str, Any], df: pd.DataFrame) -> List[str]:
        """Generate insights for exploratory analysis"""
        insights = []
        
        # Dataset overview
        insights.append(f"Dataset contains {len(df)} observations across {len(df.columns)} variables")
        
        # Distribution insights
        normal_distributions = sum(1 for dist in patterns["distributions"].values() 
                                 if dist["distribution_type"] == "approximately_normal")
        if normal_distributions > 0:
            insights.append(f"{normal_distributions} variables show approximately normal distributions")
        
        # Correlation insights
        correlations = patterns.get("correlations") or {}
        if correlations:
            strong_corr_count = len(correlations.get("strong_correlations", []))
            if strong_corr_count > 0:
                insights.append(f"{strong_corr_count} strong correlations identified for further investigation")
        
        # Categorical insights
        if patterns["categorical_analysis"]:
            high_cardinality_cols = [col for col, analysis in patterns["categorical_analysis"].items() 
                                   if analysis["unique_count"] > len(df) * 0.8]
            if high_cardinality_cols:
                insights.append(f"High cardinality detected in: {', '.join(high_cardinality_cols[:2])}")
        
        return insights
    
    @staticmethod
    def create_exploratory_charts(df: pd.DataFrame, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create charts for exploratory analysis dashboard"""
        charts = []
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Correlation Heatmap
        correlations = patterns.get("correlations") or {}
        if correlations and len(numerical_cols) > 1:
            corr_matrix = correlations.get("matrix", {})
            charts.append({
                "id": "correlation_heatmap",
                "type": "heatmap",
                "config": {
                    "z": [list(corr_matrix[col].values()) for col in corr_matrix.keys()] if isinstance(corr_matrix, dict) else [],
                    "x": list(corr_matrix.keys()) if isinstance(corr_matrix, dict) else [],
                    "y": list(corr_matrix.keys()) if isinstance(corr_matrix, dict) else [],
                    "title": "Correlation Matrix",
                    "colorscale": "RdBu",
                    "symmetric": True
                },
                "columns": numerical_cols,
                "size": "half_width",
                "priority": "high"
            })
        
        # Distribution Analysis
        if numerical_cols:
            primary_col = numerical_cols[0]
            charts.append({
                "id": f"distribution_{primary_col}",
                "type": "histogram",
                "config": {
                    "x": df[primary_col].tolist(),
                    "title": f"Distribution of {primary_col.replace('_', ' ').title()}",
                    "color": "#7c3aed",
                    "bins": 30
                },
                "columns": [primary_col],
                "size": "half_width",
                "priority": "high"
            })
        
        # Scatter Plot for relationships
        if len(numerical_cols) >= 2:
            charts.append({
                "id": "scatter_relationship",
                "type": "scatter",
                "config": {
                    "x": df[numerical_cols[0]].tolist(),
                    "y": df[numerical_cols[1]].tolist(),
                    "title": f"{numerical_cols[0]} vs {numerical_cols[1]}",
                    "color": "#059669",
                    "size": 6
                },
                "columns": [numerical_cols[0], numerical_cols[1]],
                "size": "half_width",
                "priority": "medium"
            })
        
        # Categorical Analysis
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = df[cat_col].value_counts().head(10)
            charts.append({
                "id": f"categorical_{cat_col}",
                "type": "bar_chart",
                "config": {
                    "x": value_counts.index.tolist(),
                    "y": value_counts.values.tolist(),
                    "title": f"Distribution of {cat_col.replace('_', ' ').title()}",
                    "color": "#d97706",
                    "orientation": "vertical"
                },
                "columns": [cat_col],
                "size": "half_width",
                "priority": "medium"
            })
        
        return charts


class TimeSeriesDashboardTool:
    """Specialized tool for time series analysis dashboards"""
    
    @staticmethod
    def analyze_time_patterns(df: pd.DataFrame, date_column: str = None) -> Dict[str, Any]:
        """Analyze time series patterns in the data"""
        patterns = {
            "temporal_analysis": {},
            "trends": {},
            "seasonality": {},
            "forecasting_potential": {},
            "insights": []
        }
        
        # Try to identify date columns if not specified
        if date_column is None:
            date_column = TimeSeriesDashboardTool._identify_date_column(df)
        
        if date_column and date_column in df.columns:
            # Convert to datetime if not already
            try:
                df[date_column] = pd.to_datetime(df[date_column])
                
                # Sort by date
                df_sorted = df.sort_values(date_column)
                
                patterns["temporal_analysis"] = {
                    "date_range": {
                        "start": df_sorted[date_column].min().isoformat(),
                        "end": df_sorted[date_column].max().isoformat(),
                        "duration_days": (df_sorted[date_column].max() - df_sorted[date_column].min()).days
                    },
                    "frequency": TimeSeriesDashboardTool._detect_frequency(df_sorted[date_column]),
                    "data_points": len(df_sorted)
                }
                
                # Analyze numerical columns for trends
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                for col in numerical_cols:
                    patterns["trends"][col] = TimeSeriesDashboardTool._analyze_trend(df_sorted, date_column, col)
                
            except Exception as e:
                patterns["insights"].append(f"Date column processing error: {str(e)}")
        else:
            patterns["insights"].append("No suitable date column found for time series analysis")
        
        return patterns
    
    @staticmethod
    def _identify_date_column(df: pd.DataFrame) -> Optional[str]:
        """Try to identify a date column in the dataframe"""
        date_indicators = ['date', 'time', 'timestamp', 'created', 'updated', 'year', 'month']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(indicator in col_lower for indicator in date_indicators):
                try:
                    pd.to_datetime(df[col].head(10))
                    return col
                except:
                    continue
        
        return None
    
    @staticmethod
    def _detect_frequency(date_series: pd.Series) -> str:
        """Detect the frequency of the time series"""
        if len(date_series) < 2:
            return "insufficient_data"
        
        date_diffs = date_series.diff().dropna()
        most_common_diff = date_diffs.mode().iloc[0] if len(date_diffs.mode()) > 0 else date_diffs.median()
        
        if most_common_diff <= timedelta(days=1):
            return "daily_or_higher"
        elif most_common_diff <= timedelta(days=7):
            return "weekly"
        elif most_common_diff <= timedelta(days=31):
            return "monthly"
        else:
            return "quarterly_or_longer"
    
    @staticmethod
    def _analyze_trend(df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """Analyze trend for a specific numerical column"""
        # Simple linear trend analysis
        x = np.arange(len(df))
        y = df[value_col].values
        
        # Calculate trend using least squares
        if len(x) > 1:
            trend_slope = np.polyfit(x, y, 1)[0]
            
            return {
                "slope": float(trend_slope),
                "direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
                "volatility": float(df[value_col].std()),
                "mean_value": float(df[value_col].mean()),
                "min_value": float(df[value_col].min()),
                "max_value": float(df[value_col].max())
            }
        
        return {"slope": 0, "direction": "stable", "volatility": 0, "mean_value": 0}


class CorrelationDashboardTool:
    """Specialized tool for correlation analysis dashboards"""
    
    @staticmethod
    def comprehensive_correlation_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive correlation analysis"""
        analysis = {
            "correlation_matrix": {},
            "correlation_strength_distribution": {},
            "variable_relationships": {},
            "network_analysis": {},
            "insights": []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) < 2:
            analysis["insights"].append("Insufficient numerical variables for correlation analysis")
            return analysis
        
        # Calculate correlation matrix
        corr_matrix = df[numerical_cols].corr()
        analysis["correlation_matrix"] = corr_matrix.to_dict()
        
        # Analyze correlation strength distribution
        corr_values = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_values.append(abs(corr_matrix.iloc[i, j]))
        
        analysis["correlation_strength_distribution"] = {
            "strong_correlations": sum(1 for v in corr_values if v >= 0.7),
            "moderate_correlations": sum(1 for v in corr_values if 0.3 <= v < 0.7),
            "weak_correlations": sum(1 for v in corr_values if v < 0.3),
            "average_correlation": float(np.mean(corr_values)),
            "max_correlation": float(max(corr_values)) if corr_values else 0
        }
        
        # Find most correlated variable pairs
        relationships = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                relationships.append({
                    "variable1": col1,
                    "variable2": col2,
                    "correlation": float(corr_value),
                    "strength": "strong" if abs(corr_value) >= 0.7 else "moderate" if abs(corr_value) >= 0.3 else "weak",
                    "direction": "positive" if corr_value > 0 else "negative"
                })
        
        # Sort by correlation strength
        relationships.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        analysis["variable_relationships"] = relationships[:10]  # Top 10 relationships
        
        # Generate insights
        analysis["insights"] = CorrelationDashboardTool._generate_correlation_insights(analysis)
        
        return analysis
    
    @staticmethod
    def _generate_correlation_insights(analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from correlation analysis"""
        insights = []
        
        dist = analysis["correlation_strength_distribution"]
        relationships = analysis["variable_relationships"]
        
        # Overall correlation landscape
        if dist["strong_correlations"] > 0:
            insights.append(f"Found {dist['strong_correlations']} strong correlations (|r| ≥ 0.7)")
        
        if dist["average_correlation"] > 0.5:
            insights.append("Variables show generally high intercorrelation")
        elif dist["average_correlation"] < 0.2:
            insights.append("Variables are relatively independent")
        else:
            insights.append("Mixed correlation patterns observed")
        
        # Specific relationship insights
        if relationships:
            strongest = relationships[0]
            insights.append(f"Strongest relationship: {strongest['variable1']} ↔ {strongest['variable2']} (r={strongest['correlation']:.3f})")
        
        # Multicollinearity warning
        if dist["strong_correlations"] > 2:
            insights.append("⚠️ High multicollinearity detected - consider for modeling")
        
        return insights


# Factory class to get appropriate tool
class DashboardToolFactory:
    """Factory to get the appropriate dashboard tool based on type"""
    
    @staticmethod
    def get_tool(dashboard_type: str):
        """Get the appropriate tool for the dashboard type"""
        tools = {
            "executive": ExecutiveDashboardTool,
            "data_quality": DataQualityDashboardTool,
            "exploratory": ExploratoryDashboardTool,
            "time_series": TimeSeriesDashboardTool,
            "correlation": CorrelationDashboardTool
        }
        
        return tools.get(dashboard_type, ExploratoryDashboardTool)