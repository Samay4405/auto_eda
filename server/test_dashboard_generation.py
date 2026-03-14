"""
Test script for the enhanced LLM-based dashboard generation.
This demonstrates the new LangGraph workflow with LLM code generation and verification.
"""

import sys
import os
import asyncio
import pandas as pd
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.langgraph_dashboard_builder import LangGraphDashboardBuilder


async def test_dashboard_generation():
    """Test the dashboard generation with a sample dataset"""
    
    print("=" * 80)
    print("DASHBOARD GENERATION TEST")
    print("=" * 80)
    
    # Load a sample dataset
    upload_dir = Path(__file__).parent.parent / "uploads"
    csv_files = list(upload_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in uploads directory")
        print("   Please upload a CSV file to test with")
        return
    
    csv_file = csv_files[0]
    print(f"\n📊 Loading dataset: {csv_file.name}")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"   ✓ Loaded {len(df)} rows × {len(df.columns)} columns")
        print(f"   Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Test different dashboard types
    dashboard_types = ["exploratory", "executive", "data_quality"]
    
    for dashboard_type in dashboard_types:
        print(f"\n{'─' * 80}")
        print(f"Testing: {dashboard_type.upper()} Dashboard")
        print(f"{'─' * 80}")
        
        try:
            # Initialize builder
            builder = LangGraphDashboardBuilder()
            
            # Check if LLM is available
            has_llm = os.getenv("OPENAI_API_KEY") is not None
            print(f"   LLM Mode: {'ENABLED ✓' if has_llm else 'DISABLED (using fallback)'}")
            
            # Build dashboard
            print("   Generating dashboard...")
            result = await builder.build_dashboard(
                df=df,
                dashboard_type=dashboard_type,
                user_context=f"Analysis of {csv_file.stem} dataset",
                target_audience="analyst"
            )
            
            if result.get("success"):
                print("   ✓ Dashboard generation successful!")
                
                # Show stats
                html_code = result.get("dashboard_html", "")
                print(f"   Generated HTML: {len(html_code):,} characters")
                
                chart_specs = result.get("chart_specifications", [])
                print(f"   Charts configured: {len(chart_specs)}")
                
                insights = result.get("insights", [])
                print(f"   Insights generated: {len(insights)}")
                
                # Check verification
                verification_report = result.get("verification_report")
                if verification_report:
                    print(f"\n   Verification Status: {verification_report.get('overall_status', 'N/A')}")
                    print(f"   Passed Checks: {len(verification_report.get('passed_checks', []))}")
                    print(f"   Warnings: {len(verification_report.get('warnings', []))}")
                    print(f"   Critical Issues: {len(verification_report.get('critical_issues', []))}")
                    
                    if verification_report.get('llm_review'):
                        llm_review = verification_report['llm_review']
                        print(f"\n   LLM Review Score: {llm_review.get('score', 0)}/100")
                        print(f"   Summary: {llm_review.get('summary', 'N/A')[:100]}")
                
                # Save dashboard to file
                output_dir = Path(__file__).parent / "generated_dashboards"
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{dashboard_type}_dashboard_{csv_file.stem}.html"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_code)
                
                print(f"\n   💾 Dashboard saved to: {output_file}")
                print(f"   📂 Open in browser to view!")
                
            else:
                print(f"   ❌ Generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error during generation: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    print("\n📝 SUMMARY:")
    print("   • Dashboard types tested: exploratory, executive, data_quality")
    print("   • LLM integration: " + ("Active" if os.getenv("OPENAI_API_KEY") else "Fallback mode"))
    print("   • Generated files saved to: server/generated_dashboards/")
    print("\n💡 NEXT STEPS:")
    if not os.getenv("OPENAI_API_KEY"):
        print("   • Set OPENAI_API_KEY environment variable to enable LLM generation")
        print("     Example: $env:OPENAI_API_KEY='sk-...' (PowerShell)")
    print("   • Open generated HTML files in a browser to preview dashboards")
    print("   • Integrate into your FastAPI endpoints for production use")


if __name__ == "__main__":
    asyncio.run(test_dashboard_generation())
