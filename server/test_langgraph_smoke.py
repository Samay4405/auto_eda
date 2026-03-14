import asyncio
import pandas as pd
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder


def test_langgraph_dashboard_build_exploratory():
    df = pd.DataFrame({
        'num1': [1,2,3,4,5,6,7,8,9,10],
        'num2': [2,4,6,8,10,12,14,16,18,20],
        'cat': ['A','B','A','B','A','B','A','B','A','B']
    })

    async def _run():
        builder = LangGraphDashboardBuilder()
        res = await builder.build_dashboard(
            df=df,
            dashboard_type='exploratory',
            user_context='pytest',
            target_audience='analyst'
        )
        assert res.get('success') is True
        html = res.get('dashboard_html', '')
        assert isinstance(html, str) and len(html) > 100
        # Ensure insights rendered
        assert 'insights-content' in html
        # Ensure we have some charts planned
        assert isinstance(res.get('chart_specifications', []), list)

    asyncio.run(_run())
