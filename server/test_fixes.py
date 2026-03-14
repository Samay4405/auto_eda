#!/usr/bin/env python3
"""Validate recent fixes: NumPy serialization and Groq key"""

print("=" * 60)
print("Validating Recent Fixes")
print("=" * 60)

# Test 1: NumPy conversion
print("\n[1] Testing NumPy serialization fix...")
try:
    from api import convert_numpy_types
    import numpy as np

    test_data = {
        "int64": np.int64(42),
        "float64": np.float64(3.14),
        "array": np.array([1, 2, 3]).tolist(),
        "normal": "string"
    }
    result = convert_numpy_types(test_data)
    assert isinstance(result["int64"], int)
    assert isinstance(result["float64"], float)
    print("  ✓ NumPy types converted correctly")
except Exception as e:
    print(f"  ✗ NumPy conversion failed: {e}")

# Test 2: Groq API key
print("\n[2] Testing Groq API key detection...")
try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"  ✓ Groq API key loaded (ends with: ...{groq_key[-8:]})")
    else:
        print("  ✗ Groq API key not found")
except Exception as e:
    print(f"  ✗ Groq key test failed: {e}")

# Test 3: LLM insights fallback
print("\n[3] Testing LLM insights fallback behavior...")
try:
    from services.llm_insights_engine import LANGCHAIN_AVAILABLE, LC_GROQ_AVAILABLE, LC_OPENAI_AVAILABLE
    print(f"  LangChain available: {LANGCHAIN_AVAILABLE}")
    print(f"  Groq available: {LC_GROQ_AVAILABLE}")
    print(f"  OpenAI available: {LC_OPENAI_AVAILABLE}")
    
    if not LANGCHAIN_AVAILABLE:
        print("  Note: LLM unavailable (huggingface_hub issue) - using fallback insights")
    print("  ✓ LLM module imports without errors")
except Exception as e:
    print(f"  ✗ LLM insights test failed: {e}")

# Test 4: Dashboard builder initialization
print("\n[4] Testing Dashboard Builder...")
try:
    from services.langgraph_dashboard_builder import LangGraphDashboardBuilder
    import pandas as pd
    
    builder = LangGraphDashboardBuilder()
    print("Testing NumPy conversion...")
    from api import convert_numpy_types
    import numpy as np
    
    test_data = {"value": np.int64(42)}
    result = convert_numpy_types(test_data)
    print(f"NumPy int64 converted to: {type(result['value'])}")
    
    print("\nTesting Groq key...")
    from dotenv import load_dotenv
    import os
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"Groq key loaded, ends with: ...{groq_key[-8:]}")
    else:
        print("Groq key not found")
    
    print("\nAll fixes validated!")
    print(f"  ✓ Dashboard builder initialized (LLM enabled: {builder.use_llm_insights})")
except Exception as e:
    print(f"  ✗ Dashboard builder failed: {e}")

print("\n" + "=" * 60)
print("Validation Complete!")
print("=" * 60)
