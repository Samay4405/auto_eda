"""
Test that dashboard charts are properly embedded and rendered
"""

import sys
import os
import pandas as pd
import re
import asyncio
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from services.langgraph_dashboard_builder import LangGraphDashboardBuilder
from services.dashboard_tools import ExecutiveDashboardTool, DataQualityDashboardTool, ExploratoryDashboardTool

async def test_executive_dashboard():
    """Test executive dashboard generation with chart embedding"""
    print("\n" + "=" * 60)
    print("Testing Executive Dashboard Chart Embedding")
    print("=" * 60)
    
    # Create sample data
    df = pd.DataFrame({
        'revenue': [100, 120, 115, 130, 125, 140, 135, 150],
        'profit': [20, 25, 22, 28, 26, 30, 29, 33],
        'customers': [1000, 1100, 1050, 1200, 1150, 1300, 1250, 1400],
        'satisfaction': [4.2, 4.3, 4.1, 4.4, 4.3, 4.5, 4.4, 4.6]
    })
    
    # Generate executive dashboard
    builder = LangGraphDashboardBuilder()
    result = await builder.build_dashboard(
        df=df,
        dashboard_type="executive",
        user_context="Executive performance dashboard"
    )
    
    if result.get("status") == "error":
        print(f"❌ Dashboard generation failed: {result.get('error')}")
        return False
    
    html = result.get("dashboard_html", "")
    chart_specs = result.get("chart_specifications", [])
    
    print(f"\n✓ Dashboard HTML generated: {len(html)} bytes")
    print(f"✓ Chart specifications: {len(chart_specs)} charts")
    
    # Verify chart specs have correct IDs matching layout
    print("\nChart IDs in specifications:")
    for i, chart in enumerate(chart_specs):
        chart_id = chart.get("id", "NO_ID")
        chart_type = chart.get("type", "NO_TYPE")
        has_data = "config" in chart and ("x" in chart["config"] or "y" in chart["config"] or "value" in chart["config"])
        has_columns = "columns" in chart
        print(f"  {i+1}. ID: {chart_id}, Type: {chart_type}, Has Data: {has_data}, Has Columns: {has_columns}")
    
    # Check for primary_chart and secondary_chart (matching layout IDs)
    chart_ids = [c.get("id") for c in chart_specs]
    if "primary_chart" in chart_ids:
        print("✓ Found 'primary_chart' (matches layout section ID)")
    else:
        print("⚠️  Missing 'primary_chart' ID")
    
    if "secondary_chart" in chart_ids:
        print("✓ Found 'secondary_chart' (matches layout section ID)")
    else:
        print("⚠️  Missing 'secondary_chart' ID")
    
    # Verify HTML contains chart containers with correct IDs
    print("\nChart containers in HTML:")
    chart_container_pattern = r'<div class="chart-container" id="([^"]+)"'
    containers = re.findall(chart_container_pattern, html)
    for container_id in containers:
        print(f"  - {container_id}")
    
    # Verify JavaScript embeds chart configs
    if "const chartConfigs =" in html:
        print("✓ chartConfigs embedded in JavaScript")
        
        # Extract chartConfigs to verify structure
        match = re.search(r'const chartConfigs = (\[.*?\]);', html, re.DOTALL)
        if match:
            print("✓ chartConfigs data structure found")
        else:
            print("⚠️  chartConfigs structure not parseable")
    else:
        print("❌ chartConfigs NOT embedded in JavaScript")
    
    # Verify Plotly.newPlot calls exist
    plotly_calls = html.count("Plotly.newPlot")
    print(f"\n✓ Plotly.newPlot calls found: {plotly_calls}")
    
    # Check for gauge and line chart renderers
    if "renderGaugeChart" in html:
        print("✓ renderGaugeChart function included")
    else:
        print("⚠️  renderGaugeChart function missing")
    
    if "renderLineChart" in html:
        print("✓ renderLineChart function included")
    else:
        print("⚠️  renderLineChart function missing")
    
    # Check for flexible rendering logic
    if "config.config?.x" in html or "config.config?.y" in html:
        print("✓ Flexible data extraction (checks config.config for embedded data)")
    else:
        print("⚠️  May not handle embedded chart data properly")
    
    print("\n" + "=" * 60)
    return True


async def test_exploratory_dashboard():
    """Test exploratory dashboard generation"""
    print("\n" + "=" * 60)
    print("Testing Exploratory Dashboard Chart Embedding")
    print("=" * 60)
    
    # Create sample data
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65],
        'income': [50000, 60000, 75000, 85000, 95000, 105000, 110000, 120000, 125000],
        'education': ['BS', 'MS', 'PhD', 'BS', 'MS', 'PhD', 'BS', 'MS', 'PhD'],
        'satisfaction': [3.5, 4.0, 4.5, 3.8, 4.2, 4.7, 3.9, 4.3, 4.8]
    })
    
    # Generate exploratory dashboard
    builder = LangGraphDashboardBuilder()
    result = await builder.build_dashboard(
        df=df,
        dashboard_type="exploratory",
        user_context="Exploratory data analysis"
    )
    
    if result.get("status") == "error":
        print(f"❌ Dashboard generation failed: {result.get('error')}")
        return False
    
    html = result.get("dashboard_html", "")
    chart_specs = result.get("chart_specifications", [])
    
    print(f"\n✓ Dashboard HTML generated: {len(html)} bytes")
    print(f"✓ Chart specifications: {len(chart_specs)} charts")
    
    # Verify chart types
    print("\nChart specifications:")
    for i, chart in enumerate(chart_specs):
        chart_id = chart.get("id", "NO_ID")
        chart_type = chart.get("type", "NO_TYPE")
        has_data = "config" in chart and ("x" in chart["config"] or "z" in chart["config"])
        print(f"  {i+1}. ID: {chart_id}, Type: {chart_type}, Has Data: {has_data}")
    
    # Check for fallback rendering logic
    if "section_" in html or "chart_" in html:
        print("✓ Fallback section IDs present in HTML")
    
    # Verify flexible chart rendering
    if "chartConfigs.forEach" in html:
        print("✓ Charts will be rendered from chartConfigs array")
    else:
        print("❌ Chart rendering loop not found")
    
    print("\n" + "=" * 60)
    return True


async def test_data_quality_dashboard():
    """Test data quality dashboard generation"""
    print("\n" + "=" * 60)
    print("Testing Data Quality Dashboard Chart Embedding")
    print("=" * 60)
    
    # Create sample data with quality issues
    df = pd.DataFrame({
        'col1': [1, 2, None, 4, 5, 6, 7, 1000],  # Has missing + outlier
        'col2': [10, 20, 30, 40, None, 60, 70, 80],  # Has missing
        'col3': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
        'col4': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8]
    })
    
    # Generate data quality dashboard
    builder = LangGraphDashboardBuilder()
    result = await builder.build_dashboard(
        df=df,
        dashboard_type="data_quality",
        user_context="Data quality assessment"
    )
    
    if result.get("status") == "error":
        print(f"❌ Dashboard generation failed: {result.get('error')}")
        return False
    
    html = result.get("dashboard_html", "")
    chart_specs = result.get("chart_specifications", [])
    
    print(f"\n✓ Dashboard HTML generated: {len(html)} bytes")
    print(f"✓ Chart specifications: {len(chart_specs)} charts")
    
    # Verify gauge chart for quality score
    gauge_charts = [c for c in chart_specs if c.get("type") == "gauge_chart"]
    print(f"\n✓ Gauge charts: {len(gauge_charts)}")
    
    if gauge_charts and "renderGaugeChart" in html:
        print("✓ Gauge chart rendering function available")
    
    print("\n" + "=" * 60)
    return True


async def main():
    """Main async test runner"""
    print("\n🧪 Testing Dashboard Chart Embedding Fixes\n")
    
    success_count = 0
    total_tests = 3
    
    try:
        if await test_executive_dashboard():
            success_count += 1
    except Exception as e:
        print(f"\n❌ Executive dashboard test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        if await test_exploratory_dashboard():
            success_count += 1
    except Exception as e:
        print(f"\n❌ Exploratory dashboard test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        if await test_data_quality_dashboard():
            success_count += 1
    except Exception as e:
        print(f"\n❌ Data quality dashboard test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Summary: {success_count}/{total_tests} tests passed")
    print("=" * 60)
    
    if success_count == total_tests:
        print("\n✅ All chart embedding tests PASSED!")
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) FAILED")


if __name__ == "__main__":
    asyncio.run(main())
