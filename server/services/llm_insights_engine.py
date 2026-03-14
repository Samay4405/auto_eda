"""
LLM-Powered Insights Engine for Real-Time Dashboard Analysis

This module provides intelligent analysis of generated dashboards and data
using LLM capabilities to generate actionable insights, recommendations,
and business intelligence.
"""

import os
import json
import warnings
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

# Suppress huggingface warnings BEFORE any imports
import warnings
warnings.filterwarnings("ignore")

import os
import json
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

# Try to import LangChain components and providers (OpenAI and Groq)
LC_OPENAI_AVAILABLE = False
LC_GROQ_AVAILABLE = False
ChatOpenAI = None
ChatGroq = None
ChatPromptTemplate = None
HumanMessage = None
SystemMessage = None
GROQ_SDK_AVAILABLE = False
GroqClient = None

try:
    from langchain_openai import ChatOpenAI as _ChatOpenAI
    LC_OPENAI_AVAILABLE = True
    ChatOpenAI = _ChatOpenAI
except Exception as e:
    # Silently fail - LangChain OpenAI not available
    pass

try:
    # Suppress ALL warnings during import attempt (huggingface_hub can be noisy)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        from langchain_groq import ChatGroq as _ChatGroq
        LC_GROQ_AVAILABLE = True
        ChatGroq = _ChatGroq
except Exception as e:
    # Import failed - likely due to huggingface_hub metadata issues
    # This is expected and we'll use OpenAI fallback or deterministic insights
    pass

try:
    from langchain.prompts import ChatPromptTemplate as _ChatPromptTemplate
    from langchain.schema import HumanMessage as _HumanMessage, SystemMessage as _SystemMessage
    ChatPromptTemplate = _ChatPromptTemplate
    HumanMessage = _HumanMessage
    SystemMessage = _SystemMessage
except Exception:
    # Prompts/messages unavailable – LLM paths will fallback
    pass

# Try to import Groq SDK (direct client, no transformers dependency)
try:
    from groq import Groq as _GroqClient  # type: ignore
    GROQ_SDK_AVAILABLE = True
    GroqClient = _GroqClient
except Exception:
    GROQ_SDK_AVAILABLE = False

# Backwards-compatibility flag expected by some tests
LANGCHAIN_AVAILABLE = bool(LC_OPENAI_AVAILABLE or LC_GROQ_AVAILABLE)


