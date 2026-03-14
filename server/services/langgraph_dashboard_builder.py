"""
LangGraph-powered dashboard builder that generates complete dashboard code dynamically.
Replaces template-based approach with intelligent code generation.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Literal, TypedDict, Annotated
from datetime import datetime
import logging
import uuid
import operator
import hashlib
from functools import lru_cache

from langgraph.graph import StateGraph, END
from .langgraph_agents import LangGraphAgentOrchestrator
from .dashboard_tools import DashboardToolFactory
from .csv_to_json import CSVToJSONConverter
from .llm_insights_engine import LLMInsightsEngine, generate_insights_summary

# Optional LLM integration: try to import LangChain LLM wrappers (OpenAI/Groq). If unavailable,
# the code generator fallback will be used.
import os
try:
    # Try multiple import paths for different langchain versions
    try:
        from langchain_openai import ChatOpenAI as LCOpenAI  # type: ignore
        _USE_CHAT_MODEL = True
    except Exception:
        try:
            from langchain.chat_models import ChatOpenAI as LCOpenAI  # type: ignore
            _USE_CHAT_MODEL = True
        except Exception:
            try:
                from langchain import OpenAI as LCOpenAI  # type: ignore
                _USE_CHAT_MODEL = False
            except Exception:
                from langchain.llms import OpenAI as LCOpenAI  # type: ignore
                _USE_CHAT_MODEL = False
except Exception:
    LCOpenAI = None  # type: ignore
    _USE_CHAT_MODEL = False

# Try to import Groq chat model as well
LCGroq = None
_GROQ_IMPORT_ERROR = None
try:
    from langchain_groq import ChatGroq as _ChatGroq  # type: ignore
    LCGroq = _ChatGroq
except Exception as e:
    _GROQ_IMPORT_ERROR = str(e)
    LCGroq = None

# Try to import HumanMessage for different LangChain versions
_HumanMessage = None
_HumanMessage_Import_Error = None
try:
    # Try langchain_core first (new versions)
    from langchain_core.messages import HumanMessage as _HumanMessage_
    _HumanMessage = _HumanMessage_
except Exception:
    try:
        # Try langchain.schema (older versions)
        from langchain.schema import HumanMessage as _HumanMessage_
        _HumanMessage = _HumanMessage_
    except Exception as e:
        _HumanMessage_Import_Error = str(e)
        _HumanMessage = None

logger = logging.getLogger(__name__)


class DashboardGenerationState(TypedDict, total=False):
    """State for dashboard generation workflow"""
    session_id: str
    df: pd.DataFrame
    json_data: Dict[str, Any]
    dashboard_type: str
    user_context: str
    target_audience: str
    layout_requirements: Dict[str, Any]
    data_analysis: Dict[str, Any]
    chart_specifications: Annotated[List[Dict[str, Any]], operator.add]
    styling_preferences: Dict[str, Any]
    generated_html: str
    generated_css: str
    generated_js: str
    generated_code: str
    generated_code_type: str
    insights: Annotated[List[str], operator.add]
    llm_insights: Dict[str, Any]  # NEW: Structured LLM-generated insights
    error_messages: Annotated[List[str], operator.add]
    verification_issues: Annotated[List[str], operator.add]
    verification_report: Dict[str, Any]


class CodeGenerationAgent:
    """Agent responsible for generating dashboard code components"""
    
    def __init__(self):
        self.html_templates = self._load_html_components()
        self.css_frameworks = self._load_css_frameworks()
        self.js_libraries = self._load_js_libraries()
    
    def generate_html_structure(self, layout_config: Dict[str, Any], dashboard_type: str) -> str:
        """Generate HTML structure based on layout configuration"""
        
        # Base HTML structure
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            self._generate_html_head(dashboard_type),
            '<body>',
            self._generate_dashboard_container(layout_config, dashboard_type),
            self._generate_script_section(),
            '</body>',
            '</html>'
        ]
        
        return '\n'.join(html_parts)
    
    def _generate_html_head(self, dashboard_type: str) -> str:
        """Generate HTML head section with appropriate meta tags and external resources"""
        title = f"{dashboard_type.replace('_', ' ').title()} Dashboard"
        
        return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI-generated {dashboard_type} dashboard">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {self._generate_embedded_css(dashboard_type)}
    </style>
</head>"""
    
    def _generate_dashboard_container(self, layout_config: Dict[str, Any], dashboard_type: str) -> str:
        """Generate main dashboard container structure"""
        
        sections = layout_config.get("sections", [])
        grid_columns = layout_config.get("grid_structure", {}).get("columns", 2)
        
        container_html = [
            f'<div class="dashboard-container dashboard-{dashboard_type}">',
            self._generate_header_section(dashboard_type),
            f'<div class="dashboard-grid" style="grid-template-columns: repeat({grid_columns}, 1fr);">'
        ]
        
        # Generate sections based on layout
        for i, section in enumerate(sections):
            container_html.append(self._generate_section_html(section, i))
        
        # Ensure an insights panel exists at the bottom if layout did not include one
        has_insights = any((sec.get("id") == "insights_panel" or sec.get("type") == "insights_panel") for sec in sections)
        if not has_insights:
            container_html.append(self._generate_insights_section("insights_panel", "", "height-compact"))
        
        container_html.extend([
            '</div>',  # Close dashboard-grid
            self._generate_footer_section(),
            '</div>'   # Close dashboard-container
        ])
        
        return '\n'.join(container_html)
    
    def _generate_header_section(self, dashboard_type: str) -> str:
        """Generate dashboard header with title and metadata"""
        title = dashboard_type.replace('_', ' ').title()
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        return f"""
    <header class="dashboard-header">
        <div class="header-content">
            <h1 class="dashboard-title">{title} Dashboard</h1>
            <p class="dashboard-subtitle">AI-Generated Analysis • {timestamp}</p>
        </div>
        <div class="header-actions">
            <button class="action-btn" onclick="exportDashboard()">
                <span>📊</span> Export
            </button>
            <button class="action-btn" onclick="refreshDashboard()">
                <span>🔄</span> Refresh
            </button>
        </div>
    </header>"""
    
    def _generate_section_html(self, section: Dict[str, Any], index: int) -> str:
        """Generate HTML for individual dashboard section"""
        section_type = section.get("type", "chart")
        section_id = section.get("id", f"section_{index}")
        span_style = self._get_grid_span_style(section.get("span", {}))
        height_class = f"height-{section.get('height', 'standard')}"
        
        # If a section is explicitly named insights_panel by id, treat it as insights regardless of type
        if section_id == "insights_panel":
            return self._generate_insights_section(section_id, span_style, height_class)
        
        if section_type == "kpi_cards":
            return self._generate_kpi_section(section_id, span_style, height_class)
        elif section_type == "chart":
            return self._generate_chart_section(section_id, span_style, height_class, section)
        elif section_type == "insights_panel":
            return self._generate_insights_section(section_id, span_style, height_class)
        else:
            return self._generate_generic_section(section_id, span_style, height_class, section)
    
    def _generate_kpi_section(self, section_id: str, span_style: str, height_class: str) -> str:
        """Generate KPI cards section"""
        return f"""
    <section class="dashboard-section kpi-section {height_class}" style="{span_style}" id="{section_id}">
        <div class="kpi-container" id="{section_id}_container">
            <!-- KPI cards will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _generate_chart_section(self, section_id: str, span_style: str, height_class: str, section: Dict[str, Any]) -> str:
        """Generate chart section"""
        chart_title = section.get("title", "Chart Analysis")
        
        return f"""
    <section class="dashboard-section chart-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">{chart_title}</h3>
            <div class="section-controls">
                <button class="control-btn" onclick="toggleFullscreen('{section_id}')">⛶</button>
            </div>
        </div>
        <div class="chart-container" id="{section_id}">
            <div class="chart-loading">
                <div class="spinner"></div>
                <p>Loading visualization...</p>
            </div>
        </div>
    </section>"""
    
    def _generate_insights_section(self, section_id: str, span_style: str, height_class: str) -> str:
        """Generate insights panel section"""
        return f"""
    <section class="dashboard-section insights-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">🔍 Key Insights</h3>
        </div>
        <div class="insights-content" id="{section_id}">
            <!-- Insights will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _generate_generic_section(self, section_id: str, span_style: str, height_class: str, section: Dict[str, Any]) -> str:
        """Generate generic section"""
        title = section.get("title", "Analysis")
        
        return f"""
    <section class="dashboard-section generic-section {height_class}" style="{span_style}">
        <div class="section-header">
            <h3 class="section-title">{title}</h3>
        </div>
        <div class="section-content" id="{section_id}">
            <!-- Content will be populated by JavaScript -->
        </div>
    </section>"""
    
    def _get_grid_span_style(self, span: Dict[str, Any]) -> str:
        """Convert span configuration to CSS grid style"""
        css_parts = []
        
        if "col" in span:
            css_parts.append(f"grid-column: {span['col']}")
        if "row" in span:
            css_parts.append(f"grid-row: {span['row']}")
        
        return "; ".join(css_parts)
    
    def _generate_footer_section(self) -> str:
        """Generate dashboard footer"""
        return """
    <footer class="dashboard-footer">
        <p>Generated by LangGraph AI Dashboard Builder • 
           <span id="generation-time"></span> • 
           <a href="#" onclick="showDataSources()">Data Sources</a>
        </p>
    </footer>"""
    
    def _generate_script_section(self) -> str:
        """Generate JavaScript section placeholder"""
        return """
    <script>
        // Dashboard JavaScript will be injected here
        document.getElementById('generation-time').textContent = new Date().toLocaleString();
    </script>"""
    
    def _generate_embedded_css(self, dashboard_type: str) -> str:
        """Generate embedded CSS for the dashboard"""
        color_schemes = {
            "executive": {
                "primary": "#1e40af",
                "secondary": "#3b82f6", 
                "accent": "#60a5fa",
                "background": "#f8fafc",
                "surface": "#ffffff",
                "text": "#1f2937"
            },
            "data_quality": {
                "primary": "#059669",
                "secondary": "#10b981",
                "accent": "#34d399",
                "background": "#f0fdf4",
                "surface": "#ffffff",
                "text": "#1f2937"
            },
            "exploratory": {
                "primary": "#7c3aed",
                "secondary": "#8b5cf6",
                "accent": "#a78bfa",
                "background": "#faf5ff",
                "surface": "#ffffff",
                "text": "#1f2937"
            }
        }
        
        colors = color_schemes.get(dashboard_type, color_schemes["exploratory"])
        
        return f"""
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --accent-color: {colors['accent']};
            --background-color: {colors['background']};
            --surface-color: {colors['surface']};
            --text-color: {colors['text']};
            --border-radius: 12px;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            --transition: all 0.3s ease;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
        }}

        .dashboard-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: grid;
            grid-template-rows: auto 1fr auto;
            gap: 20px;
        }}

        .dashboard-header {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 30px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .dashboard-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .dashboard-subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .header-actions {{
            display: flex;
            gap: 10px;
        }}

        .action-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
        }}

        .action-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}

        .dashboard-grid {{
            display: grid;
            gap: 20px;
            grid-auto-rows: minmax(200px, auto);
        }}

        .dashboard-section {{
            background: var(--surface-color);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            border: 1px solid rgba(0, 0, 0, 0.05);
            overflow: hidden;
            transition: var(--transition);
        }}

        .dashboard-section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }}

        .section-header {{
            padding: 20px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .section-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--primary-color);
        }}

        .section-controls {{
            display: flex;
            gap: 8px;
        }}

        .control-btn {{
            background: none;
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: var(--text-color);
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: var(--transition);
        }}

        .control-btn:hover {{
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }}

        .chart-container {{
            padding: 20px;
            height: 100%;
            min-height: 300px;
        }}

        .kpi-container {{
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
            color: white;
            padding: 25px;
            border-radius: var(--border-radius);
            text-align: center;
            transition: var(--transition);
        }}

        .kpi-card:hover {{
            transform: scale(1.05);
        }}

        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .kpi-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}

        .kpi-trend {{
            font-size: 0.9rem;
            margin-top: 10px;
        }}

        .insights-content {{
            padding: 20px;
        }}

        .insight-item {{
            display: flex;
            align-items: flex-start;
            padding: 15px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }}

        .insight-item:last-child {{
            border-bottom: none;
        }}

        .insight-icon {{
            width: 8px;
            height: 8px;
            background: var(--accent-color);
            border-radius: 50%;
            margin-right: 15px;
            margin-top: 8px;
            flex-shrink: 0;
        }}

        .insight-text {{
            flex: 1;
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        .chart-loading {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            color: var(--primary-color);
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .height-small {{
            grid-row: span 1;
        }}

        .height-standard {{
            grid-row: span 2;
        }}

        .height-large {{
            grid-row: span 3;
        }}

        .height-compact {{
            grid-row: span 1;
            min-height: 120px;
        }}

        .dashboard-footer {{
            text-align: center;
            padding: 20px;
            color: rgba(0, 0, 0, 0.6);
            font-size: 0.9rem;
        }}

        .dashboard-footer a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        .dashboard-footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr !important;
            }}
            
            .dashboard-header {{
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }}
            
            .dashboard-title {{
                font-size: 2rem;
            }}
        }}
        """
    
    def generate_javascript_code(self, chart_configs: List[Dict[str, Any]], insights: List[str], json_data: Dict[str, Any]) -> str:
        """Generate JavaScript code for dashboard functionality"""
        
        # Custom JSON encoder to handle NumPy types
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)
        
        js_code = f"""
// Dashboard Data and Configuration
const dashboardData = {json.dumps(json_data, indent=2, cls=NumpyEncoder)};
const chartConfigs = {json.dumps(chart_configs, indent=2, cls=NumpyEncoder)};
const insights = {json.dumps(insights, indent=2)};

// Shared color palette to keep charts vivid and consistent
const chartPalette = ['#1e3a8a', '#2563eb', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
const borderColor = '#0f172a';

function pickColor(index) {{
    return chartPalette[index % chartPalette.length];
}}

// Ensure we have enough varied charts; auto-derive extras when the incoming spec is sparse
if (chartConfigs.length < 4) {{
    const numericalColumns = dashboardData.metadata?.data_types?.numerical_columns || [];
    const categoricalColumns = dashboardData.metadata?.data_types?.categorical_columns || [];
    const derived = [];

    if (numericalColumns.length >= 1) {{
        derived.push({{
            id: `auto_hist_${{chartConfigs.length + derived.length}}`,
            type: 'histogram',
            columns: [numericalColumns[0]],
            title: 'Distribution Overview'
        }});
    }}

    if (numericalColumns.length >= 2) {{
        derived.push({{
            id: `auto_scatter_${{chartConfigs.length + derived.length}}`,
            type: 'scatter',
            columns: [numericalColumns[0], numericalColumns[1]],
            title: 'Numeric Relationship'
        }});
    }}

    if (categoricalColumns.length >= 1) {{
        derived.push({{
            id: `auto_bar_${{chartConfigs.length + derived.length}}`,
            type: 'bar_chart',
            columns: [categoricalColumns[0]],
            title: 'Category Breakdown'
        }});
    }}

    if (numericalColumns.length >= 3) {{
        derived.push({{
            id: `auto_heatmap_${{chartConfigs.length + derived.length}}`,
            type: 'heatmap',
            columns: numericalColumns.slice(0, 5),
            title: 'Correlation Matrix'
        }});
    }}

    derived.slice(0, 4 - chartConfigs.length).forEach(cfg => chartConfigs.push(cfg));
}}

// Dashboard Initialization
document.addEventListener('DOMContentLoaded', function() {{
    initializeDashboard();
}});

function initializeDashboard() {{
    renderKPICards();
    renderCharts();
    renderInsights();
    setupEventListeners();
}}

// KPI Card Rendering
function renderKPICards() {{
    const kpiContainer = document.querySelector('.kpi-container');
    if (!kpiContainer) return;
    
    const kpiData = extractKPIData();
    kpiContainer.innerHTML = '';
    
    kpiData.forEach(kpi => {{
        const kpiCard = createKPICard(kpi);
        kpiContainer.appendChild(kpiCard);
    }});
}}

function extractKPIData() {{
    // Extract KPI data from dashboard data
    const numericalColumns = dashboardData.metadata?.data_types?.numerical_columns || [];
    const data = dashboardData.data?.records || [];
    
    return numericalColumns.slice(0, 4).map(col => {{
        const values = data.map(row => row[col]).filter(val => val != null);
        const total = values.reduce((sum, val) => sum + val, 0);
        const avg = values.length > 0 ? total / values.length : 0;
        
        return {{
            label: col.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()),
            value: total,
            average: avg,
            trend: Math.random() > 0.5 ? 'up' : 'down',
            trendPercent: (Math.random() * 20 - 10).toFixed(1)
        }};
    }});
}}

function createKPICard(kpi) {{
    const card = document.createElement('div');
    card.className = 'kpi-card';
    
    const trendIcon = kpi.trend === 'up' ? '↗️' : '↘️';
    const trendColor = kpi.trend === 'up' ? '#10b981' : '#ef4444';
    
    card.innerHTML = `
        <div class="kpi-value">${{formatNumber(kpi.value)}}</div>
        <div class="kpi-label">${{kpi.label}}</div>
        <div class="kpi-trend" style="color: ${{trendColor}}">
            ${{trendIcon}} ${{kpi.trendPercent}}%
        </div>
    `;
    
    return card;
}}

// Chart Rendering
function renderCharts() {{
    // First try to match by exact IDs
    const renderedElements = new Set();
    
    chartConfigs.forEach((config, index) => {{
        let chartElement = null;
        
        // Try exact ID match first
        if (config.id) {{
            chartElement = document.getElementById(config.id);
        }}
        
        // If no match and ID doesn't exist, try backup ID patterns
        if (!chartElement && config.id) {{
            const fallbackIds = [config.id, `chart_${{index}}`, `section_${{index}}`];
            for (const id of fallbackIds) {{
                const el = document.getElementById(id);
                if (el && !renderedElements.has(el)) {{
                    chartElement = el;
                    break;
                }}
            }}
        }}
        
        if (chartElement) {{
            config._colorIndex = index;
            renderChart(chartElement, config, index);
            renderedElements.add(chartElement);
        }} else {{
            console.warn(`No element found for chart:`, config);
        }}
    }});
    
    // For any remaining empty chart containers, try sequential matching
    const allChartContainers = document.querySelectorAll('.chart-container');
    let configIndex = 0;
    allChartContainers.forEach(container => {{
        if (!renderedElements.has(container) && container.children.length === 0 && configIndex < chartConfigs.length) {{
            chartConfigs[configIndex]._colorIndex = configIndex;
            renderChart(container, chartConfigs[configIndex], configIndex);
            configIndex++;
        }}
    }});
}}

function renderChart(element, config, index = 0) {{
    // Remove loading spinner
    element.innerHTML = '';
    const colorIndex = config?._colorIndex != null ? config._colorIndex : index;
    config._colorIndex = colorIndex;
    
    try {{
        if (config.type === 'histogram') {{
            renderHistogram(element, config);
        }} else if (config.type === 'scatter') {{
            renderScatter(element, config);
        }} else if (config.type === 'bar_chart') {{
            renderBarChart(element, config);
        }} else if (config.type === 'heatmap') {{
            renderHeatmap(element, config);
        }} else if (config.type === 'line_chart') {{
            renderLineChart(element, config);
        }} else if (config.type === 'gauge_chart') {{
            renderGaugeChart(element, config);
        }} else if (config.type === 'kpi_card') {{
            renderKPICard(element, config);
        }} else {{
            renderDefaultChart(element, config);
        }}
    }} catch (error) {{
        console.error('Error rendering chart:', error);
        element.innerHTML = '<div class="error-message">Error loading chart</div>';
    }}
}}

function renderHistogram(element, config) {{
    // Use provided data if available, otherwise extract from dashboardData
    let data;
    if (config.config?.x) {{
        data = config.config.x;
    }} else {{
        data = extractColumnData(config.columns?.[0] || Object.keys(dashboardData.data?.by_column || {{}})[0]);
    }}
    
    const trace = {{
        x: data,
        type: 'histogram',
        name: config.config?.title || config.title || 'Distribution',
        marker: {{
            color: config.config?.color || config.color || pickColor(config._colorIndex || 0),
            line: {{ color: borderColor, width: 1.2 }}
        }},
        nbinsx: config.config?.bins || 30
    }};
    
    const layout = {{
        title: config.config?.title || config.title || 'Distribution Analysis',
        xaxis: {{ title: config.columns?.[0] || 'Value' }},
        yaxis: {{ title: 'Frequency' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderScatter(element, config) {{
    // Use provided data if available
    let xData, yData;
    if (config.config?.x && config.config?.y) {{
        xData = config.config.x;
        yData = config.config.y;
    }} else {{
        xData = extractColumnData(config.columns?.[0]);
        yData = extractColumnData(config.columns?.[1]);
    }}
    
    const trace = {{
        x: xData,
        y: yData,
        mode: 'markers',
        type: 'scatter',
        name: config.config?.title || config.title || 'Scatter Plot',
        marker: {{ 
            color: config.config?.color || config.color || pickColor(config._colorIndex || 0),
            size: config.config?.size || 8,
            opacity: 0.75,
            line: {{ color: borderColor, width: 1 }}
        }}
    }};
    
    const layout = {{
        title: config.config?.title || config.title || 'Scatter Plot Analysis',
        xaxis: {{ title: config.columns?.[0] || 'X' }},
        yaxis: {{ title: config.columns?.[1] || 'Y' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderBarChart(element, config) {{
    // Use provided data if available
    let xData, yData;
    if (config.config?.x && config.config?.y) {{
        xData = config.config.x;
        yData = config.config.y;
    }} else {{
        const data = extractColumnData(config.columns?.[0]);
        const valueCounts = getValueCounts(data);
        xData = Object.keys(valueCounts);
        yData = Object.values(valueCounts);
    }}
    
    const barColors = xData.map((_, idx) => pickColor(idx));
    const trace = {{
        x: xData,
        y: yData,
        type: 'bar',
        name: config.config?.title || config.title || 'Bar Chart',
        marker: {{
            color: config.config?.color || config.color || barColors,
            line: {{ color: borderColor, width: 1.2 }}
        }}
    }};
    
    const layout = {{
        title: config.config?.title || config.title || 'Bar Chart Analysis',
        xaxis: {{ title: config.columns?.[0] || 'Category' }},
        yaxis: {{ title: 'Count' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderHeatmap(element, config) {{
    const numericalColumns = dashboardData.metadata?.data_types?.numerical_columns || [];
    const correlationMatrix = calculateCorrelationMatrix(numericalColumns);
    
    const trace = {{
        z: correlationMatrix.values,
        x: correlationMatrix.columns,
        y: correlationMatrix.columns,
        type: 'heatmap',
        colorscale: 'RdBu',
        zmid: 0,
        showscale: true
    }};
    
    const layout = {{
        title: 'Correlation Matrix',
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderLineChart(element, config) {{
    // Use provided data if available
    let xData, yData;
    if (config.config?.x && config.config?.y) {{
        xData = config.config.x;
        yData = config.config.y;
    }} else {{
        yData = extractColumnData(config.columns?.[0]);
        xData = Array.from({{length: yData.length}}, (_, i) => i);
    }}
    
    const seriesColor = config.config?.color || config.color || pickColor(config._colorIndex || 0);
    const trace = {{
        x: xData,
        y: yData,
        type: 'scatter',
        mode: 'lines+markers',
        name: config.config?.title || config.title || 'Trend',
        line: {{ color: seriesColor, width: 3 }},
        marker: {{ size: 7, color: seriesColor, line: {{ color: borderColor, width: 1.2 }} }}
    }};
    
    const layout = {{
        title: config.config?.title || config.title || 'Trend Analysis',
        xaxis: {{ title: 'Index' }},
        yaxis: {{ title: config.columns?.[0] || 'Value' }},
        margin: {{ t: 40, r: 30, b: 40, l: 60 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)'
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderGaugeChart(element, config) {{
    // Gauge chart using Plotly indicator
    const value = config.config?.value || 0;
    const maxValue = config.config?.max_value || 100;
    const title = config.config?.title || config.title || 'Performance';
    
    const trace = {{
        type: 'indicator',
        mode: 'gauge+number',
        value: value,
        title: {{ text: title }},
        gauge: {{
            axis: {{ range: [0, maxValue] }},
            bar: {{ color: config.config?.color || '#059669' }},
            steps: config.config?.thresholds ? [
                {{ range: [0, config.config.thresholds[0]], color: '#dc2626' }},
                {{ range: [config.config.thresholds[0], config.config.thresholds[1]], color: '#d97706' }},
                {{ range: [config.config.thresholds[1], maxValue], color: '#059669' }}
            ] : [],
            threshold: {{
                line: {{ color: '#1e40af', width: 4 }},
                thickness: 0.75,
                value: value
            }}
        }}
    }};
    
    const layout = {{
        margin: {{ t: 40, r: 30, b: 40, l: 30 }},
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: {{ color: '#374151' }}
    }};
    
    Plotly.newPlot(element, [trace], layout, {{responsive: true}});
}}

function renderKPICard(element, config) {{
    // KPI card HTML rendering
    const value = config.config?.value || 0;
    const title = config.config?.title || 'KPI';
    const trend = config.config?.trend || 'neutral';
    const trendPercent = config.config?.trend_percent || 0;
    const color = config.config?.color || '#3b82f6';
    
    const trendIcon = trend === 'up' ? '↗️' : trend === 'down' ? '↘️' : '→';
    const trendColor = trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#6b7280';
    
    element.innerHTML = `
        <div class="kpi-card-content" style="padding: 20px; text-align: center;">
            <div class="kpi-value" style="font-size: 32px; font-weight: bold; color: ${{color}};">
                ${{formatNumber(value)}}
            </div>
            <div class="kpi-label" style="font-size: 14px; color: #6b7280; margin-top: 8px;">
                ${{title}}
            </div>
            <div class="kpi-trend" style="font-size: 12px; color: ${{trendColor}}; margin-top: 8px;">
                ${{trendIcon}} ${{trendPercent}}%
            </div>
        </div>
    `;
}}

function renderDefaultChart(element, config) {{
    element.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #6b7280;">
            <h3>Chart Type: ${{config.type}}</h3>
            <p>Visualization will be rendered here</p>
        </div>
    `;
}}

// Insights Rendering
function renderInsights() {{
    const insightsContainer = document.querySelector('.insights-content');
    if (!insightsContainer) return;
    
    insightsContainer.innerHTML = '';
    
    insights.forEach(insight => {{
        const insightElement = createInsightElement(insight);
        insightsContainer.appendChild(insightElement);
    }});
}}

function createInsightElement(insight) {{
    const element = document.createElement('div');
    element.className = 'insight-item';
    element.innerHTML = `
        <div class="insight-icon"></div>
        <div class="insight-text">${{insight}}</div>
    `;
    return element;
}}

// Utility Functions
function extractColumnData(columnName) {{
    if (!columnName || !dashboardData.data) return [];
    
    if (dashboardData.data.by_column && dashboardData.data.by_column[columnName]) {{
        return dashboardData.data.by_column[columnName].filter(val => val != null);
    }}
    
    if (dashboardData.data.records) {{
        return dashboardData.data.records
            .map(record => record[columnName])
            .filter(val => val != null);
    }}
    
    return [];
}}

function getValueCounts(data) {{
    const counts = {{}};
    data.forEach(value => {{
        counts[value] = (counts[value] || 0) + 1;
    }});
    return counts;
}}

function calculateCorrelationMatrix(columns) {{
    const matrix = [];
    const size = columns.length;
    
    for (let i = 0; i < size; i++) {{
        const row = [];
        for (let j = 0; j < size; j++) {{
            if (i === j) {{
                row.push(1);
            }} else {{
                const corr = calculateCorrelation(
                    extractColumnData(columns[i]),
                    extractColumnData(columns[j])
                );
                row.push(corr);
            }}
        }}
        matrix.push(row);
    }}
    
    return {{ values: matrix, columns: columns }};
}}

function calculateCorrelation(x, y) {{
    if (x.length !== y.length || x.length === 0) return 0;
    
    const n = x.length;
    const meanX = x.reduce((sum, val) => sum + val, 0) / n;
    const meanY = y.reduce((sum, val) => sum + val, 0) / n;
    
    let numerator = 0;
    let sumXSquared = 0;
    let sumYSquared = 0;
    
    for (let i = 0; i < n; i++) {{
        const xDiff = x[i] - meanX;
        const yDiff = y[i] - meanY;
        numerator += xDiff * yDiff;
        sumXSquared += xDiff * xDiff;
        sumYSquared += yDiff * yDiff;
    }}
    
    const denominator = Math.sqrt(sumXSquared * sumYSquared);
    return denominator === 0 ? 0 : numerator / denominator;
}}

function formatNumber(num) {{
    if (num >= 1000000) {{
        return (num / 1000000).toFixed(1) + 'M';
    }} else if (num >= 1000) {{
        return (num / 1000).toFixed(1) + 'K';
    }} else {{
        return num.toFixed(0);
    }}
}}

// Event Handlers
function setupEventListeners() {{
    // Make charts responsive
    window.addEventListener('resize', function() {{
        const charts = document.querySelectorAll('.chart-container [id]');
        charts.forEach(chart => {{
            if (chart.id && window.Plotly) {{
                Plotly.Plots.resize(chart.id);
            }}
        }});
    }});
}}

function exportDashboard() {{
    // Create export functionality
    const dashboardHTML = document.documentElement.outerHTML;
    const blob = new Blob([dashboardHTML], {{ type: 'text/html' }});
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dashboard.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}}

function refreshDashboard() {{
    location.reload();
}}

function toggleFullscreen(elementId) {{
    const element = document.getElementById(elementId);
    if (element) {{
        if (document.fullscreenElement) {{
            document.exitFullscreen();
        }} else {{
            element.requestFullscreen();
        }}
    }}
}}

function showDataSources() {{
    alert('Data source information:\\n' + JSON.stringify(dashboardData.metadata, null, 2));
}}
"""
        
        return js_code
    
    def _load_html_components(self) -> Dict[str, str]:
        """Load reusable HTML components"""
        return {
            "kpi_card": """
                <div class="kpi-card">
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-trend">{trend}</div>
                </div>
            """,
            "chart_container": """
                <div class="chart-container" id="{id}">
                    <div class="chart-loading">Loading...</div>
                </div>
            """
        }
    
    def _load_css_frameworks(self) -> Dict[str, str]:
        """Load CSS framework configurations"""
        return {
            "modern": "Modern design with cards and gradients",
            "minimal": "Clean minimal design",
            "corporate": "Professional corporate styling"
        }
    
    def _load_js_libraries(self) -> Dict[str, str]:
        """Load JavaScript library configurations"""
        return {
            "plotly": "Plotly.js for interactive charts",
            "d3": "D3.js for custom visualizations",
            "chart_js": "Chart.js for simple charts"
        }


