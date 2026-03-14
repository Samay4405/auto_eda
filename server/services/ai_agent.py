import os
from typing import Dict, List, Any, TypedDict
import pandas as pd
import numpy as np
import json
import asyncio

from langgraph.graph import StateGraph, END

from .data_processor import DataProcessor
from .chart_generator import ChartGenerator


class EDAState(TypedDict, total=False):
    df: pd.DataFrame
    basic_info: Dict[str, Any]
    operation: str
    options: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    operation_results: Dict[str, Any]
    insights: Dict[str, Any]


class AIAgent:
    """Agentic EDA pipeline implemented with LangGraph (no external LLM required).

    The graph orchestrates:
    - summarize -> recommend -> execute -> insights
    """

    def __init__(self):
        self.data_processor = DataProcessor()
        self.chart_generator = ChartGenerator()

        # Build the agent graph once
        graph = StateGraph(EDAState)

        graph.add_node("summarize", self._node_summarize)
        graph.add_node("recommend", self._node_recommend)
        graph.add_node("execute", self._node_execute)
        graph.add_node("generate_insights", self._node_insights)

        graph.set_entry_point("summarize")
        graph.add_edge("summarize", "recommend")
        graph.add_edge("recommend", "execute")
        graph.add_edge("execute", "generate_insights")
        graph.add_edge("generate_insights", END)

        self._compiled = graph.compile()

    # Graph nodes
    def _node_summarize(self, state: EDAState) -> EDAState:
        df = state["df"]
        basic_info = self.data_processor.get_basic_info(df)
        return {**state, "basic_info": basic_info}

    def _node_recommend(self, state: EDAState) -> EDAState:
        op = state.get("operation", "visualize")
        basic = state.get("basic_info", {})
        dtypes = basic.get("dtypes", {})
        missing = basic.get("missing_values", {})

        recommendations: List[Dict[str, Any]] = []
        if op == "clean":
            if any(v > 0 for v in missing.values()):
                recommendations.append(
                    {
                        "action": "handle_missing_values",
                        "method": "imputation",
                        "columns": [c for c, v in missing.items() if v > 0],
                    }
                )
            recommendations.append(
                {"action": "remove_duplicates", "method": "drop_duplicates"}
            )
            recommendations.append(
                {"action": "convert_data_types", "method": "automatic_conversion"}
            )
        elif op == "transform":
            num_cols = [c for c, t in dtypes.items() if "int" in t or "float" in t]
            cat_cols = [c for c, t in dtypes.items() if t == "object"]
            if num_cols:
                recommendations.append(
                    {
                        "action": "scale_features",
                        "method": "standard_scaling",
                        "columns": num_cols,
                    }
                )
            if cat_cols:
                recommendations.append(
                    {
                        "action": "encode_categorical",
                        "method": "label_encoding",
                        "columns": cat_cols,
                    }
                )
        elif op == "classify":
            recommendations.append(
                {
                    "action": "analyze_data_types",
                    "method": "comprehensive_classification",
                }
            )
        else:  # visualize/default
            recommendations.append(
                {
                    "action": "create_comprehensive_charts",
                    "method": "automatic_chart_selection",
                }
            )

        return {**state, "recommendations": recommendations}

    def _node_execute(self, state: EDAState) -> EDAState:
        df = state["df"]
        op = state.get("operation", "visualize")
        options = state.get("options", {})
        recs = state.get("recommendations", [])

        if op == "clean":
            cleaning_options = {
                "remove_duplicates": True,
                "missing_strategy": "impute",
                "numerical_impute_strategy": "mean",
                "categorical_impute_strategy": "most_frequent",
                "convert_dtypes": True,
                "remove_outliers": options.get("remove_outliers", False),
            }
            results = self.data_processor.clean_data(df, cleaning_options)
        elif op == "transform":
            transform_options = {
                "scaling_method": options.get("scaling_method", "standard"),
                "encoding_method": options.get("encoding_method", "label"),
                "create_features": options.get("create_features", False),
            }
            results = self.data_processor.transform_data(df, transform_options)
        elif op == "classify":
            results = self.data_processor.classify_data(df, options)
        else:
            chart_options = {"chart_type": "auto"}
            results = self.chart_generator.generate_charts(df, chart_options)

        return {**state, "operation_results": results}

    def _node_insights(self, state: EDAState) -> EDAState:
        basic = state.get("basic_info", {})
        op_results = state.get("operation_results", {})

        # Simple, deterministic insights based on summary and results
        findings = [
            f"Dataset has {basic.get('shape', ['?','?'])[0]} rows and {basic.get('shape', ['?','?'])[1]} columns.",
        ]
        if basic.get("missing_values"):
            total_missing = int(sum(basic["missing_values"].values()))
            if total_missing > 0:
                findings.append(
                    f"Detected {total_missing} missing values across columns."
                )

        recommendations = []
        if "cleaned_df" in op_results:
            recommendations.append("Review cleaned data and validate transformations.")
        if op_results.get("charts"):
            recommendations.append(
                "Explore generated charts for patterns and anomalies."
            )

        insights = {
            "key_findings": findings or ["Analysis completed."],
            "recommendations": recommendations or ["Proceed with further analysis."],
            "next_steps": [
                "Iterate on dashboard filters and KPIs based on stakeholder feedback."
            ],
        }

        return {**state, "insights": insights}

    # Public API
    async def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        basic_info = self.data_processor.get_basic_info(df)
        # Simple heuristic quality score
        missing_total = int(sum(basic_info.get("missing_values", {}).values()))
        total_cells = int(
            basic_info.get("shape", [0, 0])[0]
            * max(1, basic_info.get("shape", [0, 0])[1])
        )
        quality = 100 - int((missing_total / total_cells) * 100) if total_cells else 80
        ai_analysis = {
            "quality_score": max(0, min(100, quality)),
            "issues": ["Missing values present"] if missing_total else [],
            "recommendations": (
                ["Consider imputing missing values"]
                if missing_total
                else ["Data quality looks good"]
            ),
            "column_insights": {},
        }
        return {"basic_info": basic_info, "ai_analysis": ai_analysis}

    async def generate_recommendations(
        self, operation: str, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        # Reuse the recommend node logic
        state: EDAState = {
            "df": pd.DataFrame(),
            "operation": operation,
            "basic_info": analysis.get("basic_info", {}),
        }
        next_state = self._node_recommend(state)
        return next_state.get("recommendations", [])

    async def apply_operations(
        self,
        df: pd.DataFrame,
        operation: str,
        recommendations: List[Dict[str, Any]],
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        state: EDAState = {
            "df": df,
            "operation": operation,
            "options": options,
            "recommendations": recommendations,
        }
        next_state = self._node_execute(state)
        return next_state.get("operation_results") or {}


    async def generate_insights(
        self, df: pd.DataFrame, operation_results: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        state: EDAState = {
            "df": df,
            "operation_results": operation_results or {},
            "basic_info": self.data_processor.get_basic_info(df),
        }
        next_state = self._node_insights(state)
        return next_state.get("insights", {})

    async def process_data(
        self, df: pd.DataFrame, operation: str, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            result_state = self._compiled.invoke(
                {"df": df, "operation": operation, "options": options}
            )
            charts: List[Dict[str, Any]] = []
            if operation != "visualize":
                charts = self.chart_generator.generate_all_charts(
                    df, "distribution,correlation,missing"
                )
            else:
                charts = result_state.get("operation_results", {}).get("charts", [])

            return {
                "success": True,
                "operation": operation,
                "analysis": {
                    "basic_info": result_state.get("basic_info", {}),
                    "ai_analysis": {},
                },
                "results": result_state.get("operation_results", {}),
                "charts": charts,
                "insights": result_state.get("insights", {}),
                "recommendations": result_state.get("recommendations", []),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "operation": operation}
