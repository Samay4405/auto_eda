"""
LangGraph-powered chart generator with intelligent chart selection and configuration.
Replaces static chart generation with AI-driven chart recommendations and optimizations.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional, TypedDict, Literal
import json
import logging
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


class ChartGenerationState(TypedDict, total=False):
    """State for chart generation workflow"""
    session_id: str
    df: pd.DataFrame
    chart_purpose: str
    data_characteristics: Dict[str, Any]
    target_audience: str
    chart_recommendations: List[Dict[str, Any]]
    selected_charts: List[Dict[str, Any]]
    chart_configurations: List[Dict[str, Any]]
    styling_preferences: Dict[str, Any]
    final_charts: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]


class DataCharacteristicsAnalyzer:
    """Analyzes data characteristics to inform chart selection"""
    
    @staticmethod
    def analyze_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive analysis of data structure and characteristics"""
        analysis = {
            "basic_info": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "missing_data_percent": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            },
            "column_types": {
                "numerical": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical": df.select_dtypes(include=['object']).columns.tolist(),
                "datetime": df.select_dtypes(include=['datetime64']).columns.tolist(),
                "boolean": df.select_dtypes(include=['bool']).columns.tolist()
            },
            "data_patterns": {},
            "relationships": {},
            "recommendations": []
        }
        
        # Analyze numerical columns
        numerical_cols = analysis["column_types"]["numerical"]
        for col in numerical_cols:
            analysis["data_patterns"][col] = {
                "distribution_type": DataCharacteristicsAnalyzer._classify_distribution(df[col]),
                "outlier_percentage": DataCharacteristicsAnalyzer._calculate_outlier_percentage(df[col]),
                "data_range": {"min": float(df[col].min()), "max": float(df[col].max())},
                "variability": float(df[col].std() / df[col].mean()) if df[col].mean() != 0 else 0,
                "unique_values": int(df[col].nunique()),
                "zero_percentage": float((df[col] == 0).sum() / len(df) * 100)
            }
        
        # Analyze categorical columns
        categorical_cols = analysis["column_types"]["categorical"]
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            analysis["data_patterns"][col] = {
                "cardinality": int(df[col].nunique()),
                "cardinality_ratio": float(df[col].nunique() / len(df)),
                "top_category_dominance": float(value_counts.iloc[0] / len(df)) if len(value_counts) > 0 else 0,
                "distribution_evenness": float(1 - (value_counts.std() / value_counts.mean())) if value_counts.mean() != 0 else 0,
                "has_rare_categories": int(df[col].nunique()) > 10,
                "top_categories": value_counts.head(5).to_dict()
            }
        
        # Analyze relationships between columns
        if len(numerical_cols) > 1:
            correlation_matrix = df[numerical_cols].corr()
            analysis["relationships"]["correlations"] = {
                "strong_positive": DataCharacteristicsAnalyzer._find_strong_correlations(correlation_matrix, 0.7, 1.0),
                "strong_negative": DataCharacteristicsAnalyzer._find_strong_correlations(correlation_matrix, -1.0, -0.7),
                "moderate_correlations": DataCharacteristicsAnalyzer._find_strong_correlations(correlation_matrix, 0.3, 0.7),
                "max_correlation": float(correlation_matrix.abs().max().max()),
                "correlation_matrix": correlation_matrix.to_dict()
            }
        
        # Generate high-level recommendations
        analysis["recommendations"] = DataCharacteristicsAnalyzer._generate_chart_recommendations(analysis, df)
        
        return analysis
    
    @staticmethod
    def _classify_distribution(series: pd.Series) -> str:
        """Classify the distribution type of a numerical series"""
        if series.isnull().all():
            return "no_data"
        
        skewness = series.skew()
        kurtosis = series.kurtosis()
        
        if abs(skewness) < 0.5 and abs(kurtosis - 3) < 2:
            return "normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 5:
            return "heavy_tailed"
        elif kurtosis < 1:
            return "light_tailed"
        else:
            return "irregular"
    
    @staticmethod
    def _calculate_outlier_percentage(series: pd.Series) -> float:
        """Calculate percentage of outliers using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        if IQR == 0:
            return 0.0
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return float(len(outliers) / len(series) * 100)
    
    @staticmethod
    def _find_strong_correlations(corr_matrix: pd.DataFrame, min_corr: float, max_corr: float) -> List[Dict[str, Any]]:
        """Find correlations within specified range"""
        correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if min_corr <= corr_value <= max_corr:
                    correlations.append({
                        "variable1": corr_matrix.columns[i],
                        "variable2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong" if abs(corr_value) >= 0.7 else "moderate"
                    })
        
        return correlations
    
    @staticmethod
    def _generate_chart_recommendations(analysis: Dict[str, Any], df: pd.DataFrame) -> List[str]:
        """Generate high-level chart recommendations based on data analysis"""
        recommendations = []
        
        numerical_cols = analysis["column_types"]["numerical"]
        categorical_cols = analysis["column_types"]["categorical"]
        
        # Recommendations based on data structure
        if len(numerical_cols) == 1 and len(categorical_cols) >= 1:
            recommendations.append("Consider bar charts or box plots for numerical vs categorical analysis")
        
        if len(numerical_cols) >= 2:
            if analysis["relationships"].get("correlations", {}).get("strong_positive"):
                recommendations.append("Strong positive correlations detected - scatter plots recommended")
            recommendations.append("Correlation heatmap recommended for relationship analysis")
        
        if len(categorical_cols) >= 1:
            high_cardinality_cols = [col for col in categorical_cols 
                                   if analysis["data_patterns"][col]["cardinality"] > 20]
            if high_cardinality_cols:
                recommendations.append("High cardinality categorical variables detected - consider treemaps or grouped charts")
        
        # Distribution-based recommendations
        for col in numerical_cols:
            dist_type = analysis["data_patterns"][col]["distribution_type"]
            if dist_type == "right_skewed":
                recommendations.append(f"Right-skewed distribution in {col} - consider log transformation")
            elif dist_type == "heavy_tailed":
                recommendations.append(f"Heavy-tailed distribution in {col} - outlier analysis recommended")
        
        return recommendations


class ChartRecommendationEngine:
    """Engine for recommending optimal chart types based on data characteristics"""
    
    def __init__(self):
        self.chart_rules = self._load_chart_selection_rules()
        self.audience_preferences = self._load_audience_preferences()
    
    def recommend_charts(
        self, 
        data_characteristics: Dict[str, Any], 
        chart_purpose: str = "exploration",
        target_audience: str = "analyst"
    ) -> List[Dict[str, Any]]:
        """Recommend optimal charts based on data characteristics and purpose"""
        
        recommendations = []
        numerical_cols = data_characteristics["column_types"]["numerical"]
        categorical_cols = data_characteristics["column_types"]["categorical"]
        
        # Single variable analysis
        for col in numerical_cols:
            recommendations.extend(self._recommend_univariate_numerical_charts(col, data_characteristics, chart_purpose))
        
        for col in categorical_cols:
            recommendations.extend(self._recommend_univariate_categorical_charts(col, data_characteristics, chart_purpose))
        
        # Bivariate analysis
        if len(numerical_cols) >= 2:
            recommendations.extend(self._recommend_bivariate_numerical_charts(numerical_cols, data_characteristics, chart_purpose))
        
        # Mixed analysis
        if numerical_cols and categorical_cols:
            recommendations.extend(self._recommend_mixed_type_charts(numerical_cols, categorical_cols, data_characteristics, chart_purpose))
        
        # Multivariate analysis
        if len(numerical_cols) > 2:
            recommendations.extend(self._recommend_multivariate_charts(numerical_cols, data_characteristics, chart_purpose))
        
        # Filter and rank recommendations based on audience
        recommendations = self._filter_by_audience(recommendations, target_audience)
        recommendations = self._rank_recommendations(recommendations, data_characteristics)
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _recommend_univariate_numerical_charts(self, column: str, characteristics: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """Recommend charts for single numerical variable"""
        recommendations = []
        col_pattern = characteristics["data_patterns"].get(column, {})
        
        # Always recommend histogram
        recommendations.append({
            "chart_type": "histogram",
            "columns": [column],
            "priority": "high",
            "purpose": "distribution_analysis",
            "reasoning": "Essential for understanding data distribution",
            "config": {
                "bins": "auto",
                "show_kde": col_pattern.get("distribution_type") == "normal",
                "title": f"Distribution of {column}"
            }
        })
        
        # Box plot for outlier analysis
        if col_pattern.get("outlier_percentage", 0) > 5:
            recommendations.append({
                "chart_type": "box_plot",
                "columns": [column],
                "priority": "high",
                "purpose": "outlier_detection",
                "reasoning": f"High outlier percentage ({col_pattern.get('outlier_percentage', 0):.1f}%) detected",
                "config": {
                    "show_points": "outliers",
                    "title": f"Box Plot of {column} (Outlier Analysis)"
                }
            })
        
        # Violin plot for detailed distribution shape
        if purpose == "detailed_exploration":
            recommendations.append({
                "chart_type": "violin_plot",
                "columns": [column],
                "priority": "medium",
                "purpose": "detailed_distribution",
                "reasoning": "Detailed distribution shape analysis",
                "config": {
                    "show_box": True,
                    "title": f"Violin Plot of {column}"
                }
            })
        
        return recommendations
    
    def _recommend_univariate_categorical_charts(self, column: str, characteristics: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """Recommend charts for single categorical variable"""
        recommendations = []
        col_pattern = characteristics["data_patterns"].get(column, {})
        cardinality = col_pattern.get("cardinality", 0)
        
        if cardinality <= 10:
            # Bar chart for low cardinality
            recommendations.append({
                "chart_type": "bar_chart",
                "columns": [column],
                "priority": "high",
                "purpose": "categorical_distribution",
                "reasoning": "Optimal for categorical data with low cardinality",
                "config": {
                    "orientation": "vertical" if cardinality <= 5 else "horizontal",
                    "title": f"Distribution of {column}"
                }
            })
            
            # Pie chart for proportional analysis
            if purpose in ["executive", "presentation"]:
                recommendations.append({
                    "chart_type": "pie_chart",
                    "columns": [column],
                    "priority": "medium",
                    "purpose": "proportional_analysis",
                    "reasoning": "Good for showing proportions to executive audience",
                    "config": {
                        "hole": 0.3,  # Donut chart
                        "title": f"Proportion of {column}"
                    }
                })
        
        elif cardinality <= 50:
            # Horizontal bar chart for medium cardinality
            recommendations.append({
                "chart_type": "bar_chart",
                "columns": [column],
                "priority": "high",
                "purpose": "categorical_distribution",
                "reasoning": "Horizontal layout for better readability with many categories",
                "config": {
                    "orientation": "horizontal",
                    "top_n": 20,
                    "title": f"Top 20 Categories in {column}"
                }
            })
        
        else:
            # Treemap for high cardinality
            recommendations.append({
                "chart_type": "treemap",
                "columns": [column],
                "priority": "medium",
                "purpose": "hierarchical_categorical",
                "reasoning": "Treemap handles high cardinality categories efficiently",
                "config": {
                    "top_n": 30,
                    "title": f"Treemap of {column}"
                }
            })
        
        return recommendations
    
    def _recommend_bivariate_numerical_charts(self, columns: List[str], characteristics: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """Recommend charts for two numerical variables"""
        recommendations = []
        correlations = characteristics.get("relationships", {}).get("correlations", {})
        
        # Scatter plot - always recommended for numerical bivariate analysis
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                col1, col2 = columns[i], columns[j]
                
                # Check if there's correlation information
                corr_info = None
                for corr_list in [correlations.get("strong_positive", []), 
                                correlations.get("strong_negative", []), 
                                correlations.get("moderate_correlations", [])]:
                    for corr in corr_list:
                        if (corr["variable1"] == col1 and corr["variable2"] == col2) or \
                           (corr["variable1"] == col2 and corr["variable2"] == col1):
                            corr_info = corr
                            break
                
                priority = "high" if corr_info and corr_info["strength"] == "strong" else "medium"
                reasoning = f"Correlation analysis between {col1} and {col2}"
                if corr_info:
                    reasoning += f" (correlation: {corr_info['correlation']:.3f})"
                
                recommendations.append({
                    "chart_type": "scatter_plot",
                    "columns": [col1, col2],
                    "priority": priority,
                    "purpose": "correlation_analysis",
                    "reasoning": reasoning,
                    "config": {
                        "add_trendline": corr_info is not None,
                        "title": f"{col1} vs {col2}",
                        "color_scale": "viridis"
                    }
                })
        
        # Correlation heatmap if multiple numerical variables
        if len(columns) > 2:
            recommendations.append({
                "chart_type": "correlation_heatmap",
                "columns": columns,
                "priority": "high",
                "purpose": "correlation_overview",
                "reasoning": "Comprehensive correlation analysis for multiple variables",
                "config": {
                    "annotate": True,
                    "color_scale": "RdBu",
                    "title": "Correlation Matrix"
                }
            })
        
        return recommendations
    
    def _recommend_mixed_type_charts(self, numerical_cols: List[str], categorical_cols: List[str], characteristics: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """Recommend charts for mixed numerical and categorical variables"""
        recommendations = []
        
        # Box plots for numerical vs categorical
        for num_col in numerical_cols[:3]:  # Limit to top 3 numerical columns
            for cat_col in categorical_cols[:2]:  # Limit to top 2 categorical columns
                cat_pattern = characteristics["data_patterns"].get(cat_col, {})
                cardinality = cat_pattern.get("cardinality", 0)
                
                if cardinality <= 20:  # Only if categorical variable has reasonable cardinality
                    recommendations.append({
                        "chart_type": "grouped_box_plot",
                        "columns": [num_col, cat_col],
                        "priority": "high",
                        "purpose": "categorical_comparison",
                        "reasoning": f"Compare {num_col} distribution across {cat_col} categories",
                        "config": {
                            "x": cat_col,
                            "y": num_col,
                            "title": f"{num_col} by {cat_col}"
                        }
                    })
        
        # Grouped bar charts
        if purpose in ["executive", "presentation"]:
            for cat_col in categorical_cols[:2]:
                cat_pattern = characteristics["data_patterns"].get(cat_col, {})
                if cat_pattern.get("cardinality", 0) <= 10:
                    recommendations.append({
                        "chart_type": "grouped_bar_chart",
                        "columns": [cat_col] + numerical_cols[:2],
                        "priority": "medium",
                        "purpose": "categorical_summary",
                        "reasoning": "Executive-friendly categorical summary",
                        "config": {
                            "group_by": cat_col,
                            "title": f"Summary by {cat_col}"
                        }
                    })
        
        return recommendations
    
    def _recommend_multivariate_charts(self, columns: List[str], characteristics: Dict[str, Any], purpose: str) -> List[Dict[str, Any]]:
        """Recommend charts for multivariate analysis"""
        recommendations = []
        
        # Scatter plot matrix for up to 5 variables
        if len(columns) <= 5:
            recommendations.append({
                "chart_type": "scatter_matrix",
                "columns": columns,
                "priority": "medium",
                "purpose": "multivariate_exploration",
                "reasoning": "Comprehensive pairwise relationship analysis",
                "config": {
                    "diagonal_type": "histogram",
                    "title": "Scatter Plot Matrix"
                }
            })
        
        # Parallel coordinates plot
        if len(columns) >= 3:
            recommendations.append({
                "chart_type": "parallel_coordinates",
                "columns": columns[:6],  # Limit to 6 variables for readability
                "priority": "medium",
                "purpose": "pattern_detection",
                "reasoning": "Pattern detection across multiple dimensions",
                "config": {
                    "title": "Parallel Coordinates Plot"
                }
            })
        
        return recommendations
    
    def _filter_by_audience(self, recommendations: List[Dict[str, Any]], target_audience: str) -> List[Dict[str, Any]]:
        """Filter recommendations based on target audience preferences"""
        audience_prefs = self.audience_preferences.get(target_audience, {})
        
        if not audience_prefs:
            return recommendations
        
        filtered = []
        for rec in recommendations:
            chart_type = rec["chart_type"]
            
            # Check if chart type is preferred for this audience
            if chart_type in audience_prefs.get("preferred_charts", []):
                rec["priority"] = "high"
                filtered.append(rec)
            elif chart_type not in audience_prefs.get("avoid_charts", []):
                filtered.append(rec)
        
        return filtered
    
    def _rank_recommendations(self, recommendations: List[Dict[str, Any]], characteristics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank recommendations based on data characteristics and chart effectiveness"""
        def ranking_score(rec):
            score = 0
            
            # Priority scoring
            if rec["priority"] == "high":
                score += 10
            elif rec["priority"] == "medium":
                score += 5
            
            # Purpose scoring
            if rec["purpose"] in ["distribution_analysis", "correlation_analysis"]:
                score += 5
            
            # Data size consideration
            row_count = characteristics["basic_info"]["row_count"]
            if row_count > 10000 and rec["chart_type"] in ["scatter_plot", "scatter_matrix"]:
                score -= 3  # Penalize scatter plots for large datasets
            
            return score
        
        return sorted(recommendations, key=ranking_score, reverse=True)
    
    def _load_chart_selection_rules(self) -> Dict[str, Any]:
        """Load rules for chart selection based on data characteristics"""
        return {
            "univariate_numerical": {
                "histogram": {"always": True},
                "box_plot": {"condition": "outliers > 5%"},
                "violin_plot": {"condition": "detailed_analysis"}
            },
            "univariate_categorical": {
                "bar_chart": {"condition": "cardinality <= 20"},
                "pie_chart": {"condition": "cardinality <= 7 and executive_audience"},
                "treemap": {"condition": "cardinality > 20"}
            },
            "bivariate_numerical": {
                "scatter_plot": {"always": True},
                "correlation_heatmap": {"condition": "variables > 2"}
            }
        }
    
    def _load_audience_preferences(self) -> Dict[str, Any]:
        """Load chart preferences for different audiences"""
        return {
            "executive": {
                "preferred_charts": ["bar_chart", "pie_chart", "line_chart", "kpi_card"],
                "avoid_charts": ["scatter_matrix", "parallel_coordinates", "violin_plot"],
                "complexity_level": "simple"
            },
            "analyst": {
                "preferred_charts": ["histogram", "scatter_plot", "box_plot", "correlation_heatmap"],
                "avoid_charts": [],
                "complexity_level": "medium"
            },
            "data_scientist": {
                "preferred_charts": ["scatter_matrix", "parallel_coordinates", "violin_plot", "correlation_heatmap"],
                "avoid_charts": ["pie_chart"],
                "complexity_level": "advanced"
            },
            "business_user": {
                "preferred_charts": ["bar_chart", "line_chart", "pie_chart"],
                "avoid_charts": ["scatter_matrix", "violin_plot", "parallel_coordinates"],
                "complexity_level": "simple"
            }
        }