class LangGraphDashboardBuilder:
    """Main LangGraph-powered dashboard builder"""
    
    def __init__(self):
        self.agent_orchestrator = LangGraphAgentOrchestrator()
        self.code_generator = CodeGenerationAgent()
        self.csv_converter = CSVToJSONConverter()
        
        # Initialize LLM Insights Engine
        try:
            self.insights_engine = LLMInsightsEngine()
            self.use_llm_insights = True
        except Exception as e:
            print(f"Warning: LLM Insights Engine not available: {e}")
            self.insights_engine = None
            self.use_llm_insights = False
        
        # Initialize response cache for LLM calls (max 100 entries with TTL)
        self.llm_response_cache = {}
        self.max_cache_size = 100
        
        self.dashboard_graph = self._create_dashboard_workflow()
    
    def _wrap_node(self, fn, node_name: str):
        """Wrap a node function to ensure it always returns at least one valid state update.

        - Catches exceptions and reports them via error_messages
        - Ensures a non-empty update for LangGraph (adds a minimal 'insights' message if needed)
        - Logs returned keys for easier debugging
        """
        allowed_keys = set(DashboardGenerationState.__annotations__.keys())

        def wrapper(state: DashboardGenerationState) -> DashboardGenerationState:
            try:
                update = fn(state)
                if update is None:
                    update = {}
                if not isinstance(update, dict):
                    # If a non-dict was returned, convert to an error update
                    logger.warning(f"Node {node_name} returned non-dict update: {type(update)}")
                    update = {}
            except Exception as e:
                logger.exception(f"Node {node_name} raised an exception: {e}")
                return {"error_messages": [f"{node_name} failed: {str(e)}"]}

            # If update doesn't include any allowed keys, add a minimal insights update to satisfy LangGraph
            if not any(k in allowed_keys for k in update.keys()):
                logger.warning(f"Node {node_name} produced empty or invalid update; injecting minimal fallback update")
                update = {**({} if isinstance(update, dict) else {}),
                          "insights": [f"Node '{node_name}' produced no updates; continuing workflow."]}

            try:
                logger.debug(f"Node {node_name} update keys: {list(update.keys())}")
            except Exception:
                # Avoid any logging-related errors from unusual types
                pass

            return update  # type: ignore

        return wrapper

    def _create_dashboard_workflow(self) -> StateGraph:
        """Create the complete dashboard generation workflow"""
        graph = StateGraph(DashboardGenerationState)
        
        # Add workflow nodes
        graph.add_node("initialize_session", self._wrap_node(self._initialize_session, "initialize_session"))
        graph.add_node("convert_data_to_json", self._wrap_node(self._convert_data_to_json, "convert_data_to_json"))
        graph.add_node("analyze_dashboard_requirements", self._wrap_node(self._analyze_requirements, "analyze_dashboard_requirements"))
        graph.add_node("generate_layout_structure", self._wrap_node(self._generate_layout, "generate_layout_structure"))
        graph.add_node("create_chart_specifications", self._wrap_node(self._create_charts, "create_chart_specifications"))
        graph.add_node("generate_insights", self._wrap_node(self._generate_insights, "generate_insights"))
        graph.add_node("generate_llm_insights", self._wrap_node(self._generate_llm_insights, "generate_llm_insights"))  # NEW: LLM-powered insights
        # New nodes: generate code via LLM and verify it
        graph.add_node("generate_code_via_llm", self._wrap_node(self._generate_code_via_llm, "generate_code_via_llm"))
        graph.add_node("verify_generated_code", self._wrap_node(self._verify_generated_code, "verify_generated_code"))
        graph.add_node("finalize_dashboard", self._wrap_node(self._finalize_dashboard, "finalize_dashboard"))
        
        # Define workflow edges
        graph.set_entry_point("initialize_session")
        graph.add_edge("initialize_session", "convert_data_to_json")
        graph.add_edge("convert_data_to_json", "analyze_dashboard_requirements")
        graph.add_edge("analyze_dashboard_requirements", "generate_layout_structure")
        graph.add_edge("generate_layout_structure", "create_chart_specifications")
        graph.add_edge("create_chart_specifications", "generate_insights")
        graph.add_edge("generate_insights", "generate_llm_insights")  # NEW: Add LLM insights
        # generate code (JSX/HTML/JS) using an LLM-driven generator node, then verify
        graph.add_edge("generate_llm_insights", "generate_code_via_llm")
        graph.add_edge("generate_code_via_llm", "verify_generated_code")
        graph.add_edge("verify_generated_code", "finalize_dashboard")
        graph.add_edge("finalize_dashboard", END)
        
        return graph.compile()
    
    # Workflow node implementations
    def _initialize_session(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Initialize dashboard generation session"""
        session_id = uuid.uuid4().hex
        return {"session_id": session_id}
    
    def _convert_data_to_json(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Convert DataFrame to optimized JSON format"""
        df = state["df"]
        # Avoid calling CSV converter with invalid path; use orchestrator's converter directly
        try:
            json_data = self.agent_orchestrator.data_tools.convert_to_json_structure(df)
        except Exception as e:
            # Fallback to a minimal JSON structure to keep workflow moving
            logger.warning(f"convert_to_json_structure failed: {e}; using minimal JSON structure")
            json_data = {
                "metadata": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "created_at": datetime.now().isoformat(),
                },
                "columns": df.columns.tolist(),
                "data": df.head(1000).to_dict("records") if hasattr(df, "to_dict") else [],
            }
        
        return {"json_data": json_data}
    
    def _analyze_requirements(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Analyze dashboard requirements based on data and user input"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        user_context = state.get("user_context", "")
        
        # Get appropriate tool for dashboard type
        tool_class = DashboardToolFactory.get_tool(dashboard_type)
        
        if dashboard_type == "executive":
            analysis = tool_class.analyze_business_metrics(df, user_context)
        elif dashboard_type == "data_quality":
            analysis = tool_class.analyze_data_quality_comprehensive(df)
        elif dashboard_type == "exploratory":
            analysis = tool_class.analyze_data_patterns(df)
        else:
            analysis = {"type": dashboard_type, "basic_analysis": "completed"}
        
        # Determine layout requirements
        if hasattr(tool_class, 'generate_executive_layout'):
            layout_requirements = tool_class.generate_executive_layout()
        else:
            layout_requirements = self.agent_orchestrator.dashboard_tools.generate_dashboard_layout(
                dashboard_type, len(df.columns)
            )
        
        return {"layout_requirements": layout_requirements, "data_analysis": analysis}
    
    def _generate_layout(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate optimal layout structure"""
        layout_requirements = state.get("layout_requirements", {})
        
        # Re-emit layout requirements to satisfy LangGraph's requirement that each node updates state
        return {"layout_requirements": layout_requirements}
    
    def _create_charts(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Create chart specifications"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        # Get appropriate tool and create charts
        tool_class = DashboardToolFactory.get_tool(dashboard_type)
        
        if hasattr(tool_class, 'create_executive_charts'):
            # Use the stored data_analysis (which contains metrics with 'kpis')
            data_analysis = state.get("data_analysis", {})
            charts = tool_class.create_executive_charts(df, data_analysis)
        elif hasattr(tool_class, 'create_quality_charts'):
            data_analysis = state.get("data_analysis", tool_class.analyze_data_quality_comprehensive(df))
            charts = tool_class.create_quality_charts(df, data_analysis)
        elif hasattr(tool_class, 'create_exploratory_charts'):
            data_analysis = state.get("data_analysis", tool_class.analyze_data_patterns(df))
            charts = tool_class.create_exploratory_charts(df, data_analysis)
        else:
            # Fallback to general chart suggestions
            charts = self.agent_orchestrator.dashboard_tools.suggest_chart_types(df, dashboard_type)
        
        # With operator.add, return only new charts
        return {"chart_specifications": charts}
    
    def _generate_insights(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate insights for the dashboard"""
        df = state["df"]
        dashboard_type = state.get("dashboard_type", "exploratory")
        
        # Generate insights based on dashboard type
        new_insights = [
            f"Dashboard generated for {len(df)} records across {len(df.columns)} variables",
            f"Analysis type: {dashboard_type.replace('_', ' ').title()}",
            f"Data completeness: {((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100):.1f}%"
        ]
        
        # Add type-specific insights
        if dashboard_type == "executive":
            new_insights.extend([
                "Key performance indicators identified and prioritized",
                "Business metrics configured for executive review"
            ])
        elif dashboard_type == "data_quality":
            missing_percent = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            new_insights.extend([
                f"Data quality assessment completed",
                f"Missing data: {missing_percent:.1f}% of total values"
            ])
        
        # With operator.add, return only new insights - they'll be added to existing
        return {"insights": new_insights}
    
    def _generate_llm_insights(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate comprehensive insights using LLM analysis"""
        if not self.use_llm_insights or not self.insights_engine:
            # Ensure this node updates at least one field to comply with LangGraph
            return {"insights": ["Advanced LLM insights unavailable; showing baseline insights."]}
        
        try:
            df = state["df"]
            dashboard_type = state.get("dashboard_type", "exploratory")
            chart_specs = state.get("chart_specifications", [])
            data_analysis = state.get("data_analysis", {})
            user_context = state.get("user_context")
            
            # Generate comprehensive LLM insights
            llm_insights = self.insights_engine.analyze_dashboard(
                df=df,
                dashboard_type=dashboard_type,
                chart_specs=chart_specs,
                data_analysis=data_analysis,
                user_context=user_context
            )
            
            # Convert structured insights to readable summary points
            insight_summary = generate_insights_summary(llm_insights)
            
            # Add summary points to the insights list (these will show in the dashboard)
            return {
                "llm_insights": llm_insights,  # Full structured insights
                "insights": insight_summary     # Summary points for display
            }
            
        except Exception as e:
            print(f"Warning: LLM insights generation failed: {e}")
            return {
                "insights": [f"Advanced insights temporarily unavailable"]
            }
    
    def _generate_html(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate HTML code for the dashboard"""
        layout_requirements = state.get("layout_requirements", {})
        dashboard_type = state.get("dashboard_type", "exploratory")
        # Legacy fallback: if LLM not available, use code generator
        html_code = self.code_generator.generate_html_structure(layout_requirements, dashboard_type)

        return {"generated_html": html_code}

    def _get_cache_key(self, prompt: str, backend_name: str) -> str:
        """Generate a cache key from prompt hash and backend name.
        
        Args:
            prompt: The LLM prompt
            backend_name: Name of the LLM backend
            
        Returns:
            Unique cache key
        """
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        return f"{backend_name}:{prompt_hash}"
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Retrieve cached LLM response if available.
        
        Args:
            cache_key: Cache key from _get_cache_key
            
        Returns:
            Cached response or None if not found
        """
        if cache_key in self.llm_response_cache:
            logger.debug(f"Cache hit for key: {cache_key}")
            return self.llm_response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """Store LLM response in cache with size management.
        
        Args:
            cache_key: Cache key from _get_cache_key
            response: LLM response to cache
        """
        # Simple LRU: if cache is full, remove oldest entries
        if len(self.llm_response_cache) >= self.max_cache_size:
            # Remove 25% oldest entries to make room
            remove_count = self.max_cache_size // 4
            for key in list(self.llm_response_cache.keys())[:remove_count]:
                del self.llm_response_cache[key]
            logger.debug(f"Cache cleanup: removed {remove_count} oldest entries")
        
        self.llm_response_cache[cache_key] = response
        logger.debug(f"Cached response for key: {cache_key} (cache size: {len(self.llm_response_cache)})")

    def _safe_invoke_llm(self, llm_backend: Any, prompt: str, backend_name: str) -> Optional[str]:
        """Safely invoke LLM backend with proper error handling and multiple fallback strategies.
        
        Args:
            llm_backend: Initialized LLM backend instance
            prompt: The prompt to send
            backend_name: Name of the backend (for logging)
            
        Returns:
            Response text or None if invocation fails
        """
        if llm_backend is None:
            return None
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, backend_name)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            logger.info(f"[{backend_name}] Using cached response")
            return cached_response
        
        try:
            logger.debug(f"Invoking {backend_name} LLM backend for code generation")
            text = None
            
            # Strategy 1: Try chat model interface with messages
            try:
                if _HumanMessage is not None:
                    logger.debug(f"[{backend_name}] Attempting invoke with HumanMessage")
                    response = llm_backend.invoke([_HumanMessage(content=prompt)])
                    text = response.content if hasattr(response, 'content') else str(response)
                    logger.info(f"[{backend_name}] Successfully generated code via chat interface")
                    # Cache the successful response
                    self._cache_response(cache_key, text)
                    return text
                else:
                    logger.debug(f"[{backend_name}] HumanMessage not available: {_HumanMessage_Import_Error}")
            except (AttributeError, TypeError, ModuleNotFoundError) as e:
                logger.debug(f"[{backend_name}] Chat interface failed: {type(e).__name__}: {e}")
            
            # Strategy 2: Try direct call interface
            try:
                logger.debug(f"[{backend_name}] Attempting direct call interface")
                response = llm_backend(prompt)
                text = response if isinstance(response, str) else str(response)
                logger.info(f"[{backend_name}] Successfully generated code via direct call")
                # Cache the successful response
                self._cache_response(cache_key, text)
                return text
            except (TypeError, AttributeError, ModuleNotFoundError) as e:
                logger.debug(f"[{backend_name}] Direct call failed: {type(e).__name__}: {e}")
            
            # Strategy 3: Try __call__ method explicitly
            try:
                logger.debug(f"[{backend_name}] Attempting __call__ method")
                response = llm_backend.__call__(prompt)
                text = response if isinstance(response, str) else str(response)
                logger.info(f"[{backend_name}] Successfully generated code via __call__")
                # Cache the successful response
                self._cache_response(cache_key, text)
                return text
            except Exception as e:
                logger.debug(f"[{backend_name}] __call__ method failed: {type(e).__name__}: {e}")
            
            # All strategies failed
            logger.warning(f"[{backend_name}] All LLM invocation strategies failed")
            return None
            
        except Exception as e:
            logger.error(f"[{backend_name}] Unexpected error during LLM invocation: {type(e).__name__}: {e}")
            return None

    def _generate_code_via_llm(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate full dashboard code (JSX/HTML + JS) using an LLM.

        The prompt is structured with a clear spec: data summary, layout, chart specs, interactivity
        requirements and a strict output format. If no LLM is available, fall back to
        the deterministic code generator.
        """
        # Assemble context for prompt
        dashboard_type = state.get("dashboard_type", "exploratory")
        layout = state.get("layout_requirements", {})
        charts = state.get("chart_specifications", [])
        insights = state.get("insights", [])
        json_data = state.get("json_data", {})
        
        # Get metadata for prompt context
        metadata = json_data.get("metadata", {})
        columns = json_data.get("columns", [])
        sample_records = json_data.get("data", [])[:5] if json_data.get("data") else []

        # Build a comprehensive, structured prompt for high-quality code generation
        prompt_lines = [
            "# ROLE",
            "You are an expert full-stack engineer specializing in data visualization and dashboard development.",
            f"Generate a production-ready, interactive {dashboard_type.upper()} dashboard.",
            "",
            "# OUTPUT FORMAT",
            "Return ONLY valid code - either:",
            "1. A complete HTML5 file with embedded CSS and JavaScript, OR",
            "2. A React functional component (JSX/TSX)",
            "",
            "If returning JSON-wrapped code, use this EXACT format:",
            '{"type": "html", "code": "<!DOCTYPE html>..."}',
            'OR {"type": "jsx", "code": "import React..."}',
            "",
            "# TECHNICAL REQUIREMENTS",
            "## Charts & Visualization",
            "- Use Plotly.js (CDN: https://cdn.plot.ly/plotly-2.26.0.min.js) for all charts",
            "- Each chart MUST have a unique, deterministic ID (e.g., chart_0, chart_1, ...)",
            "- Implement chart configurations based on the provided chart specifications",
            "- Make all charts fully responsive (use Plotly.Plots.resize on window resize)",
            "- Include proper error handling for chart rendering",
            "",
            "## Layout & Styling",
            f"- Grid layout: {layout.get('grid_structure', {}).get('columns', 2)} columns",
            "- Use CSS Grid or Flexbox for responsive layout",
            "- Color scheme: Modern, professional (primary: #2563eb, accent: #3b82f6)",
            "- Typography: Use Inter or system fonts with proper hierarchy",
            "- Ensure mobile responsiveness (breakpoints at 768px, 1024px)",
            "",
            "## Interactivity",
            "- Add hover effects on cards and charts",
            "- Include export functionality (download dashboard as HTML)",
            "- Add fullscreen toggle for charts",
            "- Implement smooth transitions (300ms ease)",
            "- Use multi-color palettes with visible borders on chart elements for clarity",
            "",
            "## Code Quality",
            "- Write clean, well-commented code",
            "- Use semantic HTML5 elements",
            "- Follow accessibility best practices (ARIA labels, proper contrast)",
            "- Optimize for performance (minimize DOM operations)",
            "- NO placeholder comments like '// Add more charts...' - implement everything",
            "",
            "# DATA CONTEXT",
            f"Dataset: {metadata.get('total_rows', 0)} rows × {metadata.get('total_columns', 0)} columns",
            f"Columns: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}",
            "",
            "# LAYOUT CONFIGURATION",
            json.dumps(layout, indent=2)[:800],
            "",
            "# CHART SPECIFICATIONS",
            "Implement these charts exactly as specified:",
        ]
        
        # Add detailed chart specifications
        for i, chart in enumerate(charts[:6]):  # Limit to 6 charts for prompt size
            chart_desc = [
                f"\n## Chart {i+1}: {chart.get('type', 'unknown').upper()}",
                f"- ID: chart_{i}",
                f"- Container ID: chart_{i}_container",
                f"- Purpose: {chart.get('purpose', 'analysis')}",
                f"- Columns: {', '.join(chart.get('columns', [])[:3])}",
                f"- Priority: {chart.get('priority', 'medium')}",
            ]
            prompt_lines.extend(chart_desc)
        
        prompt_lines.extend([
            "",
            "# INSIGHTS TO DISPLAY",
            "Show these insights in an attractive panel:",
        ])
        
        for insight in insights[:5]:
            prompt_lines.append(f"• {insight}")
        
        prompt_lines.extend([
            "",
            "# IMPLEMENTATION CHECKLIST",
            "✓ Complete HTML structure with proper DOCTYPE",
            "✓ Embedded CSS with modern design system",
            "✓ JavaScript with actual chart rendering logic",
            "✓ Include at least 4-6 varied charts when the data supports it (bar, line, scatter, heatmap, etc.)",
            "✓ KPI cards showing key metrics with trend indicators",
            "✓ Interactive chart containers with Plotly",
            "✓ Insights panel with formatted text",
            "✓ Responsive design for mobile/tablet/desktop",
            "✓ Export and fullscreen functionality",
            "✓ Professional color scheme and typography",
            "✓ No TODO comments or incomplete implementations",
            "",
            "# SAMPLE DATA (for reference)",
            json.dumps(sample_records[:3], indent=2)[:500] if sample_records else "No sample data",
            "",
            "NOW GENERATE THE COMPLETE, PRODUCTION-READY CODE:",
        ])

        prompt = "\n".join(prompt_lines)

        generated_html = ""
        generated_js = ""

        # Try to call an LLM if available and API key is configured
        # Priority: Groq (fast, cost-effective), then OpenAI
        llm_backend = None
        backend_name = None
        try:
            if LCGroq is not None and os.getenv("GROQ_API_KEY"):
                backend_name = "groq"
                groq_model_env = os.getenv("GROQ_MODEL", "")
                groq_model = groq_model_env if groq_model_env else "openai/gpt-oss-120b"
                try:
                    llm_backend = LCGroq(
                        model=groq_model, 
                        temperature=0.1,
                        timeout=30.0
                    )
                    logger.debug("Successfully initialized Groq LLM backend")
                except TypeError as te:
                    # ChatGroq might not support all parameters, try basic initialization
                    logger.warning(f"Groq initialization with timeout failed: {te}, retrying without timeout")
                    llm_backend = LCGroq(
                        model=groq_model,
                        temperature=0.1
                    )
            elif LCOpenAI is not None and os.getenv("OPENAI_API_KEY"):
                backend_name = "openai"
                if _USE_CHAT_MODEL:
                    llm_backend = LCOpenAI(
                        model="gpt-4" if os.getenv("USE_GPT4", "false").lower() == "true" else "gpt-3.5-turbo",
                        temperature=0.1,
                        max_tokens=4000,
                        timeout=30.0
                    )
                else:
                    llm_backend = LCOpenAI(temperature=0.1, max_tokens=4000)
                logger.debug("Successfully initialized OpenAI LLM backend")
            else:
                if LCGroq is None and os.getenv("GROQ_API_KEY"):
                    logger.debug(f"Groq import failed: {_GROQ_IMPORT_ERROR}")
                if LCOpenAI is None and os.getenv("OPENAI_API_KEY"):
                    logger.debug("OpenAI import failed")
        except Exception as e:
            logger.warning(f"Failed initializing LLM backend ({backend_name}): {type(e).__name__}: {e}")

        if llm_backend is not None:
            try:
                logger.info(f"Attempting {backend_name} LLM-based dashboard code generation...")
                # Use the safe invoke helper method
                text = self._safe_invoke_llm(llm_backend, prompt, backend_name)
                
                if text is None:
                    raise RuntimeError(f"LLM backend ({backend_name}) invocation returned None")
                
                logger.info(f"LLM response received, length: {len(text)} chars")
                
                # Try to extract JSON-like {"type":"...","code":"..."}
                start = text.find('{')
                end = text.rfind('}')
                
                if start != -1 and end > start:
                    try:
                        # Try to parse as JSON
                        candidate = json.loads(text[start:end+1])
                        code_type = candidate.get("type", "html")
                        code = candidate.get("code", "")
                        
                        if code and len(code) > 100:
                            logger.info(f"Successfully parsed LLM JSON response: type={code_type}")
                            if code_type == "jsx":
                                return {
                                    **state, 
                                    "generated_html": "", 
                                    "generated_js": "", 
                                    "generated_code_type": "jsx", 
                                    "generated_code": code
                                }
                            else:
                                return {
                                    **state, 
                                    "generated_html": code, 
                                    "generated_js": "", 
                                    "generated_code_type": "html", 
                                    "generated_code": code
                                }
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse LLM response as JSON: {e}")
                
                # Not JSON or invalid: assume raw HTML/JS returned
                text_str = text.strip()
                
                # Check if it looks like HTML
                if "<!DOCTYPE" in text_str or "<html" in text_str.lower():
                    logger.info("LLM returned raw HTML")
                    return {
                        **state, 
                        "generated_html": text_str, 
                        "generated_js": "", 
                        "generated_code_type": "html", 
                        "generated_code": text_str
                    }
                # Check if it looks like JSX/React
                elif ("import React" in text_str or "export default" in text_str or 
                      "const " in text_str and "return (" in text_str):
                    logger.info("LLM returned JSX/React component")
                    return {
                        **state, 
                        "generated_html": "", 
                        "generated_js": text_str, 
                        "generated_code_type": "jsx", 
                        "generated_code": text_str
                    }
                else:
                    logger.warning("LLM response format not recognized, falling back to deterministic generator")
                    
            except Exception as e:
                logger.warning(f"LLM generation failed ({type(e).__name__}): {e}, falling back to deterministic generator")
        else:
            if LCGroq is None and os.getenv("GROQ_API_KEY"):
                logger.debug(f"Groq not available, skipping LLM generation: {_GROQ_IMPORT_ERROR}")
            elif LCOpenAI is None and os.getenv("OPENAI_API_KEY"):
                logger.debug("OpenAI not available, skipping LLM generation")
            else:
                logger.debug("No LLM API keys configured, using deterministic generator")

        # Fallback: deterministic generator
        try:
            html_code = self.code_generator.generate_html_structure(layout, dashboard_type)
            js_code = self.code_generator.generate_javascript_code(charts, insights, json_data)
            # Inject JS placeholder into HTML so finalize step finds it
            final_html = html_code.replace("// Dashboard JavaScript will be injected here", js_code)

            return {"generated_html": final_html, "generated_js": js_code, "generated_code_type": "html", "generated_code": final_html}
        except Exception as e:
            logger.error(f"Fallback code generation failed: {e}")
            return {"generated_html": "", "generated_js": "", "error_messages": [str(e)]}

    def _verify_generated_code(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Verify generated code with comprehensive heuristics and optional LLM-based validation.

        Checks:
        - Basic structure (non-empty, minimum length, proper format)
        - Chart rendering (Plotly presence, chart container IDs)
        - Interactivity (event handlers, functions)
        - Styling (CSS presence, responsiveness)
        - Data integration (data variables, proper structure)
        - If LLM available: semantic code review
        """
        code = state.get("generated_code", state.get("generated_html", "")) or ""
        code_type = state.get("generated_code_type", "html")

        verifications = []
        warnings = []
        passed_checks = []
        
        try:
            # === BASIC STRUCTURE CHECKS ===
            if not code or len(code) < 200:
                verifications.append("CRITICAL: Generated code is empty or too short (< 200 chars)")
            else:
                passed_checks.append("Code length adequate")
            
            # Check for proper document structure
            if code_type == "html":
                if "<!DOCTYPE" not in code and "<html" not in code.lower():
                    verifications.append("CRITICAL: Missing DOCTYPE or HTML tag")
                else:
                    passed_checks.append("Valid HTML structure")
                    
                if "<head>" not in code.lower():
                    warnings.append("Missing <head> section")
                    
                if "<body>" not in code.lower():
                    verifications.append("CRITICAL: Missing <body> tag")
                else:
                    passed_checks.append("Body section present")
                    
            elif code_type == "jsx":
                if "export default" not in code and "export const" not in code:
                    warnings.append("No default export found (JSX component)")
                else:
                    passed_checks.append("JSX export detected")
                    
                if "return (" not in code and "return >" not in code:
                    verifications.append("CRITICAL: No JSX return statement found")
                else:
                    passed_checks.append("JSX return statement present")
            
            # === CHART RENDERING CHECKS ===
            has_plotly = "Plotly" in code or "plotly" in code.lower()
            if not has_plotly:
                verifications.append("CRITICAL: No Plotly library usage detected")
            else:
                passed_checks.append("Plotly library integrated")
                
                # Check for actual chart rendering calls
                if "Plotly.newPlot" in code or "Plotly.react" in code:
                    passed_checks.append("Plotly chart rendering calls present")
                else:
                    warnings.append("Plotly imported but no rendering calls found")

                plot_call_count = code.count("Plotly.newPlot") + code.count("Plotly.react")
                if plot_call_count < 3:
                    warnings.append("Limited chart count detected (Plotly render calls < 3); consider adding more visuals when data allows")
                else:
                    passed_checks.append("Multiple chart render calls detected")
            
            # Check for chart container IDs
            chart_containers = []
            for i in range(10):
                if f"chart_{i}" in code or f"chart-{i}" in code:
                    chart_containers.append(f"chart_{i}")
                    
            if chart_containers:
                passed_checks.append(f"Chart containers found: {', '.join(chart_containers[:3])}")
            else:
                verifications.append("WARNING: No deterministic chart container IDs detected (chart_0, chart_1, ...)")
            
            # === STYLING CHECKS ===
            has_css = "<style>" in code or "styled-components" in code or ".css" in code
            if not has_css and code_type == "html":
                warnings.append("No embedded CSS or style tags found")
            else:
                passed_checks.append("Styling present")
                
            # Check for responsive design
            has_responsive = any(keyword in code.lower() for keyword in [
                "@media", "max-width", "min-width", "responsive", "grid-template-columns"
            ])
            if has_responsive:
                passed_checks.append("Responsive design patterns detected")
            else:
                warnings.append("No obvious responsive design patterns")
            
            # === INTERACTIVITY CHECKS ===
            has_event_handlers = any(keyword in code for keyword in [
                "onclick", "addEventListener", "onClick", "onLoad"
            ])
            if has_event_handlers:
                passed_checks.append("Event handlers present")
            else:
                warnings.append("No event handlers detected (limited interactivity)")
            
            # === DATA INTEGRATION CHECKS ===
            has_data_vars = any(keyword in code for keyword in [
                "data", "dataset", "dashboardData", "chartData"
            ])
            if has_data_vars:
                passed_checks.append("Data variables detected")
            else:
                warnings.append("No obvious data variables found")
            
            # === LLM-BASED SEMANTIC VERIFICATION ===
            llm_review_summary = None
            if LCOpenAI is not None and os.getenv("OPENAI_API_KEY") and len(code) > 100:
                try:
                    logger.info("Running LLM-based code verification...")
                    
                    verifier_prompt = f"""You are a senior code reviewer. Review this {code_type.upper()} dashboard code.

EVALUATION CRITERIA:
1. Chart Integration: Does it properly render interactive charts with Plotly?
2. Data Flow: Are data variables properly defined and used?
3. Responsiveness: Is the layout responsive and mobile-friendly?
4. Interactivity: Are there interactive features (export, fullscreen, hover)?
5. Code Quality: Is the code clean, well-structured, and production-ready?
6. Completeness: Are all required components implemented (no TODOs)?

CODE TO REVIEW (first 4000 chars):
{code[:4000]}

Return ONLY a JSON object in this format:
{{
  "valid": true/false,
  "score": 0-100,
  "issues": ["issue1", "issue2", ...],
  "strengths": ["strength1", "strength2", ...],
  "summary": "Brief overall assessment"
}}"""

                    if _USE_CHAT_MODEL:
                        from langchain.schema import HumanMessage
                        llm = LCOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=500)
                        vresp = llm.invoke([HumanMessage(content=verifier_prompt)])
                        vtext = vresp.content if hasattr(vresp, 'content') else str(vresp)
                    else:
                        llm = LCOpenAI(temperature=0, max_tokens=500)
                        vtext = llm(verifier_prompt)
                    
                    # Parse LLM verification response
                    vjson_start = str(vtext).find('{')
                    vjson_end = str(vtext).rfind('}')
                    
                    if vjson_start != -1 and vjson_end > vjson_start:
                        v = json.loads(str(vtext)[vjson_start:vjson_end+1])
                        llm_review_summary = {
                            "valid": v.get('valid', True),
                            "score": v.get('score', 0),
                            "issues": v.get('issues', []),
                            "strengths": v.get('strengths', []),
                            "summary": v.get('summary', '')
                        }
                        
                        if not v.get('valid', True):
                            verifications.extend([f"LLM REVIEW: {issue}" for issue in v.get('issues', [])[:3]])
                        
                        logger.info(f"LLM verification complete: score={v.get('score', 0)}/100")
                        
                except Exception as e:
                    logger.warning(f"LLM verification failed: {e}")
                    warnings.append(f"LLM verification unavailable: {str(e)[:100]}")

        except Exception as e:
            verifications.append(f"Verification error: {str(e)}")

        # Compile verification report
        verification_report = {
            "critical_issues": [v for v in verifications if "CRITICAL" in v],
            "warnings": warnings,
            "passed_checks": passed_checks,
            "llm_review": llm_review_summary,
            "overall_status": "PASS" if len([v for v in verifications if "CRITICAL" in v]) == 0 else "FAIL"
        }
        
        logger.info(f"Verification complete: {verification_report['overall_status']}, "
                   f"{len(passed_checks)} checks passed, "
                   f"{len(verification_report['critical_issues'])} critical issues, "
                   f"{len(warnings)} warnings")

        return {
            "verification_issues": verifications,
            "verification_report": verification_report
        }
    
    def _generate_javascript(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Generate JavaScript code for dashboard functionality"""
        chart_specifications = state.get("chart_specifications", [])
        insights = state.get("insights", [])
        json_data = state.get("json_data", {})
        
        js_code = self.code_generator.generate_javascript_code(
            chart_specifications, insights, json_data
        )
        
        return {"generated_js": js_code}
    
    def _finalize_dashboard(self, state: DashboardGenerationState) -> DashboardGenerationState:
        """Finalize the dashboard by combining all components"""
        html_code = state.get("generated_html", "")
        js_code = state.get("generated_js", "")
        
        # Inject JavaScript into HTML
        final_html = html_code.replace(
            "// Dashboard JavaScript will be injected here",
            js_code
        )
        
        return {"generated_html": final_html}
    
    # Public API
    async def build_dashboard(
        self,
        df: pd.DataFrame,
        dashboard_type: str = "exploratory",
        user_context: str = "",
        target_audience: str = "analyst"
    ) -> Dict[str, Any]:
        """Build complete dashboard using LangGraph workflow"""
        try:
            initial_state: DashboardGenerationState = {
                "df": df,
                "dashboard_type": dashboard_type,
                "user_context": user_context,
                "target_audience": target_audience
            }
            
            result = self.dashboard_graph.invoke(initial_state)
            
            return {
                "success": True,
                "dashboard_html": result.get("generated_html", ""),
                "session_id": result.get("session_id", ""),
                "dashboard_type": dashboard_type,
                "json_data": result.get("json_data", {}),
                "chart_specifications": result.get("chart_specifications", []),
                "insights": result.get("insights", []),
                "llm_insights": result.get("llm_insights", {}),  # NEW: Include LLM insights
                "layout_config": result.get("layout_requirements", {}),
                "generation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error building dashboard: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_type": dashboard_type
            }
