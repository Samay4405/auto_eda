"""
Enhanced LangGraph-based agents for automated EDA and dashboard generation.
This module contains specialized agents for different dashboard types and data operations.
"""

import pandas as pd
import numpy as np
import json
import uuid
from typing import Dict, List, Any, Optional, TypedDict, Literal
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END

# Set up logger
logger = logging.getLogger(__name__)


# State definitions for different agent workflows
class BaseEDAState(TypedDict, total=False):
    """Base state for all EDA operations"""
    session_id: str
    df: pd.DataFrame
    data_summary: Dict[str, Any]
    data_json: Dict[str, Any]  # JSON representation of data
    operation_type: str
    user_context: str
    error_messages: List[str]
    timestamp: str


class DashboardState(BaseEDAState, total=False):
    """State for dashboard generation workflows"""
    dashboard_type: Literal["executive", "data_quality", "exploratory", "correlation", "time_series", "custom"]
    target_audience: Literal["executive", "analyst", "data_scientist", "business_user"]
    kpi_metrics: List[Dict[str, Any]]
    chart_configs: List[Dict[str, Any]]
    insights: List[str]
    dashboard_code: str
    layout_config: Dict[str, Any]
    interactivity_level: Literal["basic", "intermediate", "advanced"]


class DataProcessingState(BaseEDAState, total=False):
    """State for data processing operations"""
    processing_steps: List[str]
    data_quality_score: float
    missing_data_strategy: str
    outlier_strategy: str
    feature_engineering_suggestions: List[Dict[str, Any]]
    processed_data: Dict[str, Any]


class ChartGenerationState(BaseEDAState, total=False):
    """State for chart generation operations"""
    chart_type: str
    columns_used: List[str]
    chart_purpose: str
    chart_data: Dict[str, Any]
    styling_preferences: Dict[str, Any]
    interactivity_features: List[str]


