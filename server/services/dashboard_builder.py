import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from jinja2 import Template, Environment, BaseLoader
import asyncio
import uuid

from .chart_generator import ChartGenerator
from .data_processor import DataProcessor
from .ai_agent import AIAgent

# Set up logger
logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


class DashboardBuilder:
    """MCP-based automated dashboard builder"""

    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.data_processor = DataProcessor()
        self.ai_agent = AIAgent()
        self.dashboard_templates = self._load_dashboard_templates()
        self.dashboard_storage = {}  # In-memory storage for dashboards

    def _load_dashboard_templates(self) -> Dict[str, str]:
        """Load dashboard templates for different use cases"""
        return {
            "interactive_dashboard": """
<!DOCTYPE html>
<html>
<head>
    <title>{{dataset_name}} - Interactive Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; }
        
        .dashboard-container { 
            display: grid; 
            grid-template-rows: auto auto 1fr; 
            height: 100vh; 
            max-width: 1600px; 
            margin: 0 auto; 
            padding: 10px;
        }
        
        /* Header */
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 2.2em; margin-bottom: 5px; }
        .header .subtitle { opacity: 0.9; font-size: 1.1em; }
        
        /* Filters Panel */
        .filters-panel { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filters-row { 
            display: flex; 
            gap: 20px; 
            align-items: center; 
            flex-wrap: wrap;
        }
        .filter-group { 
            display: flex; 
            flex-direction: column; 
            min-width: 150px;
        }
        .filter-label { 
            font-weight: 600; 
            margin-bottom: 5px; 
            color: #2c3e50;
        }
        .filter-control { 
            padding: 8px 12px; 
            border: 2px solid #e1e8ed; 
            border-radius: 8px; 
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .filter-control:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .filter-button { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: 600;
            transition: background-color 0.3s;
        }
        .filter-button:hover { background: #5a6fd8; }
        
        /* Main Dashboard Grid */
        .dashboard-grid { 
            display: grid; 
            grid-template-columns: 1fr 2fr 1fr; 
            grid-template-rows: auto 1fr 1fr; 
            gap: 15px; 
            height: 100%;
        }
        
        /* KPI Cards */
        .kpi-section { 
            grid-column: 1 / -1; 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px;
        }
        .kpi-card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .kpi-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .kpi-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #2c3e50; 
            margin: 10px 0;
        }
        .kpi-label { 
            color: #7f8c8d; 
            font-weight: 600;
            font-size: 1.1em;
        }
        .kpi-change { 
            font-size: 0.9em; 
            margin-top: 5px;
        }
        .kpi-change.positive { color: #27ae60; }
        .kpi-change.negative { color: #e74c3c; }
        
        /* Chart Containers */
        .chart-container { 
            background: white; 
            border-radius: 12px; 
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chart-title { 
            font-size: 1.2em; 
            font-weight: 600; 
            color: #2c3e50; 
            margin-bottom: 15px;
            border-bottom: 2px solid #f8f9fa;
            padding-bottom: 10px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .dashboard-grid { 
                grid-template-columns: 1fr 1fr; 
                grid-template-rows: auto repeat(3, 1fr);
            }
        }
        @media (max-width: 768px) {
            .dashboard-grid { 
                grid-template-columns: 1fr; 
                grid-template-rows: auto repeat(6, 300px);
            }
            .filters-row { flex-direction: column; align-items: stretch; }
        }
        
        /* Loading Spinner */
        .loading { 
            display: none; 
            text-align: center; 
            padding: 20px;
        }
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #667eea; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="header">
            <h1>{{dataset_name}}</h1>
            <div class="subtitle">Interactive Analytics Dashboard • Last Updated: {{date}}</div>
        </div>
        
        <!-- Filters Panel -->
        <div class="filters-panel">
            <div class="filters-row">
                <div class="filter-group" id="dateFilterGroup" style="display: none;">
                    <label class="filter-label">Date Range</label>
                    <select id="dateFilter" class="filter-control">
                        <option value="all">All Time</option>
                    </select>
                </div>
                
                <div class="filter-group" id="categoryFilterGroup" style="display: none;">
                    <label class="filter-label">Category</label>
                    <select id="categoryFilter" class="filter-control">
                        <option value="all">All Categories</option>
                    </select>
                </div>
                
                <div class="filter-group" id="numericFilterGroup" style="display: none;">
                    <label class="filter-label">Value Range</label>
                    <select id="numericFilter" class="filter-control">
                        <option value="all">All Values</option>
                    </select>
                </div>
                
                <button class="filter-button" onclick="resetFilters()">Reset Filters</button>
                <button class="filter-button" onclick="refreshData()">Refresh</button>
            </div>
        </div>
        
        <!-- Main Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- KPI Cards -->
            <div class="kpi-section">
                {% for kpi in kpi_metrics %}
                <div class="kpi-card">
                    <div class="kpi-label">{{kpi.label}}</div>
                    <div class="kpi-value" id="kpi_{{loop.index}}">{{kpi.value}}</div>
                    {% if kpi.change %}
                    <div class="kpi-change {{kpi.change_class}}" id="kpi_change_{{loop.index}}">{{kpi.change}}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            
            <!-- Chart 1: Main Trend/Time Series -->
            <div class="chart-container">
                <div class="chart-title">📈 Primary Trend Analysis</div>
                <div id="mainTrendChart" style="height: 400px;"></div>
            </div>
            
            <!-- Chart 2: Category Distribution -->
            <div class="chart-container">
                <div class="chart-title">📊 Distribution Analysis</div>
                <div id="distributionChart" style="height: 400px;"></div>
            </div>
            
            <!-- Chart 3: Correlation/Relationship -->
            <div class="chart-container">
                <div class="chart-title">🔗 Correlation Matrix</div>
                <div id="correlationChart" style="height: 400px;"></div>
            </div>
            
            <!-- Chart 4: Top/Bottom Analysis -->
            <div class="chart-container">
                <div class="chart-title">🏆 Top Performers</div>
                <div id="topPerformersChart" style="height: 400px;"></div>
            </div>
            
            <!-- Chart 5: Geographic/Detailed View -->
            <div class="chart-container">
                <div class="chart-title">🌍 Detailed Breakdown</div>
                <div id="detailedChart" style="height: 400px;"></div>
            </div>
            
            <!-- Chart 6: Summary Stats -->
            <div class="chart-container">
                <div class="chart-title">📋 Statistical Summary</div>
                <div id="summaryChart" style="height: 400px;"></div>
            </div>
        </div>
        
        <!-- Loading Indicator -->
        <div class="loading" id="loadingIndicator">
            <div class="spinner"></div>
            <p>Updating dashboard...</p>
        </div>
    </div>

    <script>
        // Global data storage
        let dashboardData = {{raw_data|safe}};
        let currentFilters = {
            date: 'all',
            category: 'all',
            numeric: 'all'
        };
        
        // Chart configurations
        let chartConfigs = {{chart_configs|safe}};
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeFilters();
            renderAllCharts();
            setupEventListeners();
        });
        
        function initializeFilters() {
            // Initialize date filters if date columns exist
            if (dashboardData.date_columns && dashboardData.date_columns.length > 0) {
                document.getElementById('dateFilterGroup').style.display = 'block';
                populateDateFilter();
            }
            
            // Initialize category filters
            if (dashboardData.categorical_columns && dashboardData.categorical_columns.length > 0) {
                document.getElementById('categoryFilterGroup').style.display = 'block';
                populateCategoryFilter();
            }
            
            // Initialize numeric filters
            if (dashboardData.numeric_columns && dashboardData.numeric_columns.length > 0) {
                document.getElementById('numericFilterGroup').style.display = 'block';
                populateNumericFilter();
            }
        }
        
        function populateDateFilter() {
            const dateFilter = document.getElementById('dateFilter');
            const dates = dashboardData.unique_dates || [];
            
            // Add date range options
            dates.forEach(date => {
                const option = document.createElement('option');
                option.value = date;
                option.textContent = date;
                dateFilter.appendChild(option);
            });
        }
        
        function populateCategoryFilter() {
            const categoryFilter = document.getElementById('categoryFilter');
            const categories = dashboardData.unique_categories || [];
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categoryFilter.appendChild(option);
            });
        }
        
        function populateNumericFilter() {
            const numericFilter = document.getElementById('numericFilter');
            
            // Add predefined ranges
            const ranges = [
                { value: 'low', text: 'Low (Bottom 25%)' },
                { value: 'medium', text: 'Medium (25-75%)' },
                { value: 'high', text: 'High (Top 25%)' }
            ];
            
            ranges.forEach(range => {
                const option = document.createElement('option');
                option.value = range.value;
                option.textContent = range.text;
                numericFilter.appendChild(option);
            });
        }
        
        function setupEventListeners() {
            // Filter change listeners
            document.getElementById('dateFilter').addEventListener('change', function() {
                currentFilters.date = this.value;
                updateDashboard();
            });
            
            document.getElementById('categoryFilter').addEventListener('change', function() {
                currentFilters.category = this.value;
                updateDashboard();
            });
            
            document.getElementById('numericFilter').addEventListener('change', function() {
                currentFilters.numeric = this.value;
                updateDashboard();
            });
        }
        
        function updateDashboard() {
            showLoading();
            
            // Filter data based on current filters
            const filteredData = applyFilters(dashboardData);
            
            // Update KPIs
            updateKPIs(filteredData);
            
            // Update all charts
            updateAllCharts(filteredData);
            
            hideLoading();
        }
        
        function applyFilters(data) {
            let filtered = JSON.parse(JSON.stringify(data)); // Deep copy
            
            // Apply date filter
            if (currentFilters.date !== 'all' && data.date_columns) {
                // Filter logic for dates
                filtered = filterByDate(filtered, currentFilters.date);
            }
            
            // Apply category filter
            if (currentFilters.category !== 'all' && data.categorical_columns) {
                filtered = filterByCategory(filtered, currentFilters.category);
            }
            
            // Apply numeric filter
            if (currentFilters.numeric !== 'all' && data.numeric_columns) {
                filtered = filterByNumeric(filtered, currentFilters.numeric);
            }
            
            return filtered;
        }
        
        function renderAllCharts() {
            const filteredData = applyFilters(dashboardData);
            
            // Render each chart
            renderMainTrend(filteredData);
            renderDistribution(filteredData);
            renderCorrelation(filteredData);
            renderTopPerformers(filteredData);
            renderDetailed(filteredData);
            renderSummary(filteredData);
        }
        
        function updateAllCharts(data) {
            // Update each chart with new data
            updateMainTrend(data);
            updateDistribution(data);
            updateCorrelation(data);
            updateTopPerformers(data);
            updateDetailed(data);
            updateSummary(data);
        }
        
        function renderMainTrend(data) {
            if (chartConfigs.mainTrend) {
                Plotly.newPlot('mainTrendChart', chartConfigs.mainTrend.data, chartConfigs.mainTrend.layout, {responsive: true});
            }
        }
        
        function renderDistribution(data) {
            if (chartConfigs.distribution) {
                Plotly.newPlot('distributionChart', chartConfigs.distribution.data, chartConfigs.distribution.layout, {responsive: true});
            }
        }
        
        function renderCorrelation(data) {
            if (chartConfigs.correlation) {
                Plotly.newPlot('correlationChart', chartConfigs.correlation.data, chartConfigs.correlation.layout, {responsive: true});
            }
        }
        
        function renderTopPerformers(data) {
            if (chartConfigs.topPerformers) {
                Plotly.newPlot('topPerformersChart', chartConfigs.topPerformers.data, chartConfigs.topPerformers.layout, {responsive: true});
            }
        }
        
        function renderDetailed(data) {
            if (chartConfigs.detailed) {
                Plotly.newPlot('detailedChart', chartConfigs.detailed.data, chartConfigs.detailed.layout, {responsive: true});
            }
        }
        
        function renderSummary(data) {
            if (chartConfigs.summary) {
                Plotly.newPlot('summaryChart', chartConfigs.summary.data, chartConfigs.summary.layout, {responsive: true});
            }
        }
        
        function updateKPIs(data) {
            // Update KPI values based on filtered data
            // This would be populated with actual KPI calculations
        }
        
        function resetFilters() {
            currentFilters = { date: 'all', category: 'all', numeric: 'all' };
            document.getElementById('dateFilter').value = 'all';
            document.getElementById('categoryFilter').value = 'all';
            document.getElementById('numericFilter').value = 'all';
            updateDashboard();
        }
        
        function refreshData() {
            showLoading();
            // In a real application, this would fetch fresh data
            setTimeout(() => {
                renderAllCharts();
                hideLoading();
            }, 1000);
        }
        
        function showLoading() {
            document.getElementById('loadingIndicator').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loadingIndicator').style.display = 'none';
        }
        
        // Utility functions for filtering
        function filterByDate(data, dateValue) {
            // Implement date filtering logic
            return data;
        }
        
        function filterByCategory(data, categoryValue) {
            // Implement category filtering logic  
            return data;
        }
        
        function filterByNumeric(data, numericValue) {
            // Implement numeric filtering logic
            return data;
        }
    </script>
</body>
</html>
            """,
            "executive_summary": """
<!DOCTYPE html>
<html>
<head>
    <title>{{dataset_name}} - Executive Summary</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #3498db; padding-bottom: 20px; }
        .header h1 { color: #2c3e50; margin: 0; }
        .generated-date { color: #7f8c8d; margin: 10px 0; }
        .summary-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-card h3 { margin: 0 0 10px 0; font-size: 1.1em; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .metric-description { font-size: 0.9em; opacity: 0.9; }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .chart-container { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; }
        .insights-section { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .insights-section h2 { color: #2c3e50; margin-top: 0; }
        .insight-card { background: white; border-left: 4px solid #27ae60; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .insight-card h4 { color: #27ae60; margin: 0 0 10px 0; }
        .recommendations { list-style-type: none; padding: 0; }
        .recommendations li { background: #e8f5e8; padding: 8px 12px; margin: 5px 0; border-radius: 4px; }
        .recommendations li:before { content: "✓ "; color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="dashboard executive-summary">
        <div class="header">
            <h1>{{dataset_name}} - Executive Dashboard</h1>
            <p class="generated-date">Generated on {{date}}</p>
        </div>
        
        <div class="summary-metrics">
            {% for metric in key_metrics %}
            <div class="metric-card">
                <h3>{{metric.title}}</h3>
                <div class="metric-value">{{metric.value}}</div>
                <p class="metric-description">{{metric.description}}</p>
            </div>
            {% endfor %}
        </div>
        
        <div class="charts-grid">
            {% for chart in priority_charts %}
            <div class="chart-container">
                <div id="chart_{{loop.index}}" style="width:100%;height:400px;"></div>
                <script>
                    Plotly.newPlot('chart_{{loop.index}}', {{chart.data|safe}});
                </script>
            </div>
            {% endfor %}
        </div>
        
        <div class="insights-section">
            <h2>Key Insights & Recommendations</h2>
            {% for insight in ai_insights %}
            <div class="insight-card">
                <h4>{{insight.title}}</h4>
                <p>{{insight.description}}</p>
                {% if insight.recommendations %}
                <ul class="recommendations">
                    {% for rec in insight.recommendations %}
                    <li>{{rec}}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
            """,
            "data_quality": """
<!DOCTYPE html>
<html>
<head>
    <title>{{dataset_name}} - Data Quality Report</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #e74c3c; padding-bottom: 20px; }
        .quality-score-container { display: flex; justify-content: center; margin: 20px 0; }
        .quality-score { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; border-radius: 50%; width: 120px; height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .score { font-size: 2.5em; font-weight: bold; }
        .label { font-size: 0.9em; }
        .quality-metrics { display: grid; gap: 20px; }
        .quality-section { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .quality-section h3 { color: #2c3e50; margin-top: 0; }
        .metrics-row { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }
        .metric-item { background: white; padding: 15px; border-radius: 8px; flex: 1; min-width: 200px; }
        .metric-item.status-good { border-left: 4px solid #27ae60; }
        .metric-item.status-warning { border-left: 4px solid #f39c12; }
        .metric-item.status-error { border-left: 4px solid #e74c3c; }
        .metric-name { font-weight: bold; display: block; }
        .metric-value { font-size: 1.5em; color: #2c3e50; }
        .section-chart { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="dashboard data-quality">
        <div class="header">
            <h1>{{dataset_name}} - Data Quality Report</h1>
            <div class="quality-score-container">
                <div class="quality-score">
                    <span class="score">{{quality_score}}%</span>
                    <span class="label">Quality Score</span>
                </div>
            </div>
        </div>
        
        <div class="quality-metrics">
            {% for section in quality_sections %}
            <div class="quality-section">
                <h3>{{section.title}}</h3>
                <div class="metrics-row">
                    {% for metric in section.metrics %}
                    <div class="metric-item status-{{metric.status}}">
                        <span class="metric-name">{{metric.name}}</span>
                        <span class="metric-value">{{metric.value}}</span>
                    </div>
                    {% endfor %}
                </div>
                {% if section.chart %}
                <div class="section-chart">
                    <div id="{{section.id}}_chart" style="width:100%;height:400px;"></div>
                    <script>
                        Plotly.newPlot('{{section.id}}_chart', {{section.chart.data|safe}});
                    </script>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
            """,
            "exploratory": """
<!DOCTYPE html>
<html>
<head>
    <title>{{dataset_name}} - Exploratory Analysis</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #9b59b6; padding-bottom: 20px; }
        .dataset-overview { display: flex; justify-content: center; gap: 30px; margin: 20px 0; }
        .overview-stat { text-align: center; padding: 20px; background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; border-radius: 8px; min-width: 120px; }
        .stat-value { display: block; font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .analysis-sections { display: grid; gap: 30px; }
        .analysis-section { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .analysis-section h2 { color: #2c3e50; margin-top: 0; }
        .section-description { color: #7f8c8d; margin-bottom: 20px; }
        .charts-container.layout-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }
        .charts-container.layout-row { display: flex; flex-wrap: wrap; gap: 20px; }
        .charts-container.layout-mixed { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .chart-wrapper { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; }
        .section-insights { margin-top: 20px; }
        .insight-item { display: flex; align-items: center; gap: 10px; padding: 10px; background: white; margin: 10px 0; border-radius: 8px; }
        .insight-icon { font-size: 1.2em; }
        .insight-text { flex: 1; }
    </style>
</head>
<body>
    <div class="dashboard exploratory">
        <div class="header">
            <h1>{{dataset_name}} - Exploratory Analysis</h1>
            <div class="dataset-overview">
                <div class="overview-stat">
                    <span class="stat-value">{{row_count}}</span>
                    <span class="stat-label">Rows</span>
                </div>
                <div class="overview-stat">
                    <span class="stat-value">{{column_count}}</span>
                    <span class="stat-label">Columns</span>
                </div>
                <div class="overview-stat">
                    <span class="stat-value">{{missing_percentage}}%</span>
                    <span class="stat-label">Missing Data</span>
                </div>
            </div>
        </div>
        
        <div class="analysis-sections">
            {% for section in analysis_sections %}
            <div class="analysis-section">
                <h2>{{section.title}}</h2>
                <p class="section-description">{{section.description}}</p>
                <div class="charts-container layout-{{section.layout}}">
                    {% for chart in section.charts %}
                    <div class="chart-wrapper">
                        <div id="chart_{{section.id}}_{{loop.index}}" style="width:100%;height:400px;"></div>
                        <script>
                            Plotly.newPlot('chart_{{section.id}}_{{loop.index}}', {{chart.data|safe}});
                        </script>
                    </div>
                    {% endfor %}
                </div>
                {% if section.insights %}
                <div class="section-insights">
                    {% for insight in section.insights %}
                    <div class="insight-item">
                        <span class="insight-icon">💡</span>
                        <span class="insight-text">{{insight}}</span>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
            """,
        }

    async def build_interactive_dashboard(
        self,
        dataset_name: str,
        charts: List[Dict],
        summary_stats: Dict,
        raw_data: Dict = None,
    ) -> str:
        """Build an interactive Power BI/Tableau-style dashboard"""
        try:
            # Generate KPI metrics
            kpi_metrics = self._generate_kpi_metrics(summary_stats, raw_data)

            # Generate chart configurations for interactive dashboard
            chart_configs = self._generate_interactive_chart_configs(charts, raw_data)

            # Prepare template data
            template_data = {
                "dataset_name": dataset_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "kpi_metrics": kpi_metrics,
                "raw_data": json.dumps(convert_numpy_types(raw_data or {})),
                "chart_configs": json.dumps(convert_numpy_types(chart_configs)),
            }

            # Render template
            template = Template(self.dashboard_templates["interactive_dashboard"])
            dashboard_html = template.render(**template_data)

            return dashboard_html

        except Exception as e:
            logger.error(f"Error building interactive dashboard: {str(e)}")
            raise

    def _generate_kpi_metrics(
        self, summary_stats: Dict, raw_data: Dict = None
    ) -> List[Dict]:
        """Generate KPI metrics for the dashboard"""
        kpis = []

        try:
            # Total Records
            total_records = (
                len(raw_data.get("data", []))
                if raw_data
                else summary_stats.get("total_rows", 0)
            )
            kpis.append(
                {
                    "label": "Total Records",
                    "value": f"{total_records:,}",
                    "change": None,
                    "change_class": None,
                }
            )

            # Numeric columns count
            numeric_cols = len(summary_stats.get("numeric_columns", []))
            kpis.append(
                {
                    "label": "Numeric Features",
                    "value": str(numeric_cols),
                    "change": None,
                    "change_class": None,
                }
            )

            # Categorical columns count
            cat_cols = len(summary_stats.get("categorical_columns", []))
            kpis.append(
                {
                    "label": "Categorical Features",
                    "value": str(cat_cols),
                    "change": None,
                    "change_class": None,
                }
            )

            # Missing data percentage
            if "missing_data" in summary_stats:
                missing_pct = summary_stats["missing_data"].get("percentage", 0)
                kpis.append(
                    {
                        "label": "Data Quality",
                        "value": f"{100-missing_pct:.1f}%",
                        "change": f"Missing: {missing_pct:.1f}%",
                        "change_class": "negative" if missing_pct > 10 else "positive",
                    }
                )

            # If we have numeric data, add statistical KPIs
            if raw_data and "numeric_columns" in summary_stats:
                for col in summary_stats["numeric_columns"][
                    :2
                ]:  # Top 2 numeric columns
                    if col in summary_stats.get("column_stats", {}):
                        stats = summary_stats["column_stats"][col]
                        kpis.append(
                            {
                                "label": f"Avg {col.title()}",
                                "value": f"{stats.get('mean', 0):.2f}",
                                "change": f"σ: {stats.get('std', 0):.2f}",
                                "change_class": None,
                            }
                        )

        except Exception as e:
            logger.error(f"Error generating KPIs: {str(e)}")
            # Fallback KPIs
            kpis = [
                {
                    "label": "Total Records",
                    "value": "N/A",
                    "change": None,
                    "change_class": None,
                },
                {
                    "label": "Features",
                    "value": "N/A",
                    "change": None,
                    "change_class": None,
                },
                {
                    "label": "Data Quality",
                    "value": "N/A",
                    "change": None,
                    "change_class": None,
                },
            ]

        return kpis

    async def build_ai_interactive_dashboard(
        self,
        dataset_name: str,
        df: pd.DataFrame,
        charts: List[Dict],
        summary_stats: Dict,
        raw_data: Dict = None,
        business_context: str = "",
    ) -> str:
        """Build an AI-generated interactive dashboard using agentic pipeline for layout and insights"""
        try:
            # Use agentic analysis to suggest structure
            ai_analysis = await self.ai_agent.analyze_data(df)
            # Generate insights deterministically
            ai_insights = await self.ai_agent.generate_insights(df)

            # Create AI-optimized chart configurations
            chart_configs = await self._generate_ai_chart_configs(
                charts, raw_data, ai_analysis.get("ai_analysis", {})
            )

            # Generate KPI metrics with AI recommendations
            kpi_metrics = await self._generate_ai_kpi_metrics(
                summary_stats, raw_data, ai_analysis.get("ai_analysis", {})
            )

            # Create the dashboard HTML with AI-generated content
            dashboard_html = await self._render_ai_dashboard(
                dataset_name,
                kpi_metrics,
                chart_configs,
                ai_insights,
                ai_analysis.get("ai_analysis", {}),
            )

            return dashboard_html

        except Exception as e:
            logger.error(f"Error building AI interactive dashboard: {str(e)}")
            # Fallback to template-based dashboard
            return await self.build_interactive_dashboard(
                dataset_name, charts, summary_stats, raw_data
            )

    async def _generate_ai_dashboard_structure(
        self, df: pd.DataFrame, summary_stats: Dict, business_context: str
    ) -> Dict:
        """Backwards-compatible stub retained for internal calls; now returns heuristic structure."""
        try:
            numeric_columns = summary_stats.get(
                "numeric_columns", df.select_dtypes(include=["number"]).columns.tolist()
            )
            categorical_columns = summary_stats.get(
                "categorical_columns",
                df.select_dtypes(exclude=["number"]).columns.tolist(),
            )
            return {
                "priority_insights": [
                    "Data quality analysis",
                    "Distribution patterns",
                    "Key correlations",
                ],
                "recommended_layout": {
                    "kpis": 1,
                    "trends": 2,
                    "distributions": 3,
                    "correlations": 4,
                },
                "key_metrics": ["Total Records", "Data Quality", "Key Features"],
                "chart_priorities": ["bar", "line", "scatter", "histogram"],
                "narrative": "This dashboard provides a comprehensive overview of your data.",
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
            }
        except Exception:
            return {
                "priority_insights": ["Data overview"],
                "recommended_layout": {"kpis": 1, "trends": 2},
                "key_metrics": ["Total Records"],
                "chart_priorities": ["bar", "line"],
                "narrative": "Overview",
            }

    async def _generate_ai_insights(
        self, df: pd.DataFrame, business_context: str
    ) -> List[str]:
        """Generate AI-powered insights about the data (agentic)"""
        try:
            # Get sample data for analysis
            sample_data = (
                df.head(10).to_string() if len(df) > 0 else "No data available"
            )

            prompt = f"""
            Analyze this data sample and provide 5-7 specific, actionable insights:
            
            Data Sample:
            {sample_data}
            
            Business Context: {business_context or 'General analysis'}
            
            Provide insights as a JSON array of strings. Focus on:
            - Data quality observations
            - Patterns and trends
            - Potential business implications
            - Recommendations for action
            
            Make insights specific and valuable, not generic.
            """

            # Use internal agent to get deterministic insights
            deterministic = await self.ai_agent.generate_insights(df)
            insights = deterministic.get("key_findings", [])
            return insights if isinstance(insights, list) else [str(insights)]

        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return [
                "Data analysis completed successfully",
                "Multiple variables show interesting patterns",
                "Consider data quality improvements where needed",
                "Further investigation recommended for key metrics",
            ]

    async def _generate_ai_chart_configs(
        self, charts: List[Dict], raw_data: Dict, ai_analysis: Dict
    ) -> Dict:
        """Generate optimized chart configurations based on AI analysis"""
        configs = {}

        try:
            # Prioritize charts based on AI recommendations
            chart_priorities = ai_analysis.get(
                "chart_priorities", ["bar", "line", "scatter"]
            )

            # Map charts to dashboard positions based on priority
            available_charts = {chart.get("type", "unknown"): chart for chart in charts}

            # Main trend chart (highest priority)
            if "line" in available_charts or "bar" in available_charts:
                main_chart = available_charts.get("line", available_charts.get("bar"))
                if main_chart:
                    configs["mainTrend"] = {
                        "type": main_chart.get("type", "bar"),
                        "data": main_chart.get("data", {}),
                        "title": f"Key Trends - {main_chart.get('title', 'Primary Analysis')}",
                        "config": main_chart.get("config", {}),
                    }

            # Distribution analysis
            if "histogram" in available_charts or "box" in available_charts:
                dist_chart = available_charts.get(
                    "histogram", available_charts.get("box")
                )
                if dist_chart:
                    configs["distribution"] = {
                        "type": dist_chart.get("type", "histogram"),
                        "data": dist_chart.get("data", {}),
                        "title": f"Data Distribution - {dist_chart.get('title', 'Value Analysis')}",
                        "config": dist_chart.get("config", {}),
                    }

            # Correlation/relationship analysis
            if "scatter" in available_charts or "heatmap" in available_charts:
                corr_chart = available_charts.get(
                    "scatter", available_charts.get("heatmap")
                )
                if corr_chart:
                    configs["correlation"] = {
                        "type": corr_chart.get("type", "scatter"),
                        "data": corr_chart.get("data", {}),
                        "title": f"Relationships - {corr_chart.get('title', 'Correlation Analysis')}",
                        "config": corr_chart.get("config", {}),
                    }

            # Fill remaining positions with available charts
            remaining_charts = [
                chart
                for chart in charts
                if chart.get("type")
                not in [
                    configs.get("mainTrend", {}).get("type"),
                    configs.get("distribution", {}).get("type"),
                    configs.get("correlation", {}).get("type"),
                ]
            ]

            if remaining_charts and "topPerformers" not in configs:
                configs["topPerformers"] = {
                    "type": remaining_charts[0].get("type", "bar"),
                    "data": remaining_charts[0].get("data", {}),
                    "title": f"Analysis - {remaining_charts[0].get('title', 'Additional Insights')}",
                    "config": remaining_charts[0].get("config", {}),
                }

            return configs

        except Exception as e:
            logger.error(f"Error generating AI chart configs: {str(e)}")
            return self._generate_interactive_chart_configs(charts, raw_data)

    async def _generate_ai_kpi_metrics(
        self, summary_stats: Dict, raw_data: Dict, ai_analysis: Dict
    ) -> List[Dict]:
        """Generate AI-recommended KPI metrics"""
        kpis = []

        try:
            recommended_metrics = ai_analysis.get(
                "key_metrics", ["Total Records", "Data Quality", "Key Features"]
            )

            # Generate KPIs based on AI recommendations
            for metric_name in recommended_metrics[:6]:  # Limit to 6 KPIs
                if "Total Records" in metric_name or "Records" in metric_name:
                    total_records = (
                        len(raw_data.get("data", []))
                        if raw_data
                        else summary_stats.get("total_rows", 0)
                    )
                    kpis.append(
                        {
                            "label": "Total Records",
                            "value": f"{total_records:,}",
                            "change": None,
                            "change_class": None,
                        }
                    )
                elif "Data Quality" in metric_name or "Quality" in metric_name:
                    missing_pct = summary_stats.get("missing_data", {}).get(
                        "percentage", 0
                    )
                    kpis.append(
                        {
                            "label": "Data Quality",
                            "value": f"{100-missing_pct:.1f}%",
                            "change": f"Missing: {missing_pct:.1f}%",
                            "change_class": (
                                "negative" if missing_pct > 10 else "positive"
                            ),
                        }
                    )
                elif "Features" in metric_name or "Columns" in metric_name:
                    total_features = len(
                        summary_stats.get("numeric_columns", [])
                    ) + len(summary_stats.get("categorical_columns", []))
                    kpis.append(
                        {
                            "label": "Total Features",
                            "value": str(total_features),
                            "change": f"Numeric: {len(summary_stats.get('numeric_columns', []))}",
                            "change_class": "neutral",
                        }
                    )
                elif "Numeric" in metric_name:
                    numeric_cols = len(summary_stats.get("numeric_columns", []))
                    kpis.append(
                        {
                            "label": "Numeric Features",
                            "value": str(numeric_cols),
                            "change": None,
                            "change_class": None,
                        }
                    )
                elif "Categorical" in metric_name:
                    cat_cols = len(summary_stats.get("categorical_columns", []))
                    kpis.append(
                        {
                            "label": "Categorical Features",
                            "value": str(cat_cols),
                            "change": None,
                            "change_class": None,
                        }
                    )

            # If we don't have enough KPIs, add default ones
            while len(kpis) < 4:
                kpis.extend(
                    [
                        {
                            "label": "Analysis Complete",
                            "value": "✓",
                            "change": None,
                            "change_class": "positive",
                        },
                        {
                            "label": "Charts Generated",
                            "value": str(len(summary_stats.get("charts", []))),
                            "change": None,
                            "change_class": None,
                        },
                    ]
                )
                break

            return kpis[:6]  # Return max 6 KPIs

        except Exception as e:
            logger.error(f"Error generating AI KPI metrics: {str(e)}")
            return self._generate_kpi_metrics(summary_stats, raw_data)

    async def _render_ai_dashboard(
        self,
        dataset_name: str,
        kpi_metrics: List[Dict],
        chart_configs: Dict,
        ai_insights: List[str],
        ai_analysis: Dict,
    ) -> str:
        """Render the AI-generated dashboard HTML"""
        try:
            # Create enhanced template data with AI insights
            template_data = {
                "dataset_name": dataset_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "kpi_metrics": kpi_metrics,
                "chart_configs": json.dumps(convert_numpy_types(chart_configs)),
                "ai_insights": ai_insights,
                "ai_narrative": ai_analysis.get(
                    "narrative", "AI-generated insights for your data analysis."
                ),
                "raw_data": json.dumps(
                    {}
                ),  # We'll focus on charts rather than raw data
            }

            # Use enhanced template with AI insights
            template = Template(self._get_ai_dashboard_template())
            dashboard_html = template.render(**template_data)

            return dashboard_html

        except Exception as e:
            logger.error(f"Error rendering AI dashboard: {str(e)}")
            # Fallback to regular template
            template_data = {
                "dataset_name": dataset_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "kpi_metrics": kpi_metrics,
                "chart_configs": json.dumps(convert_numpy_types(chart_configs)),
                "raw_data": json.dumps({}),
            }
            template = Template(self.dashboard_templates["interactive_dashboard"])
            return template.render(**template_data)

    def _get_ai_dashboard_template(self) -> str:
        """Get AI-enhanced dashboard template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered Dashboard - {{ dataset_name }}</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <!-- Tailwind CSS -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .kpi-card { transition: transform 0.2s; }
        .kpi-card:hover { transform: translateY(-2px); }
        .chart-container { min-height: 400px; }
        .ai-insight { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-left: 4px solid #4f46e5;
        }
        .loading { 
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">🤖 AI-Powered Dashboard</h1>
            <p class="text-gray-600">{{ dataset_name }} • Generated on {{ date }}</p>
            <div class="mt-4 p-4 ai-insight rounded-lg">
                <h3 class="text-lg font-semibold mb-2">🧠 AI Analysis Summary</h3>
                <p class="text-sm opacity-90">{{ ai_narrative }}</p>
            </div>
        </div>

        <!-- KPI Metrics -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
            {% for kpi in kpi_metrics %}
            <div class="kpi-card bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-sm font-medium text-gray-500 mb-2">{{ kpi.label }}</h3>
                <p class="text-2xl font-bold text-gray-900">{{ kpi.value }}</p>
                {% if kpi.change %}
                <p class="text-xs text-gray-500 mt-1">{{ kpi.change }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <!-- AI Insights Section -->
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">🎯 AI-Generated Insights</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {% for insight in ai_insights %}
                <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div class="flex items-start space-x-3">
                        <div class="flex-shrink-0">
                            <div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        </div>
                        <p class="text-sm text-gray-700">{{ insight }}</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Main Trend Chart -->
            <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">📈 Primary Analysis</h3>
                <div id="mainTrend" class="chart-container"></div>
            </div>

            <!-- Distribution Chart -->
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">📊 Distribution Analysis</h3>
                <div id="distribution" class="chart-container"></div>
            </div>

            <!-- Correlation Chart -->
            <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">🔗 Relationships</h3>
                <div id="correlation" class="chart-container"></div>
            </div>

            <!-- Additional Analysis -->
            <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">🎯 Additional Insights</h3>
                <div id="topPerformers" class="chart-container"></div>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center">
            <p class="text-sm text-gray-500">Dashboard powered by AI • Data analysis completed at {{ date }}</p>
        </div>
    </div>

    <script>
        // Chart configurations from backend
        const chartConfigs = {{ chart_configs|safe }};
        
        // Function to render charts
        function renderChart(elementId, config) {
            if (!config || !config.data) {
                document.getElementById(elementId).innerHTML = '<div class="flex items-center justify-center h-64"><p class="text-gray-500">No data available for this visualization</p></div>';
                return;
            }
            
            try {
                const plotData = config.data.data || [];
                const layout = {
                    ...config.data.layout,
                    margin: { t: 30, r: 30, b: 40, l: 40 },
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    font: { family: 'Inter, sans-serif', size: 12 }
                };
                
                Plotly.newPlot(elementId, plotData, layout, {
                    responsive: true,
                    displayModeBar: false
                });
            } catch (error) {
                console.error(`Error rendering chart ${elementId}:`, error);
                document.getElementById(elementId).innerHTML = '<div class="flex items-center justify-center h-64"><p class="text-gray-500">Error loading visualization</p></div>';
            }
        }
        
        // Render all charts
        document.addEventListener('DOMContentLoaded', function() {
            if (chartConfigs.mainTrend) renderChart('mainTrend', chartConfigs.mainTrend);
            if (chartConfigs.distribution) renderChart('distribution', chartConfigs.distribution);
            if (chartConfigs.correlation) renderChart('correlation', chartConfigs.correlation);
            if (chartConfigs.topPerformers) renderChart('topPerformers', chartConfigs.topPerformers);
        });
    </script>
</body>
</html>
        """

    def _generate_interactive_chart_configs(
        self, charts: List[Dict], raw_data: Optional[Dict] = None
    ) -> Dict:
        """Generate chart configurations for interactive dashboard"""
        configs = {}

        try:
            # Map charts to dashboard positions
            chart_mapping = {
                "mainTrend": None,
                "distribution": None,
                "correlation": None,
                "topPerformers": None,
                "detailed": None,
                "summary": None,
            }

            # Assign charts based on type
            for chart in charts:
                chart_type = chart.get("type", "").lower()
                chart_config = {
                    "data": chart.get("data", []),
                    "layout": chart.get("layout", {}),
                }

                # Enhance layout for dashboard
                chart_config["layout"].update(
                    {
                        "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
                        "font": {"family": "Segoe UI, sans-serif", "size": 12},
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "showlegend": True,
                    }
                )

                if (
                    "line" in chart_type
                    or "time" in chart_type
                    or "trend" in chart_type
                ):
                    chart_mapping["mainTrend"] = chart_config
                elif (
                    "bar" in chart_type
                    or "histogram" in chart_type
                    or "distribution" in chart_type
                ):
                    chart_mapping["distribution"] = chart_config
                elif "heatmap" in chart_type or "correlation" in chart_type:
                    chart_mapping["correlation"] = chart_config
                elif "pie" in chart_type or "donut" in chart_type:
                    chart_mapping["topPerformers"] = chart_config
                elif "scatter" in chart_type or "bubble" in chart_type:
                    chart_mapping["detailed"] = chart_config
                elif "box" in chart_type or "violin" in chart_type:
                    chart_mapping["summary"] = chart_config

            # Fill empty slots with default charts
            self._fill_empty_chart_slots(chart_mapping, raw_data)

            return chart_mapping

        except Exception as e:
            logger.error(f"Error generating chart configs: {str(e)}")
            return {}

    def _fill_empty_chart_slots(
        self, chart_mapping: Dict, raw_data: Optional[Dict] = None
    ):
        """Fill empty chart slots with default visualizations"""
        try:
            # Create placeholder charts for empty slots
            for slot, config in chart_mapping.items():
                if config is None:
                    chart_mapping[slot] = self._create_placeholder_chart(slot)

        except Exception as e:
            logger.error(f"Error filling chart slots: {str(e)}")

    def _create_placeholder_chart(self, slot: str) -> Dict:
        """Create a placeholder chart for empty slots"""
        placeholder_data = [
            {
                "x": ["No Data", "Available"],
                "y": [1, 1],
                "type": "bar",
                "marker": {"color": "#e9ecef"},
                "name": "Placeholder",
            }
        ]

        placeholder_layout = {
            "title": f"{slot.title()} - Data Processing",
            "xaxis": {"title": "Status"},
            "yaxis": {"title": "Value"},
            "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
            "font": {"family": "Segoe UI, sans-serif", "size": 12},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
        }

        return {"data": placeholder_data, "layout": placeholder_layout}

    async def analyze_dashboard_requirements(
        self, df: pd.DataFrame, dashboard_type: str = "auto"
    ) -> Dict[str, Any]:
        """Analyze dataset and determine dashboard requirements using MCP approach"""

        # Get basic dataset info
        basic_info = self.data_processor.get_basic_info(df)

        # Analyze data characteristics
        numerical_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

        # Determine optimal dashboard type if auto
        if dashboard_type == "auto":
            missing_percentage = (df.isnull().sum().sum() / df.size) * 100

            if missing_percentage > 15 or df.duplicated().sum() > 0:
                dashboard_type = "data_quality"
            elif len(numerical_cols) > 3 and len(categorical_cols) > 1:
                dashboard_type = "exploratory"
            else:
                dashboard_type = "executive_summary"

        # Define requirements based on type
        requirements = {
            "type": dashboard_type,
            "dataset_info": basic_info,
            "suggested_charts": await self._suggest_charts(
                df, numerical_cols, categorical_cols, datetime_cols
            ),
            "layout_preferences": self._determine_layout_preferences(
                df, dashboard_type
            ),
            "priority_insights": await self._identify_priority_insights(df),
            "customization_options": self._get_customization_options(dashboard_type),
        }

        return requirements

    async def _suggest_charts(
        self,
        df: pd.DataFrame,
        numerical_cols: List[str],
        categorical_cols: List[str],
        datetime_cols: List[str],
    ) -> List[Dict[str, Any]]:
        """Suggest appropriate charts based on data characteristics"""

        suggestions = []

        # Distribution charts for numerical data
        for col in numerical_cols[:3]:  # Limit to top 3
            suggestions.append(
                {
                    "type": "histogram",
                    "columns": [col],
                    "priority": "high" if df[col].nunique() > 10 else "medium",
                    "reason": f"Distribution analysis of {col}",
                    "chart_config": {"bins": 30, "opacity": 0.7},
                }
            )

        # Categorical analysis
        for col in categorical_cols[:2]:  # Limit to top 2
            if df[col].nunique() <= 20:
                suggestions.append(
                    {
                        "type": "bar",
                        "columns": [col],
                        "priority": "high",
                        "reason": f"Category distribution of {col}",
                        "chart_config": {"opacity": 0.8},
                    }
                )

        # Correlation analysis
        if len(numerical_cols) > 1:
            suggestions.append(
                {
                    "type": "heatmap",
                    "columns": numerical_cols[:6],  # Limit for readability
                    "priority": "high",
                    "reason": "Correlation analysis between numerical variables",
                    "chart_config": {"colorscale": "Viridis"},
                }
            )

        # Relationship analysis
        if len(numerical_cols) >= 2:
            suggestions.append(
                {
                    "type": "scatter",
                    "columns": numerical_cols[:2],
                    "priority": "medium",
                    "reason": f"Relationship between {numerical_cols[0]} and {numerical_cols[1]}",
                    "chart_config": {"opacity": 0.7},
                }
            )

        # Missing values analysis
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            suggestions.append(
                {
                    "type": "missing_values",
                    "columns": list(df.columns),
                    "priority": "high",
                    "reason": "Missing values pattern analysis",
                    "chart_config": {},
                }
            )

        return suggestions

    def _determine_layout_preferences(
        self, df: pd.DataFrame, dashboard_type: str
    ) -> Dict[str, Any]:
        """Determine optimal layout based on data and dashboard type"""

        layout_preferences = {
            "executive_summary": {
                "sections": ["summary_metrics", "key_charts", "insights"],
                "chart_layout": "grid",
                "priority_order": ["metrics", "trends", "distributions"],
            },
            "data_quality": {
                "sections": ["quality_score", "missing_data", "duplicates", "outliers"],
                "chart_layout": "stacked",
                "priority_order": ["quality", "completeness", "consistency"],
            },
            "exploratory": {
                "sections": ["overview", "distributions", "relationships", "patterns"],
                "chart_layout": "mixed",
                "priority_order": ["distributions", "correlations", "outliers"],
            },
        }

        return layout_preferences.get(dashboard_type, layout_preferences["exploratory"])

    async def _identify_priority_insights(
        self, df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Use AI to identify priority insights for the dashboard"""

        try:
            # Use your existing AI agent
            analysis = await self.ai_agent.analyze_data(df)

            priority_insights = []

            # Extract key insights from AI analysis
            if (
                "ai_analysis" in analysis
                and "recommendations" in analysis["ai_analysis"]
            ):
                for i, recommendation in enumerate(
                    analysis["ai_analysis"]["recommendations"][:5]
                ):
                    priority_insights.append(
                        {
                            "title": f"Key Finding {i+1}",
                            "description": recommendation,
                            "priority": "high" if i < 2 else "medium",
                            "type": "recommendation",
                            "recommendations": [],
                        }
                    )

            # Add data quality insights
            missing_percentage = (
                df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
            ) * 100
            if missing_percentage > 5:
                priority_insights.append(
                    {
                        "title": "Data Completeness Alert",
                        "description": f"Dataset has {missing_percentage:.1f}% missing values requiring attention",
                        "priority": "high" if missing_percentage > 20 else "medium",
                        "type": "quality",
                        "recommendations": [
                            "Consider imputation strategies for missing values",
                            "Analyze missing data patterns",
                            "Evaluate impact on analysis",
                        ],
                    }
                )

            # Add outlier insights
            numerical_cols = df.select_dtypes(include=["number"]).columns
            if len(numerical_cols) > 0:
                outlier_cols = []
                for col in numerical_cols[:3]:  # Check first 3 numerical columns
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[
                        (df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)
                    ]
                    if len(outliers) > 0:
                        outlier_cols.append(col)

                if outlier_cols:
                    priority_insights.append(
                        {
                            "title": "Outlier Detection",
                            "description": f"Outliers detected in columns: {', '.join(outlier_cols)}",
                            "priority": "medium",
                            "type": "pattern",
                            "recommendations": [
                                "Investigate outlier causes",
                                "Consider outlier treatment methods",
                                "Evaluate impact on statistical analysis",
                            ],
                        }
                    )

            return priority_insights

        except Exception as e:
            return [
                {
                    "title": "Analysis Status",
                    "description": "Basic dashboard generated successfully",
                    "priority": "low",
                    "type": "info",
                    "recommendations": ["Review the generated visualizations"],
                }
            ]

    def _get_customization_options(self, dashboard_type: str) -> Dict[str, Any]:
        """Get available customization options for dashboard type"""

        base_options = {
            "color_scheme": ["blue", "green", "purple", "orange", "red"],
            "chart_size": ["small", "medium", "large"],
            "layout_density": ["compact", "comfortable", "spacious"],
            "export_formats": ["html", "pdf", "png", "json"],
        }

        type_specific_options = {
            "executive_summary": {
                "metric_cards": True,
                "highlight_insights": True,
                "summary_level": ["high", "medium", "detailed"],
            },
            "data_quality": {
                "quality_thresholds": True,
                "detailed_reports": True,
                "recommendations": True,
            },
            "exploratory": {
                "interactive_filters": True,
                "drill_down": True,
                "statistical_tests": True,
            },
        }

        return {**base_options, **type_specific_options.get(dashboard_type, {})}

    async def generate_dashboard(
        self,
        df: pd.DataFrame,
        requirements: Dict[str, Any],
        customizations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate complete dashboard based on requirements"""

        dashboard_type = requirements["type"]
        customizations = customizations or {}

        # Generate all required charts
        charts = await self._generate_dashboard_charts(
            df, requirements["suggested_charts"]
        )

        # Process charts based on dashboard type
        processed_charts = self._process_charts_for_dashboard(charts, dashboard_type)

        # Generate insights
        insights = await self._generate_dashboard_insights(
            df, requirements["priority_insights"]
        )

        # Build dashboard sections
        sections = self._build_dashboard_sections(
            df, processed_charts, insights, requirements
        )

        # Generate final HTML
        html_content = self._render_dashboard_html(
            dashboard_type, sections, customizations, df
        )

        dashboard = {
            "id": str(uuid.uuid4()),
            "type": dashboard_type,
            "html": html_content,
            "charts": processed_charts,
            "sections": sections,
            "insights": insights,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "dataset_shape": df.shape,
                "customizations": customizations,
            },
        }

        # Save dashboard for future reference
        await self._save_dashboard(dashboard)

        # Convert numpy types to Python native types for JSON serialization
        return convert_numpy_types(dashboard)

    async def _generate_dashboard_charts(
        self, df: pd.DataFrame, suggested_charts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate all charts needed for the dashboard"""

        charts = []

        for suggestion in suggested_charts:
            try:
                chart_type = suggestion["type"]
                columns = suggestion.get("columns", [])

                if chart_type == "histogram" and len(columns) == 1:
                    chart_data = self.chart_generator._create_distribution_charts(
                        df, columns[0]
                    )
                    charts.extend(chart_data)

                elif chart_type == "bar" and len(columns) == 1:
                    chart_data = self.chart_generator._create_categorical_charts(
                        df, columns[0]
                    )
                    charts.extend(chart_data)

                elif chart_type == "heatmap":
                    numerical_cols = df.select_dtypes(
                        include=["number"]
                    ).columns.tolist()
                    if len(numerical_cols) > 1:
                        chart_data = self.chart_generator._create_correlation_heatmap(
                            df, numerical_cols[:6]
                        )
                        charts.append(chart_data)

                elif chart_type == "scatter" and len(columns) == 2:
                    chart_data = self.chart_generator._create_relationship_charts(
                        df, columns, []
                    )
                    charts.extend(chart_data)

                elif chart_type == "missing_values":
                    if df.isnull().sum().sum() > 0:
                        chart_data = self.chart_generator._create_missing_values_chart(
                            df
                        )
                        charts.append(chart_data)

            except Exception as e:
                print(f"Error generating chart {chart_type}: {e}")
                continue

        return charts

    def _process_charts_for_dashboard(
        self, charts: List[Dict[str, Any]], dashboard_type: str
    ) -> List[Dict[str, Any]]:
        """Process and prioritize charts for specific dashboard type"""

        # Add dashboard-specific metadata
        for chart in charts:
            chart["dashboard_priority"] = self._calculate_chart_priority(
                chart, dashboard_type
            )
            chart["dashboard_section"] = self._assign_chart_section(
                chart, dashboard_type
            )
            chart["display_size"] = self._determine_chart_size(chart, dashboard_type)

        # Sort by priority
        charts.sort(key=lambda x: x.get("dashboard_priority", 0), reverse=True)

        return charts

    def _calculate_chart_priority(
        self, chart: Dict[str, Any], dashboard_type: str
    ) -> int:
        """Calculate chart priority for dashboard type"""

        priority_map = {
            "executive_summary": {
                "correlation_heatmap": 90,
                "missing": 85,
                "histogram": 70,
                "bar": 75,
                "scatter": 60,
                "heatmap": 90,
            },
            "data_quality": {
                "missing": 95,
                "histogram": 80,
                "box": 85,
                "correlation_heatmap": 70,
                "bar": 60,
                "heatmap": 85,
            },
            "exploratory": {
                "histogram": 90,
                "correlation_heatmap": 95,
                "scatter": 85,
                "box": 80,
                "bar": 75,
                "heatmap": 95,
            },
        }

        chart_type = chart.get("type", "")
        type_priorities = priority_map.get(dashboard_type, {})

        return type_priorities.get(chart_type, 50)

    def _assign_chart_section(self, chart: Dict[str, Any], dashboard_type: str) -> str:
        """Assign chart to appropriate dashboard section"""

        chart_type = chart.get("type", "")

        section_map = {
            "executive_summary": {
                "heatmap": "relationships",
                "correlation_heatmap": "relationships",
                "missing": "quality",
                "histogram": "distributions",
                "bar": "distributions",
                "scatter": "relationships",
            },
            "data_quality": {
                "missing": "completeness",
                "histogram": "distributions",
                "box": "outliers",
                "heatmap": "consistency",
                "correlation_heatmap": "consistency",
                "bar": "distributions",
            },
            "exploratory": {
                "histogram": "distributions",
                "heatmap": "relationships",
                "correlation_heatmap": "relationships",
                "scatter": "relationships",
                "box": "distributions",
                "bar": "categorical",
            },
        }

        type_sections = section_map.get(dashboard_type, {})
        return type_sections.get(chart_type, "general")

    def _determine_chart_size(self, chart: Dict[str, Any], dashboard_type: str) -> str:
        """Determine appropriate chart size for dashboard"""

        priority = chart.get("dashboard_priority", 50)

        if priority > 85:
            return "large"
        elif priority > 70:
            return "medium"
        else:
            return "small"

    async def _generate_dashboard_insights(
        self, df: pd.DataFrame, priority_insights: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive insights for dashboard"""

        insights = priority_insights.copy()

        # Add automated insights
        try:
            ai_insights = await self.ai_agent.generate_insights(df)

            if ai_insights and "key_findings" in ai_insights:
                for finding in ai_insights["key_findings"][:3]:
                    insights.append(
                        {
                            "title": "AI-Generated Insight",
                            "description": finding,
                            "priority": "medium",
                            "type": "ai_generated",
                            "recommendations": [],
                        }
                    )

        except Exception as e:
            print(f"Error generating AI insights: {e}")

        return insights

    def _build_dashboard_sections(
        self,
        df: pd.DataFrame,
        charts: List[Dict[str, Any]],
        insights: List[Dict[str, Any]],
        requirements: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Build organized dashboard sections"""

        dashboard_type = requirements["type"]

        # Group charts by section
        sections_dict = {}
        for chart in charts:
            section = chart.get("dashboard_section", "general")
            if section not in sections_dict:
                sections_dict[section] = []
            sections_dict[section].append(chart)

        # Build sections based on dashboard type
        if dashboard_type == "executive_summary":
            return self._build_executive_sections(df, sections_dict, insights)
        elif dashboard_type == "data_quality":
            return self._build_quality_sections(df, sections_dict, insights)
        elif dashboard_type == "exploratory":
            return self._build_exploratory_sections(df, sections_dict, insights)
        else:
            return self._build_default_sections(df, sections_dict, insights)

    def _build_executive_sections(
        self,
        df: pd.DataFrame,
        sections_dict: Dict[str, List],
        insights: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build sections for executive summary dashboard"""

        sections = []

        # Key metrics
        key_metrics = self._generate_summary_metrics(df)

        # Priority charts (limit to top 4 for executive view)
        priority_charts = []
        if "relationships" in sections_dict:
            priority_charts.extend(sections_dict["relationships"][:2])
        if "distributions" in sections_dict:
            priority_charts.extend(sections_dict["distributions"][:2])

        # High priority insights
        high_priority_insights = [i for i in insights if i.get("priority") == "high"][
            :3
        ]

        return {
            "key_metrics": list(key_metrics.values()),
            "priority_charts": priority_charts,
            "ai_insights": high_priority_insights,
        }

    def _build_quality_sections(
        self,
        df: pd.DataFrame,
        sections_dict: Dict[str, List],
        insights: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build sections for data quality dashboard"""

        # Calculate quality score
        quality_score = self._calculate_quality_score(df)

        # Build quality sections
        quality_sections = []

        # Completeness section
        missing_data = df.isnull().sum()
        completeness_metrics = []
        for col, missing_count in missing_data.items():
            if missing_count > 0:
                missing_perc = (missing_count / len(df)) * 100
                status = (
                    "error"
                    if missing_perc > 20
                    else "warning" if missing_perc > 5 else "good"
                )
                completeness_metrics.append(
                    {
                        "name": f"{col} Missing",
                        "value": f"{missing_perc:.1f}%",
                        "status": status,
                    }
                )

        if completeness_metrics:
            completeness_section = {
                "id": "completeness",
                "title": "Data Completeness",
                "metrics": completeness_metrics,
            }

            # Add missing values chart if available
            if "completeness" in sections_dict:
                completeness_section["chart"] = sections_dict["completeness"][0]

            quality_sections.append(completeness_section)

        # Distribution quality section
        if "distributions" in sections_dict:
            distribution_metrics = []
            numerical_cols = df.select_dtypes(include=["number"]).columns
            for col in numerical_cols[:3]:
                std_val = df[col].std()
                status = "good" if not np.isnan(std_val) and std_val > 0 else "warning"
                distribution_metrics.append(
                    {
                        "name": f"{col} Variance",
                        "value": f"{std_val:.2f}" if not np.isnan(std_val) else "N/A",
                        "status": status,
                    }
                )

            if distribution_metrics:
                quality_sections.append(
                    {
                        "id": "distributions",
                        "title": "Distribution Quality",
                        "metrics": distribution_metrics,
                        "chart": (
                            sections_dict["distributions"][0]
                            if sections_dict["distributions"]
                            else None
                        ),
                    }
                )

        return {
            "quality_score": int(quality_score["overall_score"]),
            "quality_sections": quality_sections,
        }

    def _build_exploratory_sections(
        self,
        df: pd.DataFrame,
        sections_dict: Dict[str, List],
        insights: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build sections for exploratory analysis dashboard"""

        analysis_sections = []

        # Distributions section
        if "distributions" in sections_dict:
            analysis_sections.append(
                {
                    "id": "distributions",
                    "title": "Variable Distributions",
                    "description": "Understanding the distribution patterns of your data variables",
                    "charts": sections_dict["distributions"][:4],
                    "layout": "grid",
                    "insights": [
                        f"Analyzed {len(sections_dict['distributions'])} distribution patterns"
                    ],
                }
            )

        # Relationships section
        if "relationships" in sections_dict:
            analysis_sections.append(
                {
                    "id": "relationships",
                    "title": "Variable Relationships",
                    "description": "Exploring correlations and relationships between variables",
                    "charts": sections_dict["relationships"][:3],
                    "layout": "mixed",
                    "insights": [
                        f"Found {len(sections_dict['relationships'])} key relationships"
                    ],
                }
            )

        # Categorical section
        if "categorical" in sections_dict:
            analysis_sections.append(
                {
                    "id": "categorical",
                    "title": "Categorical Analysis",
                    "description": "Analyzing categorical variables and their distributions",
                    "charts": sections_dict["categorical"][:3],
                    "layout": "row",
                    "insights": [
                        f"Examined {len(sections_dict['categorical'])} categorical variables"
                    ],
                }
            )

        return {
            "row_count": f"{df.shape[0]:,}",
            "column_count": str(df.shape[1]),
            "missing_percentage": f"{(df.isnull().sum().sum() / df.size * 100):.1f}",
            "analysis_sections": analysis_sections,
        }

    def _build_default_sections(
        self,
        df: pd.DataFrame,
        sections_dict: Dict[str, List],
        insights: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build default sections for general dashboard"""

        return self._build_exploratory_sections(df, sections_dict, insights)

    def _generate_summary_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary metrics for executive dashboard"""

        numerical_cols = df.select_dtypes(include=["number"]).columns
        categorical_cols = df.select_dtypes(include=["object"]).columns

        metrics = {
            "total_records": {
                "title": "Total Records",
                "value": f"{df.shape[0]:,}",
                "description": "Number of data points in the dataset",
            },
            "data_completeness": {
                "title": "Data Completeness",
                "value": f"{((df.size - df.isnull().sum().sum()) / df.size * 100):.1f}%",
                "description": "Percentage of non-missing values",
            },
            "numerical_features": {
                "title": "Numerical Features",
                "value": str(len(numerical_cols)),
                "description": "Number of quantitative variables",
            },
            "categorical_features": {
                "title": "Categorical Features",
                "value": str(len(categorical_cols)),
                "description": "Number of qualitative variables",
            },
        }

        return metrics

    def _calculate_quality_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive data quality score"""

        total_score = 100
        details = []

        # Missing values penalty
        missing_percentage = (df.isnull().sum().sum() / df.size) * 100
        if missing_percentage > 0:
            penalty = min(missing_percentage * 2, 30)
            total_score -= penalty
            details.append(
                {
                    "factor": "Missing Values",
                    "score": 100 - penalty,
                    "description": f"{missing_percentage:.1f}% missing data",
                }
            )

        # Duplicate rows penalty
        duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
        if duplicate_percentage > 0:
            penalty = min(duplicate_percentage * 3, 20)
            total_score -= penalty
            details.append(
                {
                    "factor": "Duplicates",
                    "score": 100 - penalty,
                    "description": f"{duplicate_percentage:.1f}% duplicate rows",
                }
            )

        return {
            "overall_score": max(total_score, 0),
            "details": details,
            "status": (
                "excellent"
                if total_score >= 90
                else "good" if total_score >= 70 else "needs_improvement"
            ),
        }

    def _render_dashboard_html(
        self,
        dashboard_type: str,
        sections: Dict[str, Any],
        customizations: Dict[str, Any],
        df: pd.DataFrame,
    ) -> str:
        """Render final HTML dashboard"""

        template_str = self.dashboard_templates.get(
            dashboard_type, self.dashboard_templates["exploratory"]
        )

        # Create Jinja2 environment
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_str)

        # Prepare template context
        context = {
            "dataset_name": "Dataset Analysis",
            "date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            **sections,
        }

        # Render HTML
        html_content = template.render(**context)

        return html_content

    async def _save_dashboard(self, dashboard: Dict[str, Any]) -> None:
        """Save dashboard to storage"""
        self.dashboard_storage[dashboard["id"]] = dashboard

    async def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve saved dashboard"""
        return self.dashboard_storage.get(dashboard_id)

    async def list_dashboards(self) -> List[Dict[str, Any]]:
        """List all saved dashboards"""
        return [
            {
                "id": dashboard["id"],
                "type": dashboard["type"],
                "generated_at": dashboard["metadata"]["generated_at"],
                "dataset_shape": dashboard["metadata"]["dataset_shape"],
            }
            for dashboard in self.dashboard_storage.values()
        ]

    async def export_dashboard(
        self, dashboard_id: str, format: str = "html"
    ) -> Dict[str, Any]:
        """Export dashboard in specified format"""

        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")

        if format == "html":
            return {
                "format": "html",
                "content": dashboard["html"],
                "filename": f"dashboard_{dashboard_id}.html",
            }
        elif format == "json":
            return {
                "format": "json",
                "content": json.dumps(dashboard, indent=2),
                "filename": f"dashboard_{dashboard_id}.json",
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")
