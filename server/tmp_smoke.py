import asyncio, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder

async def main():
    df = pd.DataFrame({"a": [1,2,3,4], "b": [2,3,4,5]})
    builder = LangGraphDashboardBuilder()
    res = await builder.build_dashboard(df=df, dashboard_type="exploratory", user_context="smoke-test", target_audience="analyst")
    print({k: type(v).__name__ for k,v in res.items()})
    print("success:", res.get("success"), "insights:", len(res.get("insights", [])))

if __name__ == "__main__":
    asyncio.run(main())