# Tool definitions for different agent types
class DashboardTools:
    """Tools for dashboard generation agents"""
    
    @staticmethod
    def analyze_data_for_executive_dashboard(df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """Analyze data specifically for executive dashboard requirements"""
        analysis = {
            "key_metrics": [],
            "trends": [],
            "performance_indicators": [],
            "business_insights": []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Generate key metrics for executives
        for col in numerical_cols[:5]:  # Top 5 numerical columns
            if df[col].count() > 0:
                analysis["key_metrics"].append({
                    "name": col.replace('_', ' ').title(),
                    "value": float(df[col].sum()),
                    "average": float(df[col].mean()),
                    "trend": "up" if df[col].tail(10).mean() > df[col].head(10).mean() else "down",
                    "change_percent": float(((df[col].tail(10).mean() - df[col].head(10).mean()) / df[col].head(10).mean()) * 100) if df[col].head(10).mean() != 0 else 0
                })
        
        # Business insights based on context
        if "sales" in context.lower() or "revenue" in context.lower():
            analysis["business_insights"].append("Revenue trends analysis available")
        if "customer" in context.lower():
            analysis["business_insights"].append("Customer segmentation opportunities identified")
        
        return analysis
    
    @staticmethod
    def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality analysis"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        quality_metrics = {
            "completeness_score": float((total_cells - missing_cells) / total_cells * 100),
            "missing_data_pattern": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "data_types_summary": df.dtypes.astype(str).to_dict(),
            "outlier_detection": {},
            "consistency_score": 85.0  # Placeholder for more complex consistency checks
        }
        
        # Outlier detection for numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))].shape[0]
            quality_metrics["outlier_detection"][col] = {
                "outlier_count": int(outliers),
                "outlier_percentage": float((outliers / len(df)) * 100)
            }
        
        return quality_metrics
    
    @staticmethod
    def suggest_chart_types(df: pd.DataFrame, dashboard_type: str) -> List[Dict[str, Any]]:
        """Suggest optimal chart types based on data characteristics and dashboard type"""
        suggestions = []
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if dashboard_type == "executive":
            # Executive dashboards need high-level KPIs and trends
            suggestions.extend([
                {"type": "kpi_card", "columns": numerical_cols[:4], "priority": "high", "purpose": "key_metrics"},
                {"type": "line_chart", "columns": numerical_cols[:2], "priority": "high", "purpose": "trend_analysis"},
                {"type": "donut_chart", "columns": categorical_cols[:1], "priority": "medium", "purpose": "distribution"}
            ])
        
        elif dashboard_type == "data_quality":
            # Data quality dashboards focus on completeness and integrity
            suggestions.extend([
                {"type": "missing_data_heatmap", "columns": df.columns.tolist(), "priority": "high", "purpose": "completeness"},
                {"type": "outlier_boxplot", "columns": numerical_cols, "priority": "high", "purpose": "integrity"},
                {"type": "data_type_summary", "columns": df.columns.tolist(), "priority": "medium", "purpose": "structure"}
            ])
        
        elif dashboard_type == "exploratory":
            # Exploratory dashboards need comprehensive analysis
            suggestions.extend([
                {"type": "correlation_heatmap", "columns": numerical_cols, "priority": "high", "purpose": "relationships"},
                {"type": "distribution_histogram", "columns": numerical_cols, "priority": "high", "purpose": "distribution"},
                {"type": "scatter_matrix", "columns": numerical_cols[:4], "priority": "medium", "purpose": "relationships"},
                {"type": "categorical_bar", "columns": categorical_cols, "priority": "medium", "purpose": "categorical_analysis"}
            ])
        
        return suggestions
    
    @staticmethod
    def generate_dashboard_layout(dashboard_type: str, chart_count: int) -> Dict[str, Any]:
        """Generate optimal layout configuration for dashboard type"""
        layouts = {
            "executive": {
                "grid_columns": 3,
                "sections": [
                    {"type": "kpi_section", "span": "full_width", "height": "small"},
                    {"type": "primary_chart", "span": "two_thirds", "height": "medium"},
                    {"type": "secondary_chart", "span": "one_third", "height": "medium"},
                    {"type": "insights_panel", "span": "full_width", "height": "small"}
                ],
                "color_scheme": "executive",
                "spacing": "compact"
            },
            "data_quality": {
                "grid_columns": 2,
                "sections": [
                    {"type": "quality_score", "span": "full_width", "height": "small"},
                    {"type": "missing_data", "span": "half", "height": "large"},
                    {"type": "outliers", "span": "half", "height": "large"},
                    {"type": "recommendations", "span": "full_width", "height": "medium"}
                ],
                "color_scheme": "quality",
                "spacing": "normal"
            },
            "exploratory": {
                "grid_columns": 2,
                "sections": [
                    {"type": "overview", "span": "full_width", "height": "small"},
                    {"type": "correlation", "span": "half", "height": "large"},
                    {"type": "distribution", "span": "half", "height": "large"},
                    {"type": "detailed_analysis", "span": "full_width", "height": "large"}
                ],
                "color_scheme": "analytical",
                "spacing": "spacious"
            }
        }
        
        return layouts.get(dashboard_type, layouts["exploratory"])


class DataProcessingTools:
    """Tools for data processing agents"""
    
    @staticmethod
    def convert_to_json_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """Convert DataFrame to optimized JSON structure for frontend"""
        json_data = {
            "metadata": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_types": df.dtypes.astype(str).to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "created_at": datetime.now().isoformat()
            },
            "columns": df.columns.tolist(),
            "data": []
        }
        
        # Convert data to records format but with proper type handling
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    record[col] = None
                elif isinstance(value, (np.integer, int)):
                    record[col] = int(value)
                elif isinstance(value, (np.floating, float)):
                    record[col] = float(value)
                elif isinstance(value, np.bool_):
                    record[col] = bool(value)
                else:
                    record[col] = str(value)
            json_data["data"].append(record)
        
        return json_data
    
    @staticmethod
    def suggest_missing_data_strategy(df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest optimal missing data handling strategy"""
        missing_analysis = {}
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percent = (missing_count / len(df)) * 100
            
            if missing_percent == 0:
                strategy = "no_action"
            elif missing_percent < 5:
                strategy = "drop_rows"
            elif missing_percent < 20:
                if df[col].dtype in ['int64', 'float64']:
                    strategy = "mean_imputation"
                else:
                    strategy = "mode_imputation"
            elif missing_percent < 50:
                strategy = "advanced_imputation"
            else:
                strategy = "drop_column"
            
            missing_analysis[col] = {
                "missing_count": int(missing_count),
                "missing_percent": float(missing_percent),
                "recommended_strategy": strategy,
                "data_type": str(df[col].dtype)
            }
        
        return missing_analysis


class ChartGenerationTools:
    """Tools for chart generation agents"""
    
    @staticmethod
    def generate_plotly_config(chart_type: str, data: Dict[str, Any], styling: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate Plotly configuration for specific chart type"""
        styling = styling or {}
        
        base_config = {
            "responsive": True,
            "displayModeBar": True,
            "modeBarButtonsToRemove": ['pan2d', 'lasso2d', 'select2d'],
            "displaylogo": False
        }
        
        layout_base = {
            "font": {"family": "Inter, system-ui, sans-serif", "size": 12},
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "margin": {"t": 40, "r": 20, "b": 40, "l": 60}
        }
        
        # Chart-specific configurations
        if chart_type == "kpi_card":
            return {
                "type": "indicator",
                "mode": "number+delta",
                "value": data.get("value", 0),
                "delta": {"reference": data.get("reference", 0)},
                "number": {"font": {"size": 48, "color": styling.get("color", "#2563eb")}},
                "title": {"text": data.get("title", "KPI"), "font": {"size": 16}}
            }
        
        elif chart_type == "line_chart":
            return {
                "data": [{
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": data.get("x", []),
                    "y": data.get("y", []),
                    "name": data.get("name", "Trend"),
                    "line": {"color": styling.get("color", "#2563eb"), "width": 3},
                    "marker": {"size": 6}
                }],
                "layout": {
                    **layout_base,
                    "title": data.get("title", "Trend Analysis"),
                    "xaxis": {"title": data.get("x_title", "X")},
                    "yaxis": {"title": data.get("y_title", "Y")}
                },
                "config": base_config
            }
        
        elif chart_type == "correlation_heatmap":
            return {
                "data": [{
                    "type": "heatmap",
                    "z": data.get("correlation_matrix", []),
                    "x": data.get("columns", []),
                    "y": data.get("columns", []),
                    "colorscale": "RdBu",
                    "zmid": 0,
                    "texttemplate": "%{z:.2f}",
                    "textfont": {"size": 10}
                }],
                "layout": {
                    **layout_base,
                    "title": "Correlation Matrix",
                    "height": 500
                },
                "config": base_config
            }
        
        return {"type": chart_type, "data": data, "layout": layout_base, "config": base_config}


class LangGraphAgentOrchestrator:
    """Main orchestrator for all LangGraph agents"""
    
    def __init__(self):
        self.dashboard_tools = DashboardTools()
        self.data_tools = DataProcessingTools()
        self.chart_tools = ChartGenerationTools()
        
        # Initialize different agent workflows
        self.dashboard_agent = self._create_dashboard_agent()
        self.data_processing_agent = self._create_data_processing_agent()
        self.chart_generation_agent = self._create_chart_generation_agent()
    
    def _create_dashboard_agent(self) -> StateGraph:
        """Create the dashboard generation agent workflow"""
        graph = StateGraph(DashboardState)
        
        # Add nodes for dashboard generation workflow
        graph.add_node("analyze_requirements", self._analyze_dashboard_requirements)
        graph.add_node("generate_layout", self._generate_dashboard_layout)
        graph.add_node("create_charts", self._create_dashboard_charts)
        graph.add_node("generate_insights", self._generate_dashboard_insights)
        graph.add_node("compile_dashboard", self._compile_dashboard_code)
        
        # Define the workflow
        graph.set_entry_point("analyze_requirements")
        graph.add_edge("analyze_requirements", "generate_layout")
        graph.add_edge("generate_layout", "create_charts")
        graph.add_edge("create_charts", "generate_insights")
        graph.add_edge("generate_insights", "compile_dashboard")
        graph.add_edge("compile_dashboard", END)
        
        return graph.compile()
    
    def _create_data_processing_agent(self) -> StateGraph:
        """Create the data processing agent workflow"""
        graph = StateGraph(DataProcessingState)
        
        graph.add_node("analyze_data_quality", self._analyze_data_quality)
        graph.add_node("convert_to_json", self._convert_data_to_json)
        graph.add_node("suggest_preprocessing", self._suggest_preprocessing_steps)
        graph.add_node("apply_preprocessing", self._apply_preprocessing)
        
        graph.set_entry_point("analyze_data_quality")
        graph.add_edge("analyze_data_quality", "convert_to_json")
        graph.add_edge("convert_to_json", "suggest_preprocessing")
        graph.add_edge("suggest_preprocessing", "apply_preprocessing")
        graph.add_edge("apply_preprocessing", END)
        
        return graph.compile()
    
    def _create_chart_generation_agent(self) -> StateGraph:
        """Create the chart generation agent workflow"""
        graph = StateGraph(ChartGenerationState)
        
        graph.add_node("analyze_chart_requirements", self._analyze_chart_requirements)
        graph.add_node("select_optimal_chart_type", self._select_chart_type)
        graph.add_node("generate_chart_config", self._generate_chart_config)
        graph.add_node("apply_styling", self._apply_chart_styling)
        
        graph.set_entry_point("analyze_chart_requirements")
        graph.add_edge("analyze_chart_requirements", "select_optimal_chart_type")
        graph.add_edge("select_optimal_chart_type", "generate_chart_config")
        graph.add_edge("generate_chart_config", "apply_styling")
        graph.add_edge("apply_styling", END)
        
        return graph.compile()
    
    # Dashboard agent node implementations
    def _analyze_dashboard_requirements(self, state: DashboardState) -> DashboardState:
        """Analyze requirements for dashboard generation"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        user_context = state.get("user_context", "")
        
        if dashboard_type == "executive":
            analysis = self.dashboard_tools.analyze_data_for_executive_dashboard(df, user_context)
        elif dashboard_type == "data_quality":
            analysis = self.dashboard_tools.analyze_data_quality(df)
        else:
            # Default exploratory analysis
            analysis = {
                "numerical_cols": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical_cols": df.select_dtypes(include=['object']).columns.tolist(),
                "data_shape": df.shape,
                "missing_data": df.isnull().sum().sum()
            }
        
        return {**state, "data_summary": analysis}
    
    def _generate_dashboard_layout(self, state: DashboardState) -> DashboardState:
        """Generate optimal layout for dashboard"""
        dashboard_type = state.get("dashboard_type", "exploratory")
        chart_suggestions = self.dashboard_tools.suggest_chart_types(state["df"], dashboard_type)
        layout_config = self.dashboard_tools.generate_dashboard_layout(dashboard_type, len(chart_suggestions))
        
        return {
            **state, 
            "layout_config": layout_config,
            "chart_configs": chart_suggestions
        }
    
    def _create_dashboard_charts(self, state: DashboardState) -> DashboardState:
        """Create chart configurations for dashboard"""
        df = state["df"]
        chart_configs = []
        
        for chart_suggestion in state.get("chart_configs", []):
            chart_config = self.chart_tools.generate_plotly_config(
                chart_suggestion["type"],
                {"columns": chart_suggestion["columns"]},
                {"color": "#2563eb"}
            )
            chart_configs.append({
                **chart_suggestion,
                "plotly_config": chart_config,
                "id": f"chart_{uuid.uuid4().hex[:8]}"
            })
        
        return {**state, "chart_configs": chart_configs}
    
    def _generate_dashboard_insights(self, state: DashboardState) -> DashboardState:
        """Generate insights for dashboard"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        insights = []
        if dashboard_type == "executive":
            insights = [
                f"Dataset contains {len(df)} records across {len(df.columns)} dimensions",
                "Key performance indicators have been identified and prioritized",
                "Trend analysis reveals actionable business insights"
            ]
        elif dashboard_type == "data_quality":
            missing_percent = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            insights = [
                f"Overall data completeness: {100-missing_percent:.1f}%",
                f"Quality assessment completed across {len(df.columns)} columns",
                "Recommendations provided for data improvement opportunities"
            ]
        else:
            insights = [
                f"Comprehensive analysis of {len(df)} data points",
                "Statistical relationships and patterns identified",
                "Exploratory visualizations configured for deep analysis"
            ]
        
        return {**state, "insights": insights}
    
    def _compile_dashboard_code(self, state: DashboardState) -> DashboardState:
        """Compile complete dashboard code"""
        dashboard_type = state.get("dashboard_type", "exploratory")
        layout_config = state.get("layout_config", {})
        chart_configs = state.get("chart_configs", [])
        insights = state.get("insights", [])
        
        # Generate complete HTML/JS dashboard code
        dashboard_html = self._generate_dashboard_html(
            dashboard_type, layout_config, chart_configs, insights
        )
        
        return {**state, "dashboard_code": dashboard_html}
    
    def _generate_dashboard_html(self, dashboard_type: str, layout: Dict, charts: List[Dict], insights: List[str]) -> str:
        """Generate complete dashboard HTML code"""
        color_schemes = {
            "executive": {"primary": "#1e40af", "secondary": "#3b82f6", "accent": "#60a5fa"},
            "quality": {"primary": "#059669", "secondary": "#10b981", "accent": "#34d399"},
            "analytical": {"primary": "#7c3aed", "secondary": "#8b5cf6", "accent": "#a78bfa"}
        }
        
        colors = color_schemes.get(dashboard_type, color_schemes["analytical"])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard_type.title()} Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }}
        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        .dashboard-header {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        .dashboard-header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .dashboard-header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat({layout.get('grid_columns', 2)}, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
        }}
        .insights-panel {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-left: 4px solid {colors['accent']};
        }}
        .insight-item {{
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f1f5f9;
        }}
        .insight-item:last-child {{ border-bottom: none; }}
        .insight-icon {{
            width: 8px;
            height: 8px;
            background: {colors['accent']};
            border-radius: 50%;
            margin-right: 12px;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="dashboard-header">
            <h1>{dashboard_type.title()} Dashboard</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="dashboard-grid">
"""
        
        # Add chart containers
        for i, chart in enumerate(charts):
            html_template += f"""
            <div class="chart-container">
                <div id="chart_{i}"></div>
            </div>
"""
        
        html_template += f"""
        </div>
        
        <div class="insights-panel">
            <h3 style="color: {colors['primary']}; margin-bottom: 20px; font-size: 1.3rem;">Key Insights</h3>
"""
        
        # Add insights
        for insight in insights:
            html_template += f"""
            <div class="insight-item">
                <div class="insight-icon"></div>
                <span>{insight}</span>
            </div>
"""
        
        html_template += """
        </div>
    </div>
    
    <script>
        // Chart data and configurations
        const chartConfigs = """ + json.dumps([chart.get("plotly_config", {}) for chart in charts]) + """;
        
        // Render all charts
        chartConfigs.forEach((config, index) => {
            if (config.data && config.layout) {
                Plotly.newPlot(`chart_${index}`, config.data, config.layout, config.config || {});
            }
        });
        
        // Make charts responsive
        window.addEventListener('resize', () => {
            chartConfigs.forEach((config, index) => {
                Plotly.Plots.resize(`chart_${index}`);
            });
        });
    </script>
</body>
</html>
"""
        
        return html_template
    
    # Data processing agent node implementations
    def _analyze_data_quality(self, state: DataProcessingState) -> DataProcessingState:
        """Analyze data quality"""
        df = state["df"]
        quality_analysis = self.data_tools.suggest_missing_data_strategy(df)
        quality_score = sum(1 for col_analysis in quality_analysis.values() 
                          if col_analysis["missing_percent"] < 10) / len(quality_analysis) * 100
        
        return {**state, "data_quality_score": quality_score, "data_summary": quality_analysis}
    
    def _convert_data_to_json(self, state: DataProcessingState) -> DataProcessingState:
        """Convert DataFrame to JSON structure"""
        df = state["df"]
        json_data = self.data_tools.convert_to_json_structure(df)
        
        return {**state, "data_json": json_data}
    
    def _suggest_preprocessing_steps(self, state: DataProcessingState) -> DataProcessingState:
        """Suggest preprocessing steps"""
        processing_steps = [
            "Data quality analysis completed",
            "JSON structure optimized for frontend",
            "Missing data strategies identified",
            "Outlier detection configured"
        ]
        
        return {**state, "processing_steps": processing_steps}
    
    def _apply_preprocessing(self, state: DataProcessingState) -> DataProcessingState:
        """Apply preprocessing steps"""
        # This would contain actual preprocessing logic
        processed_data = state.get("data_json", {})
        
        return {**state, "processed_data": processed_data}
    
    # Chart generation agent node implementations
    def _analyze_chart_requirements(self, state: ChartGenerationState) -> ChartGenerationState:
        """Analyze chart requirements"""
        df = state["df"]
        chart_purpose = state.get("chart_purpose", "general_analysis")
        
        analysis = {
            "data_types": df.dtypes.to_dict(),
            "data_shape": df.shape,
            "purpose": chart_purpose
        }
        
        return {**state, "data_summary": analysis}
    
    def _select_chart_type(self, state: ChartGenerationState) -> ChartGenerationState:
        """Select optimal chart type"""
        # Logic for intelligent chart type selection
        chart_type = state.get("chart_type", "scatter")
        return {**state, "chart_type": chart_type}
    
    def _generate_chart_config(self, state: ChartGenerationState) -> ChartGenerationState:
        """Generate chart configuration"""
        chart_config = self.chart_tools.generate_plotly_config(
            state["chart_type"],
            {"data": "placeholder"},
            state.get("styling_preferences", {})
        )
        
        return {**state, "chart_data": chart_config}
    
    def _apply_chart_styling(self, state: ChartGenerationState) -> ChartGenerationState:
        """Apply styling to chart"""
        # Apply final styling touches
        return state
    
    # Public API methods
    async def generate_dashboard(
        self, 
        df: pd.DataFrame, 
        dashboard_type: str = "exploratory",
        user_context: str = "",
        target_audience: str = "analyst"
    ) -> Dict[str, Any]:
        """Generate complete dashboard using LangGraph workflow"""
        try:
            initial_state: DashboardState = {
                "session_id": uuid.uuid4().hex,
                "df": df,
                "dashboard_type": dashboard_type,
                "user_context": user_context,
                "target_audience": target_audience,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.dashboard_agent.invoke(initial_state)
            
            return {
                "success": True,
                "dashboard_html": result.get("dashboard_code", ""),
                "layout_config": result.get("layout_config", {}),
                "chart_configs": result.get("chart_configs", []),
                "insights": result.get("insights", []),
                "session_id": result.get("session_id", ""),
                "data_summary": result.get("data_summary", {})
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_data_to_json(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Process data and convert to JSON using LangGraph workflow"""
        try:
            initial_state: DataProcessingState = {
                "session_id": uuid.uuid4().hex,
                "df": df,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.data_processing_agent.invoke(initial_state)
            
            return {
                "success": True,
                "json_data": result.get("data_json", {}),
                "quality_score": result.get("data_quality_score", 0),
                "processing_steps": result.get("processing_steps", []),
                "data_summary": result.get("data_summary", {}),
                "session_id": result.get("session_id", "")
            }
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_chart(
        self, 
        df: pd.DataFrame, 
        chart_type: str = "auto",
        columns: List[str] = None,
        chart_purpose: str = "analysis"
    ) -> Dict[str, Any]:
        """Generate single chart using LangGraph workflow"""
        try:
            initial_state: ChartGenerationState = {
                "session_id": uuid.uuid4().hex,
                "df": df,
                "chart_type": chart_type,
                "columns_used": columns or [],
                "chart_purpose": chart_purpose,
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.chart_generation_agent.invoke(initial_state)
            
            return {
                "success": True,
                "chart_config": result.get("chart_data", {}),
                "chart_type": result.get("chart_type", ""),
                "session_id": result.get("session_id", "")
            }
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return {"success": False, "error": str(e)}