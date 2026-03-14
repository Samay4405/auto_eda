import os
import pytest


def groq_env_available():
    return bool(os.getenv("GROQ_API_KEY"))


@pytest.mark.skipif(not groq_env_available(), reason="GROQ_API_KEY not set; skipping Groq provider test")
def test_llm_insights_engine_uses_groq():
    from services.llm_insights_engine import LLMInsightsEngine

    engine = LLMInsightsEngine()
    # If GROQ_API_KEY is set, engine should prefer Groq
    assert getattr(engine, "provider", None) == "groq"
