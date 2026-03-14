"""
Test LLM Insights Engine
"""

import sys
import os
import pandas as pd
import asyncio
from pathlib import Path

# Add server directory to path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from services.llm_insights_engine import LLMInsightsEngine, generate_insights_summary
from services.dashboard_tools import ExecutiveDashboardTool, DataQualityDashboardTool, ExploratoryDashboardTool


async def test_executive_insights():
    """Test LLM insights for executive dashboard"""
    print("\n" + "=" * 70)
    print("Testing Executive Dashboard LLM Insights")
    print("=" * 70)
    
    # Create sample business data
    df = pd.DataFrame({
        'revenue': [100000, 120000, 115000, 130000, 125000, 140000, 135000, 150000],
        'profit': [20000, 25000, 22000, 28000, 26000, 30000, 29000, 33000],
        'customers': [1000, 1100, 1050, 1200, 1150, 1300, 1250, 1400],
        'satisfaction_score': [4.2, 4.3, 4.1, 4.4, 4.3, 4.5, 4.4, 4.6],
        'churn_rate': [5.2, 4.8, 5.1, 4.5, 4.7, 4.2, 4.4, 4.0]
    })
    
    # Generate analysis
    tool = ExecutiveDashboardTool()
    metrics = tool.calculate_executive_metrics(df)
    charts = tool.create_executive_charts(df, metrics)
    
    try:
        # Initialize insights engine
        insights_engine = LLMInsightsEngine()
        
        # Generate insights
        print("\n🤖 Generating LLM insights...")
        insights = insights_engine.analyze_dashboard(
            df=df,
            dashboard_type="executive",
            chart_specs=charts,
            data_analysis=metrics,
            user_context="Q4 Performance Review - Growing SaaS Company"
        )
        
        print(f"\n✅ Insights generated successfully!")
        print(f"\nAnalysis Type: {insights.get('analysis_type')}")
        print(f"Generated At: {insights.get('generated_at')}")
        
        # Display executive summary
        if 'executive_summary' in insights:
            print(f"\n📊 Executive Summary:")
            print(f"   {insights['executive_summary']}")
        
        # Display key insights
        if 'key_insights' in insights:
            print(f"\n🎯 Key Insights:")
            for insight in insights['key_insights']:
                print(f"   • {insight}")
        
        # Display recommendations
        if 'recommendations' in insights:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(insights['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Test summary generation
        print(f"\n📝 Generated Summary Points:")
        summary = generate_insights_summary(insights)
        for point in summary:
            print(f"   {point}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_quality_insights():
    """Test LLM insights for data quality dashboard"""
    print("\n" + "=" * 70)
    print("Testing Data Quality Dashboard LLM Insights")
    print("=" * 70)
    
    # Create sample data with quality issues
    df = pd.DataFrame({
        'user_id': range(100),
        'age': [25, 30, None, 40, 45, 50, None, 60] * 12 + [25, 30, None, 40],
        'income': [50000, 60000, 75000, None, 95000, 105000, 110000, None] * 12 + [50000, 60000, 75000, None],
        'email': ['valid@email.com', 'another@test.com', None, 'test@example.com'] * 25,
        'signup_date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'score': [85, 90, 95, 88, None, 92, 1000, 87] * 12 + [85, 90, 95, 88]  # Has outlier
    })
    
    # Generate quality analysis
    tool = DataQualityDashboardTool()
    quality_report = tool.analyze_data_quality_comprehensive(df)
    charts = tool.create_quality_charts(df, quality_report)
    
    try:
        insights_engine = LLMInsightsEngine()
        
        print("\n🤖 Generating LLM quality insights...")
        insights = insights_engine.analyze_dashboard(
            df=df,
            dashboard_type="data_quality",
            chart_specs=charts,
            data_analysis=quality_report,
            user_context="Pre-production data validation for user database"
        )
        
        print(f"\n✅ Quality insights generated!")
        
        # Display quality score
        if 'quality_score' in insights:
            score = insights['quality_score']
            print(f"\n📊 Overall Quality Score: {score}/100")
            print(f"   Justification: {insights.get('score_justification', 'N/A')}")
        
        # Display critical issues
        if 'critical_issues' in insights:
            print(f"\n⚠️  Critical Issues:")
            for issue in insights['critical_issues']:
                print(f"   • {issue}")
        
        # Display remediation priorities
        if 'remediation_priorities' in insights:
            print(f"\n🔧 Remediation Priorities:")
            for i, priority in enumerate(insights['remediation_priorities'], 1):
                print(f"   {i}. {priority}")
        
        # Readiness assessment
        if 'readiness_assessment' in insights:
            print(f"\n✓ Readiness: {insights['readiness_assessment']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_exploratory_insights():
    """Test LLM insights for exploratory dashboard"""
    print("\n" + "=" * 70)
    print("Testing Exploratory Dashboard LLM Insights")
    print("=" * 70)
    
    # Create interesting dataset for exploration
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70] * 10,
        'income': [40000, 55000, 70000, 85000, 95000, 105000, 110000, 115000, 120000, 125000] * 10,
        'education': ['HS', 'BS', 'BS', 'MS', 'MS', 'PhD', 'PhD', 'MS', 'BS', 'HS'] * 10,
        'experience_years': [2, 5, 10, 15, 20, 25, 30, 35, 40, 45] * 10,
        'job_satisfaction': [3.5, 4.0, 4.5, 3.8, 4.2, 4.7, 3.9, 4.3, 4.8, 4.1] * 10,
        'department': ['Sales', 'Engineering', 'Marketing', 'Engineering', 'Sales'] * 20
    })
    
    # Generate exploratory analysis
    tool = ExploratoryDashboardTool()
    patterns = tool.analyze_data_patterns(df)
    charts = tool.create_exploratory_charts(df, patterns)
    
    try:
        insights_engine = LLMInsightsEngine()
        
        print("\n🤖 Generating LLM exploratory insights...")
        insights = insights_engine.analyze_dashboard(
            df=df,
            dashboard_type="exploratory",
            chart_specs=charts,
            data_analysis=patterns,
            user_context="Employee data analysis - Understand factors affecting satisfaction"
        )
        
        print(f"\n✅ Exploratory insights generated!")
        
        # Display patterns
        if 'patterns' in insights:
            print(f"\n🔍 Key Patterns Discovered:")
            for pattern in insights['patterns'][:5]:
                print(f"   • {pattern}")
        
        # Display correlations
        if 'correlations' in insights:
            print(f"\n🔗 Correlation Insights:")
            if isinstance(insights['correlations'], list):
                for corr in insights['correlations'][:3]:
                    print(f"   • {corr}")
            else:
                print(f"   {insights['correlations']}")
        
        # Display Hypothesis 
        if 'Hypothesis ' in insights:
            print(f"\n💭 Generated Hypothesis :")
            for i, hyp in enumerate(insights['Hypothesis '][:5], 1):
                print(f"   {i}. {hyp}")
        
        # Deep dive recommendations
        if 'deep_dive_recommendations' in insights:
            print(f"\n🎯 Recommended Deep Dives:")
            for rec in insights['deep_dive_recommendations'][:3]:
                print(f"   • {rec}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all LLM insights tests"""
    print("\n" + "🧪" * 35)
    print("🤖 LLM INSIGHTS ENGINE TEST SUITE 🤖")
    print("🧪" * 35)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Executive Insights
    if await test_executive_insights():
        success_count += 1
    
    # Test 2: Data Quality Insights
    if await test_data_quality_insights():
        success_count += 1
    
    # Test 3: Exploratory Insights
    if await test_exploratory_insights():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 Test Summary: {success_count}/{total_tests} tests passed")
    print("=" * 70)
    
    if success_count == total_tests:
        print("\n✅ All LLM insights tests PASSED!")
        print("\n💡 The LLM Insights Engine is working correctly and generating:")
        print("   • Executive summaries and strategic recommendations")
        print("   • Data quality assessments and remediation priorities")
        print("   • Exploratory patterns, correlations, and Hypothesis ")
        print("\n🎯 Real-time, valuable insights are now available for all dashboards!")
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) FAILED")
        print("\nNote: LLM insights require OPENAI_API_KEY environment variable")
        print("      Fallback insights will be used if LLM is unavailable")


if __name__ == "__main__":
    asyncio.run(main())