class LLMInsightsEngine:
    """
    Advanced insights engine using LLM for real-time data and dashboard analysis.
    
    Provides:
    - Statistical insights and trend analysis
    - Anomaly detection and pattern recognition
    - Business recommendations
    - Data quality assessment
    - Predictive insights
    - Actionable next steps
    """
    
    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.3):
        """Initialize LLM insights engine with provider auto-selection.

        Provider selection order:
        1) Groq (if GROQ_API_KEY set and langchain-groq available)
        2) OpenAI (if OPENAI_API_KEY set and langchain-openai available)
        Else: raise to let caller fallback gracefully.
        """
        provider = None
        self.llm = None

        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        # Prefer Groq via LangChain if available
        if groq_key and LC_GROQ_AVAILABLE and ChatGroq is not None:
            provider = "groq"
            groq_model_env = os.getenv("GROQ_MODEL", "")
            groq_model = groq_model_env if groq_model_env else (model_name or "openai/gpt-oss-120b")
            try:
                self.llm = ChatGroq(model=groq_model, temperature=temperature)
            except Exception as e:
                raise ValueError(f"Failed to initialize Groq LLM: {e}")
        # Next, try direct Groq SDK (avoids transformers/huggingface import chain)
        elif groq_key and GROQ_SDK_AVAILABLE and GroqClient is not None:
            provider = "groq-direct"
            try:
                self.groq_client = GroqClient(api_key=groq_key)
                groq_model_env = os.getenv("GROQ_MODEL", "")
                self.groq_model = groq_model_env if groq_model_env else (model_name or "openai/gpt-oss-120b")
                self.temperature = float(temperature)
            except Exception as e:
                raise ValueError(f"Failed to initialize Groq direct client: {e}")
        elif openai_key and LC_OPENAI_AVAILABLE and ChatOpenAI is not None:
            provider = "openai"
            openai_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            try:
                self.llm = ChatOpenAI(model=openai_model, temperature=temperature, api_key=openai_key)
            except Exception as e:
                raise ValueError(f"Failed to initialize OpenAI LLM: {e}")
        else:
            # Neither provider available
            raise ValueError("No supported LLM provider available. Set GROQ_API_KEY (preferred) or OPENAI_API_KEY and install langchain-groq or langchain-openai.")
        
        self.provider = provider
    
    def _groq_complete(self, system_text: str, user_text: str) -> str:
        """Call Groq chat completions API using the direct SDK path."""
        if not hasattr(self, "groq_client"):
            raise RuntimeError("Groq client not initialized")
        resp = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": user_text},
            ],
            temperature=self.temperature,
        )
        return resp.choices[0].message.content
        
    def analyze_dashboard(
        self,
        df: pd.DataFrame,
        dashboard_type: str,
        chart_specs: List[Dict[str, Any]],
        data_analysis: Dict[str, Any],
        user_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive dashboard analysis using LLM.
        
        Args:
            df: The DataFrame being analyzed
            dashboard_type: Type of dashboard (executive, exploratory, data_quality)
            chart_specs: Chart specifications generated
            data_analysis: Statistical analysis results
            user_context: Optional user-provided context
            
        Returns:
            Dictionary containing comprehensive insights
        """
        # Prepare data summary for LLM
        data_summary = self._create_data_summary(df)
        
        # Generate insights based on dashboard type
        if dashboard_type == "executive":
            insights = self._analyze_executive_dashboard(
                data_summary, chart_specs, data_analysis, user_context
            )
        elif dashboard_type == "data_quality":
            insights = self._analyze_data_quality(
                data_summary, chart_specs, data_analysis, user_context
            )
        elif dashboard_type == "exploratory":
            insights = self._analyze_exploratory_dashboard(
                data_summary, chart_specs, data_analysis, user_context
            )
        else:
            insights = self._analyze_general_dashboard(
                data_summary, chart_specs, data_analysis, user_context
            )
        
        return insights
    
    def _create_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive data summary for LLM context"""
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numerical_columns": len(numerical_cols),
            "categorical_columns": len(categorical_cols),
            "missing_values_total": int(df.isnull().sum().sum()),
            "missing_percentage": float((df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
        }
        
        # Add statistical summary for numerical columns
        if numerical_cols:
            summary["numerical_stats"] = {}
            for col in numerical_cols[:5]:  # Top 5 for context
                summary["numerical_stats"][col] = {
                    "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                    "median": float(df[col].median()) if pd.notna(df[col].median()) else None,
                    "std": float(df[col].std()) if pd.notna(df[col].std()) else None,
                    "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                    "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                    "unique_values": int(df[col].nunique())
                }
        
        # Add categorical summary
        if categorical_cols:
            summary["categorical_stats"] = {}
            for col in categorical_cols[:5]:  # Top 5 for context
                summary["categorical_stats"][col] = {
                    "unique_values": int(df[col].nunique()),
                    "most_common": str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None,
                    "most_common_count": int(df[col].value_counts().iloc[0]) if len(df[col]) > 0 else 0
                }
        
        return summary
    
    def _analyze_executive_dashboard(
        self,
        data_summary: Dict[str, Any],
        chart_specs: List[Dict[str, Any]],
        data_analysis: Dict[str, Any],
        user_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate executive-level insights"""
        
        system_text = (
            "You are an expert business intelligence analyst with deep expertise in "
            "executive reporting and strategic insights. Your role is to analyze dashboards and data to provide "
            "C-level executives with actionable, high-impact insights that drive business decisions.\n\n"
            "Focus on:\n"
            "- Strategic implications and business outcomes\n"
            "- Key performance trends and their drivers\n"
            "- Risk factors and opportunities\n"
            "- Actionable recommendations with clear priorities\n"
            "- ROI and business value perspectives\n\n"
            "Be concise, data-driven, and business-focused. Avoid technical jargon."
        )
        user_text = (
            "Analyze this executive dashboard and provide strategic insights:\n\n"
            f"DATA SUMMARY:\n{json.dumps(data_summary, indent=2)}\n\n"
            f"DASHBOARD CONTEXT:\n{user_context or 'Executive performance dashboard'}\n\n"
            f"CHARTS GENERATED:\n{len(chart_specs)} visualizations including KPIs, trends, and performance metrics\n\n"
            "KPI ANALYSIS:\n"
            f"{json.dumps(data_analysis.get('kpis', []), indent=2) if 'kpis' in data_analysis else 'No KPIs available'}\n\n"
            "Provide a comprehensive analysis with:\n"
            "1. **Executive Summary** (2-3 sentences of the most critical findings)\n"
            "2. **Key Performance Insights** (3-5 bullet points on main trends and metrics)\n"
            "3. **Strategic Opportunities** (2-3 actionable opportunities identified in the data)\n"
            "4. **Risk Factors** (2-3 potential concerns or areas needing attention)\n"
            "5. **Recommended Actions** (3-5 specific, prioritized recommendations)\n"
            "6. **Business Impact** (How these insights translate to business outcomes)\n\n"
            "Format as JSON with keys: executive_summary, key_insights, opportunities, risks, recommendations, business_impact"
        )

        try:
            if getattr(self, "provider", None) == "groq-direct":
                insights_text = self._groq_complete(system_text, user_text)
            else:
                if ChatPromptTemplate and SystemMessage and HumanMessage:
                    prompt = ChatPromptTemplate.from_messages([
                        SystemMessage(content=system_text),
                        HumanMessage(content=user_text),
                    ])
                    response = self.llm.invoke(prompt.format_messages())
                    insights_text = response.content
                else:
                    # Last resort – single-message prompt
                    combined = system_text + "\n\n" + user_text
                    insights_text = self._groq_complete("You are a helpful analyst.", combined) if getattr(self, "provider", None) == "groq-direct" else combined
            
            # Try to extract JSON
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            insights["analysis_type"] = "executive"
            insights["generated_at"] = datetime.now().isoformat()
            
            return insights
            
        except Exception as e:
            # Fallback to basic insights
            return self._fallback_executive_insights(data_summary, data_analysis)
    
    def _analyze_data_quality(
        self,
        data_summary: Dict[str, Any],
        chart_specs: List[Dict[str, Any]],
        data_analysis: Dict[str, Any],
        user_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate data quality insights"""
        
        system_text = (
            "You are a data quality expert specializing in data governance, "
            "integrity assessment, and data preparation. Analyze datasets to identify quality issues, "
            "assess readiness for analysis, and recommend remediation strategies.\n\n"
            "Focus on:\n"
            "- Data completeness and consistency\n"
            "- Outliers and anomalies\n"
            "- Data type appropriateness\n"
            "- Potential data entry errors\n"
            "- Impact on downstream analytics\n"
            "- Prioritized remediation steps\n\n"
            "Be thorough, technical where needed, and provide clear actionability."
        )
        user_text = (
            "Assess the data quality of this dataset:\n\n"
            f"DATA SUMMARY:\n{json.dumps(data_summary, indent=2)}\n\n"
            f"QUALITY METRICS:\n{json.dumps(data_analysis, indent=2)}\n\n"
            f"CONTEXT:\n{user_context or 'Data quality assessment'}\n\n"
            "Provide a comprehensive quality assessment with:\n"
            "1. **Overall Quality Score** (0-100 with justification)\n"
            "2. **Critical Issues** (3-5 most serious data quality problems)\n"
            "3. **Data Completeness Analysis** (Assessment of missing data impact)\n"
            "4. **Consistency Findings** (Data type, format, value range issues)\n"
            "5. **Anomalies Detected** (Outliers, unusual patterns, potential errors)\n"
            "6. **Remediation Priorities** (Ordered list of fixes with expected impact)\n"
            "7. **Readiness Assessment** (Is data ready for analysis/production?)\n\n"
            "Format as JSON with keys: quality_score, score_justification, critical_issues, completeness, "
            "consistency, anomalies, remediation_priorities, readiness_assessment"
        )

        try:
            if getattr(self, "provider", None) == "groq-direct":
                insights_text = self._groq_complete(system_text, user_text)
            else:
                if ChatPromptTemplate and SystemMessage and HumanMessage:
                    prompt = ChatPromptTemplate.from_messages([
                        SystemMessage(content=system_text),
                        HumanMessage(content=user_text),
                    ])
                    response = self.llm.invoke(prompt.format_messages())
                    insights_text = response.content
                else:
                    combined = system_text + "\n\n" + user_text
                    insights_text = self._groq_complete("You are a helpful analyst.", combined) if getattr(self, "provider", None) == "groq-direct" else combined
            
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            insights["analysis_type"] = "data_quality"
            insights["generated_at"] = datetime.now().isoformat()
            
            return insights
            
        except Exception as e:
            return self._fallback_quality_insights(data_summary, data_analysis)
    
    def _analyze_exploratory_dashboard(
        self,
        data_summary: Dict[str, Any],
        chart_specs: List[Dict[str, Any]],
        data_analysis: Dict[str, Any],
        user_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate exploratory analysis insights"""
        
        system_text = (
            "You are a data scientist and statistical analyst expert in exploratory "
            "data analysis. Your role is to uncover patterns, relationships, and insights that may not be "
            "immediately obvious. Think like a detective looking for interesting stories in the data.\n\n"
            "Focus on:\n"
            "- Statistical patterns and distributions\n"
            "- Correlations and relationships\n"
            "- Segmentation opportunities\n"
            "- Unexpected findings\n"
            "- Hypothesis generation for deeper analysis\n"
            "- Next analytical steps\n\n"
            "Be curious, thorough, and insightful. Surface the interesting stories hidden in the data."
        )
        user_text = (
            "Perform exploratory analysis on this dataset:\n\n"
            f"DATA SUMMARY:\n{json.dumps(data_summary, indent=2)}\n\n"
            f"STATISTICAL ANALYSIS:\n{json.dumps(data_analysis.get('distributions', {}), indent=2)}\n\n"
            f"CORRELATIONS:\n{json.dumps(data_analysis.get('correlations', {}), indent=2)}\n\n"
            f"CONTEXT:\n{user_context or 'Exploratory data analysis'}\n\n"
            f"CHARTS GENERATED:\n{', '.join([c.get('type', 'unknown') for c in chart_specs])}\n\n"
            "Provide comprehensive exploratory insights with:\n"
            "1. **Key Patterns Discovered** (3-5 most interesting patterns in the data)\n"
            "2. **Correlation Insights** (Significant relationships and their implications)\n"
            "3. **Distribution Analysis** (Notable characteristics of data distributions)\n"
            "4. **Segmentation Opportunities** (Natural groupings or clusters identified)\n"
            "5. **Anomalies & Outliers** (Unusual observations worth investigating)\n"
            "6. **Statistical Highlights** (Interesting statistical findings)\n"
            "7. **Recommended Deep Dives** (Areas warranting further analysis)\n"
            "8. **Hypothesis Generation** (3-5 testable Hypothesis  based on patterns)\n\n"
            "Format as JSON with keys: patterns, correlations, distributions, segmentation, "
            "anomalies, statistical_highlights, deep_dive_recommendations, Hypothesis "
        )

        try:
            if getattr(self, "provider", None) == "groq-direct":
                insights_text = self._groq_complete(system_text, user_text)
            else:
                if ChatPromptTemplate and SystemMessage and HumanMessage:
                    prompt = ChatPromptTemplate.from_messages([
                        SystemMessage(content=system_text),
                        HumanMessage(content=user_text),
                    ])
                    response = self.llm.invoke(prompt.format_messages())
                    insights_text = response.content
                else:
                    combined = system_text + "\n\n" + user_text
                    insights_text = self._groq_complete("You are a helpful analyst.", combined) if getattr(self, "provider", None) == "groq-direct" else combined
            
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            insights["analysis_type"] = "exploratory"
            insights["generated_at"] = datetime.now().isoformat()
            
            return insights
            
        except Exception as e:
            return self._fallback_exploratory_insights(data_summary, data_analysis)
    
    def _analyze_general_dashboard(
        self,
        data_summary: Dict[str, Any],
        chart_specs: List[Dict[str, Any]],
        data_analysis: Dict[str, Any],
        user_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate general insights for any dashboard type"""
        
        system_text = (
            "You are a versatile data analyst capable of extracting insights "
            "from any type of dataset. Provide clear, actionable insights that help users understand their "
            "data better and make informed decisions."
        )
        user_text = (
            "Analyze this dataset and dashboard:\n\n"
            f"DATA SUMMARY:\n{json.dumps(data_summary, indent=2)}\n\n"
            f"CONTEXT:\n{user_context or 'General data analysis'}\n\n"
            "Provide:\n"
            "1. **Summary** (Overview of the dataset)\n"
            "2. **Key Findings** (3-5 main insights)\n"
            "3. **Data Characteristics** (Notable features)\n"
            "4. **Recommendations** (3-5 actionable next steps)\n\n"
            "Format as JSON with keys: summary, key_findings, characteristics, recommendations"
        )

        try:
            if getattr(self, "provider", None) == "groq-direct":
                insights_text = self._groq_complete(system_text, user_text)
            else:
                if ChatPromptTemplate and SystemMessage and HumanMessage:
                    prompt = ChatPromptTemplate.from_messages([
                        SystemMessage(content=system_text),
                        HumanMessage(content=user_text),
                    ])
                    response = self.llm.invoke(prompt.format_messages())
                    insights_text = response.content
                else:
                    combined = system_text + "\n\n" + user_text
                    insights_text = self._groq_complete("You are a helpful analyst.", combined) if getattr(self, "provider", None) == "groq-direct" else combined
            
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0].strip()
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(insights_text)
            insights["analysis_type"] = "general"
            insights["generated_at"] = datetime.now().isoformat()
            
            return insights
            
        except Exception as e:
            return self._fallback_general_insights(data_summary)
    
    # Fallback methods for when LLM is unavailable
    def _fallback_executive_insights(
        self, data_summary: Dict[str, Any], data_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback executive insights without LLM"""
        return {
            "analysis_type": "executive",
            "executive_summary": f"Dashboard analyzing {data_summary['total_rows']:,} records across {data_summary['total_columns']} metrics. Data completeness at {100 - data_summary['missing_percentage']:.1f}%.",
            "key_insights": [
                f"Dataset contains {data_summary['numerical_columns']} numerical KPIs",
                f"Data quality: {100 - data_summary['missing_percentage']:.1f}% complete",
                "Performance trends available for analysis"
            ],
            "opportunities": [
                "Leverage complete data for strategic decision-making",
                "Identify top performers and best practices"
            ],
            "risks": [
                f"Missing data in {data_summary['missing_percentage']:.1f}% of values may impact analysis"
            ],
            "recommendations": [
                "Monitor key metrics regularly",
                "Investigate anomalies in performance data",
                "Set up alerts for significant changes"
            ],
            "business_impact": "Enable data-driven decision making and performance optimization",
            "generated_at": datetime.now().isoformat(),
            "source": "fallback"
        }
    
    def _fallback_quality_insights(
        self, data_summary: Dict[str, Any], data_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback quality insights without LLM"""
        quality_score = max(0, 100 - data_summary['missing_percentage'] * 2)
        
        return {
            "analysis_type": "data_quality",
            "quality_score": int(quality_score),
            "score_justification": f"Based on {100 - data_summary['missing_percentage']:.1f}% completeness",
            "critical_issues": [
                f"{data_summary['missing_values_total']} missing values detected" if data_summary['missing_values_total'] > 0 else "No missing values"
            ],
            "completeness": f"{100 - data_summary['missing_percentage']:.1f}% of data is complete",
            "consistency": "Data types appear consistent within columns",
            "anomalies": "Statistical outlier detection recommended",
            "remediation_priorities": [
                "Address missing values through imputation or removal",
                "Validate data ranges and constraints",
                "Standardize data formats"
            ],
            "readiness_assessment": "Data is ready for analysis" if quality_score > 80 else "Data requires cleaning before production use",
            "generated_at": datetime.now().isoformat(),
            "source": "fallback"
        }
    
    def _fallback_exploratory_insights(
        self, data_summary: Dict[str, Any], data_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback exploratory insights without LLM"""
        return {
            "analysis_type": "exploratory",
            "patterns": [
                f"Dataset contains {data_summary['total_rows']:,} observations",
                f"{data_summary['numerical_columns']} numerical variables for analysis",
                f"{data_summary['categorical_columns']} categorical variables"
            ],
            "correlations": "Correlation analysis available in visualization",
            "distributions": "Distribution patterns visible in charts",
            "segmentation": "Natural groupings may exist - explore visualizations",
            "anomalies": "Outlier detection recommended for numerical columns",
            "statistical_highlights": [
                f"Data spans {data_summary['total_columns']} dimensions",
                f"Completeness: {100 - data_summary['missing_percentage']:.1f}%"
            ],
            "deep_dive_recommendations": [
                "Investigate correlation patterns",
                "Analyze distribution shapes",
                "Explore categorical relationships"
            ],
            "Hypothesis ": [
                "Strong correlations may indicate causal relationships",
                "Distribution patterns suggest natural segmentation",
                "Outliers may represent special cases or errors"
            ],
            "generated_at": datetime.now().isoformat(),
            "source": "fallback"
        }
    
    def _fallback_general_insights(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback general insights without LLM"""
        return {
            "analysis_type": "general",
            "summary": f"Dataset with {data_summary['total_rows']:,} rows and {data_summary['total_columns']} columns",
            "key_findings": [
                f"{data_summary['numerical_columns']} numerical columns",
                f"{data_summary['categorical_columns']} categorical columns",
                f"{100 - data_summary['missing_percentage']:.1f}% data completeness"
            ],
            "characteristics": "Mixed numerical and categorical data suitable for comprehensive analysis",
            "recommendations": [
                "Explore visualizations for patterns",
                "Check data quality metrics",
                "Consider advanced analytics"
            ],
            "generated_at": datetime.now().isoformat(),
            "source": "fallback"
        }


def generate_insights_summary(insights: Dict[str, Any]) -> List[str]:
    """
    Convert structured LLM insights into a list of readable summary points.
    
    Args:
        insights: Dictionary of insights from LLM analysis
        
    Returns:
        List of formatted insight strings
    """
    summary = []
    analysis_type = insights.get("analysis_type", "general")
    
    if analysis_type == "executive":
        summary.append(f"📊 Executive Summary: {insights.get('executive_summary', 'N/A')}")
        
        if insights.get('key_insights'):
            summary.append("🎯 Key Insights:")
            for insight in insights['key_insights'][:3]:
                summary.append(f"  • {insight}")
        
        if insights.get('recommendations'):
            summary.append("💡 Top Recommendations:")
            for rec in insights['recommendations'][:3]:
                summary.append(f"  • {rec}")
    
    elif analysis_type == "data_quality":
        summary.append(f"✅ Quality Score: {insights.get('quality_score', 0)}/100")
        summary.append(f"📝 {insights.get('score_justification', 'N/A')}")
        
        if insights.get('critical_issues'):
            summary.append("⚠️ Critical Issues:")
            for issue in insights['critical_issues'][:3]:
                summary.append(f"  • {issue}")
    
    elif analysis_type == "exploratory":
        if insights.get('patterns'):
            summary.append("🔍 Key Patterns:")
            for pattern in insights['patterns'][:3]:
                summary.append(f"  • {pattern}")
        
        if insights.get('Hypothesis '):
            summary.append("💭 Hypothesis  to Test:")
            for hyp in insights['Hypothesis '][:3]:
                summary.append(f"  • {hyp}")
    
    return summary