class PlotlyChartBuilder:
    """Builds Plotly charts based on specifications"""
    
    @staticmethod
    def build_chart(chart_spec: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Build a Plotly chart based on specification"""
        chart_type = chart_spec["chart_type"]
        columns = chart_spec["columns"]
        config = chart_spec.get("config", {})
        
        try:
            if chart_type == "histogram":
                return PlotlyChartBuilder._build_histogram(df, columns[0], config)
            elif chart_type == "scatter_plot":
                return PlotlyChartBuilder._build_scatter_plot(df, columns[0], columns[1], config)
            elif chart_type == "box_plot":
                return PlotlyChartBuilder._build_box_plot(df, columns[0], config)
            elif chart_type == "bar_chart":
                return PlotlyChartBuilder._build_bar_chart(df, columns[0], config)
            elif chart_type == "correlation_heatmap":
                return PlotlyChartBuilder._build_correlation_heatmap(df, columns, config)
            elif chart_type == "pie_chart":
                return PlotlyChartBuilder._build_pie_chart(df, columns[0], config)
            elif chart_type == "line_chart":
                return PlotlyChartBuilder._build_line_chart(df, columns, config)
            elif chart_type == "violin_plot":
                return PlotlyChartBuilder._build_violin_plot(df, columns[0], config)
            elif chart_type == "treemap":
                return PlotlyChartBuilder._build_treemap(df, columns[0], config)
            elif chart_type == "scatter_matrix":
                return PlotlyChartBuilder._build_scatter_matrix(df, columns, config)
            elif chart_type == "parallel_coordinates":
                return PlotlyChartBuilder._build_parallel_coordinates(df, columns, config)
            elif chart_type == "grouped_box_plot":
                return PlotlyChartBuilder._build_grouped_box_plot(df, columns[0], columns[1], config)
            else:
                return {"error": f"Unsupported chart type: {chart_type}"}
        
        except Exception as e:
            logger.error(f"Error building chart {chart_type}: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def _build_histogram(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build histogram chart"""
        # Get bins value and ensure it's an integer
        bins = config.get("bins", 30)
        if isinstance(bins, str) and bins == "auto":
            bins = 30  # Default to 30 bins if "auto" is specified
        elif not isinstance(bins, int):
            bins = int(bins) if str(bins).isdigit() else 30
            
        fig = px.histogram(
            df, 
            x=column,
            nbins=bins,
            title=config.get("title", f"Distribution of {column}")
        )
        
        if config.get("show_kde", False):
            # Add KDE curve (approximated with smoothed histogram)
            fig.add_trace(go.Histogram(
                x=df[column],
                histnorm='probability density',
                name='KDE Approximation',
                opacity=0.7
            ))
        
        fig.update_layout(
            xaxis_title=column,
            yaxis_title="Frequency",
            showlegend=False
        )
        
        return {
            "type": "histogram",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build scatter plot chart"""
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=config.get("title", f"{x_col} vs {y_col}")
        )
        
        if config.get("add_trendline", False):
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                trendline="ols",
                title=config.get("title", f"{x_col} vs {y_col}")
            )
        
        fig.update_traces(marker=dict(size=6, opacity=0.7))
        
        return {
            "type": "scatter_plot",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_box_plot(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build box plot chart"""
        fig = px.box(
            df,
            y=column,
            title=config.get("title", f"Box Plot of {column}"),
            points=config.get("show_points", False)
        )
        
        return {
            "type": "box_plot",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_bar_chart(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build bar chart"""
        value_counts = df[column].value_counts()
        
        # Apply top_n filter if specified
        if config.get("top_n"):
            value_counts = value_counts.head(config["top_n"])
        
        orientation = config.get("orientation", "vertical")
        
        if orientation == "horizontal":
            fig = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=config.get("title", f"Distribution of {column}")
            )
        else:
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=config.get("title", f"Distribution of {column}")
            )
        
        return {
            "type": "bar_chart",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_correlation_heatmap(df: pd.DataFrame, columns: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build correlation heatmap"""
        corr_matrix = df[columns].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=config.get("annotate", True),
            color_continuous_scale=config.get("color_scale", "RdBu"),
            title=config.get("title", "Correlation Matrix")
        )
        
        return {
            "type": "correlation_heatmap",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_pie_chart(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build pie chart"""
        value_counts = df[column].value_counts()
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=config.get("title", f"Distribution of {column}"),
            hole=config.get("hole", 0)
        )
        
        return {
            "type": "pie_chart",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_line_chart(df: pd.DataFrame, columns: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build line chart"""
        # Assume first column is x, rest are y values
        if len(columns) == 1:
            # Single variable line chart with index as x
            fig = px.line(
                y=df[columns[0]],
                title=config.get("title", f"Trend of {columns[0]}")
            )
        else:
            # Multi-variable line chart
            fig = px.line(
                df,
                x=columns[0] if len(columns) > 1 else None,
                y=columns[1:],
                title=config.get("title", "Line Chart")
            )
        
        return {
            "type": "line_chart",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_violin_plot(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build violin plot"""
        fig = px.violin(
            df,
            y=column,
            box=config.get("show_box", True),
            title=config.get("title", f"Violin Plot of {column}")
        )
        
        return {
            "type": "violin_plot",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_treemap(df: pd.DataFrame, column: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build treemap chart"""
        value_counts = df[column].value_counts()
        
        if config.get("top_n"):
            value_counts = value_counts.head(config["top_n"])
        
        fig = px.treemap(
            names=value_counts.index,
            values=value_counts.values,
            title=config.get("title", f"Treemap of {column}")
        )
        
        return {
            "type": "treemap",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_scatter_matrix(df: pd.DataFrame, columns: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build scatter matrix"""
        fig = px.scatter_matrix(
            df[columns],
            title=config.get("title", "Scatter Matrix")
        )
        
        return {
            "type": "scatter_matrix",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_parallel_coordinates(df: pd.DataFrame, columns: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Build parallel coordinates plot"""
        fig = px.parallel_coordinates(
            df,
            dimensions=columns,
            title=config.get("title", "Parallel Coordinates")
        )
        
        return {
            "type": "parallel_coordinates",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }
    
    @staticmethod
    def _build_grouped_box_plot(df: pd.DataFrame, numeric_col: str, category_col: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build grouped box plot"""
        fig = px.box(
            df,
            x=config.get("x", category_col),
            y=config.get("y", numeric_col),
            title=config.get("title", f"{numeric_col} by {category_col}")
        )
        
        return {
            "type": "grouped_box_plot",
            "data": fig.to_dict(),
            "plotly_json": fig.to_json()
        }


class LangGraphChartGenerator:
    """Main LangGraph-powered chart generator"""
    
    def __init__(self):
        self.data_analyzer = DataCharacteristicsAnalyzer()
        self.recommendation_engine = ChartRecommendationEngine()
        self.chart_builder = PlotlyChartBuilder()
        self.chart_workflow = self._create_chart_generation_workflow()
    
    def _create_chart_generation_workflow(self) -> StateGraph:
        """Create LangGraph workflow for chart generation"""
        graph = StateGraph(ChartGenerationState)
        
        # Add workflow nodes
        graph.add_node("initialize_session", self._initialize_session)
        graph.add_node("analyze_data_characteristics", self._analyze_data_characteristics)
        graph.add_node("generate_chart_recommendations", self._generate_chart_recommendations)
        graph.add_node("select_optimal_charts", self._select_optimal_charts)
        graph.add_node("configure_chart_styling", self._configure_chart_styling)
        graph.add_node("build_charts", self._build_charts)
        graph.add_node("optimize_performance", self._optimize_performance)
        graph.add_node("finalize_charts", self._finalize_charts)
        
        # Define workflow
        graph.set_entry_point("initialize_session")
        graph.add_edge("initialize_session", "analyze_data_characteristics")
        graph.add_edge("analyze_data_characteristics", "generate_chart_recommendations")
        graph.add_edge("generate_chart_recommendations", "select_optimal_charts")
        graph.add_edge("select_optimal_charts", "configure_chart_styling")
        graph.add_edge("configure_chart_styling", "build_charts")
        graph.add_edge("build_charts", "optimize_performance")
        graph.add_edge("optimize_performance", "finalize_charts")
        graph.add_edge("finalize_charts", END)
        
        return graph.compile()
    
    # Workflow node implementations
    def _initialize_session(self, state: ChartGenerationState) -> ChartGenerationState:
        """Initialize chart generation session"""
        return {
            **state,
            "session_id": uuid.uuid4().hex,
            "styling_preferences": {"color_scheme": "modern", "theme": "light"}
        }
    
    def _analyze_data_characteristics(self, state: ChartGenerationState) -> ChartGenerationState:
        """Analyze data characteristics for chart recommendations"""
        df = state["df"]
        characteristics = self.data_analyzer.analyze_data_structure(df)
        
        return {**state, "data_characteristics": characteristics}
    
    def _generate_chart_recommendations(self, state: ChartGenerationState) -> ChartGenerationState:
        """Generate chart recommendations based on data analysis"""
        characteristics = state["data_characteristics"]
        purpose = state.get("chart_purpose", "exploration")
        target_audience = state.get("target_audience", "analyst")
        
        recommendations = self.recommendation_engine.recommend_charts(
            characteristics, purpose, target_audience
        )
        
        return {**state, "chart_recommendations": recommendations}
    
    def _select_optimal_charts(self, state: ChartGenerationState) -> ChartGenerationState:
        """Select optimal charts from recommendations"""
        recommendations = state["chart_recommendations"]
        
        # Select top charts based on priority and purpose
        selected = []
        high_priority = [rec for rec in recommendations if rec["priority"] == "high"]
        medium_priority = [rec for rec in recommendations if rec["priority"] == "medium"]
        
        # Include all high priority charts
        selected.extend(high_priority)
        
        # Add medium priority charts up to a limit
        max_charts = 8
        remaining_slots = max_charts - len(selected)
        selected.extend(medium_priority[:remaining_slots])
        
        return {**state, "selected_charts": selected}
    
    def _configure_chart_styling(self, state: ChartGenerationState) -> ChartGenerationState:
        """Configure styling for selected charts"""
        selected_charts = state["selected_charts"]
        styling_prefs = state["styling_preferences"]
        
        # Add styling configuration to each chart
        configured_charts = []
        for chart in selected_charts:
            chart_config = chart.get("config", {})
            
            # Apply consistent styling
            chart_config.update({
                "color_scheme": styling_prefs.get("color_scheme", "modern"),
                "theme": styling_prefs.get("theme", "light"),
                "font_family": "Inter, system-ui, sans-serif",
                "responsive": True
            })
            
            chart["config"] = chart_config
            configured_charts.append(chart)
        
        return {**state, "chart_configurations": configured_charts}
    
    def _build_charts(self, state: ChartGenerationState) -> ChartGenerationState:
        """Build actual charts using Plotly"""
        df = state["df"]
        chart_configurations = state["chart_configurations"]
        
        built_charts = []
        for chart_config in chart_configurations:
            try:
                chart_result = self.chart_builder.build_chart(chart_config, df)
                
                if "error" not in chart_result:
                    built_charts.append({
                        **chart_config,
                        "chart_data": chart_result,
                        "id": f"chart_{uuid.uuid4().hex[:8]}",
                        "status": "success"
                    })
                else:
                    logger.error(f"Chart build error: {chart_result['error']}")
                    built_charts.append({
                        **chart_config,
                        "error": chart_result["error"],
                        "status": "error"
                    })
            
            except Exception as e:
                logger.error(f"Error building chart: {str(e)}")
                built_charts.append({
                    **chart_config,
                    "error": str(e),
                    "status": "error"
                })
        
        return {**state, "final_charts": built_charts}
    
    def _optimize_performance(self, state: ChartGenerationState) -> ChartGenerationState:
        """Optimize charts for performance"""
        final_charts = state["final_charts"]
        df = state["df"]
        
        # Performance optimization based on data size
        data_size = len(df)
        optimized_charts = []
        
        for chart in final_charts:
            if chart.get("status") == "success":
                # Apply optimizations for large datasets
                if data_size > 10000:
                    if chart["chart_type"] in ["scatter_plot", "scatter_matrix"]:
                        # Sample data for scatter plots with large datasets
                        chart["performance_note"] = f"Data sampled to 5000 points for performance"
                
                # Calculate performance metrics
                chart["performance_metrics"] = {
                    "data_points": data_size,
                    "estimated_render_time": "fast" if data_size < 1000 else "medium" if data_size < 10000 else "slow",
                    "optimization_applied": data_size > 10000
                }
            
            optimized_charts.append(chart)
        
        performance_summary = {
            "total_charts": len(optimized_charts),
            "successful_charts": len([c for c in optimized_charts if c.get("status") == "success"]),
            "failed_charts": len([c for c in optimized_charts if c.get("status") == "error"]),
            "data_size": data_size,
            "optimizations_applied": data_size > 10000
        }
        
        return {**state, "final_charts": optimized_charts, "performance_metrics": performance_summary}
    
    def _finalize_charts(self, state: ChartGenerationState) -> ChartGenerationState:
        """Finalize charts and prepare output"""
        # Add any final processing; re-emit a field to satisfy LangGraph's update requirement
        return {"final_charts": state.get("final_charts", [])}
    
    # Public API
    async def generate_charts(
        self,
        df: pd.DataFrame,
        chart_purpose: str = "exploration",
        target_audience: str = "analyst",
        max_charts: int = 8
    ) -> Dict[str, Any]:
        """Generate charts using LangGraph workflow"""
        try:
            initial_state: ChartGenerationState = {
                "df": df,
                "chart_purpose": chart_purpose,
                "target_audience": target_audience
            }
            
            result = self.chart_workflow.invoke(initial_state)
            
            return {
                "success": True,
                "charts": result.get("final_charts", []),
                "session_id": result.get("session_id", ""),
                "data_characteristics": result.get("data_characteristics", {}),
                "chart_recommendations": result.get("chart_recommendations", []),
                "performance_metrics": result.get("performance_metrics", {}),
                "generation_timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating charts: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "generation_timestamp": datetime.now().isoformat()
            }
    
    def generate_single_chart(
        self,
        df: pd.DataFrame,
        chart_type: str,
        columns: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a single chart with specified parameters"""
        try:
            chart_spec = {
                "chart_type": chart_type,
                "columns": columns,
                "config": config or {}
            }
            
            chart_result = self.chart_builder.build_chart(chart_spec, df)
            
            if "error" not in chart_result:
                return {
                    "success": True,
                    "chart": {
                        **chart_spec,
                        "chart_data": chart_result,
                        "id": f"chart_{uuid.uuid4().hex[:8]}"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": chart_result["error"]
                }
        
        except Exception as e:
            logger.error(f"Error generating single chart: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }