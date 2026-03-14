# LLM-Powered Dashboard Generator

## Overview

This project now features an **intelligent, LLM-driven dashboard code generator** built with LangGraph. Instead of using static templates, the system:

1. **Analyzes** your dataset to understand its structure and patterns
2. **Generates** complete, production-ready HTML/JSX dashboard code using LLM (with deterministic fallback)
3. **Verifies** the generated code for quality, completeness, and functionality
4. **Produces** interactive, responsive dashboards similar to Power BI/Tableau

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Initialize Session                                        │
│  2. Convert Data to JSON                                      │
│  3. Analyze Dashboard Requirements                            │
│  4. Generate Layout Structure                                 │
│  5. Create Chart Specifications                               │
│  6. Generate Insights                                         │
│  7. ┌───────────────────────────────────────┐                │
│     │  GENERATE CODE VIA LLM                 │                │
│     │  • Structured prompt with context      │                │
│     │  • Dataset analysis & chart specs      │                │
│     │  • Production-ready requirements       │                │
│     │  • Fallback to deterministic generator │                │
│     └───────────────────────────────────────┘                │
│  8. ┌───────────────────────────────────────┐                │
│     │  VERIFY GENERATED CODE                 │                │
│     │  • Heuristic checks (structure, etc.)  │                │
│     │  • Chart integration validation        │                │
│     │  • Optional LLM semantic review        │                │
│     └───────────────────────────────────────┘                │
│  9. Finalize Dashboard                                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🎨 **Intelligent Code Generation**

- **LLM-Powered**: Uses GPT-4/GPT-3.5 to generate custom dashboard code tailored to your data
- **Fallback Safety**: Automatically falls back to deterministic generator if LLM unavailable
- **Format Flexibility**: Supports both HTML (standalone) and JSX (React component) output

### 📊 **Chart Integration**

- Automatic Plotly.js chart configuration
- Deterministic chart container IDs (`chart_0`, `chart_1`, etc.)
- Responsive, interactive visualizations
- Multiple chart types (scatter, histogram, heatmap, bar, line, etc.)

### ✅ **Code Verification**

- **Heuristic Checks**: Structure, styling, interactivity, data integration
- **LLM Review** (optional): Semantic code quality analysis with scoring
- **Comprehensive Reports**: Detailed verification with passed checks, warnings, and critical issues

### 🎯 **Dashboard Types**

1. **Executive**: High-level KPIs, trends, business metrics
2. **Data Quality**: Missing data, outliers, consistency checks
3. **Exploratory**: Comprehensive analysis with correlations, distributions

## Setup & Configuration

### 1. Install Dependencies

```powershell
# Navigate to server directory
cd server

# Install Python packages
pip install -r requirements.txt
```

**Key packages:**

- `langgraph==0.2.32` - Workflow orchestration
- `langchain==0.3.5` - LLM integration
- `numpy>=1.22.4,<2.3.0` - NumPy (SciPy compatible)
- `plotly==5.17.0` - Visualization library

### 2. Configure LLM (Optional)

To enable LLM-based generation, set your OpenAI API key:

```powershell
# PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Optional: Use GPT-4 instead of GPT-3.5-turbo
$env:USE_GPT4 = "true"
```

**Without API Key**: The system automatically falls back to the deterministic code generator (still produces high-quality dashboards).

### 3. Run Tests

```powershell
# Test dashboard generation with sample data
python test_dashboard_generation.py
```

This will:

- Load sample datasets from `uploads/`
- Generate 3 dashboard types (exploratory, executive, data_quality)
- Save HTML files to `generated_dashboards/`
- Show verification reports

## Usage

### Basic Usage

```python
import pandas as pd
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder

# Load your data
df = pd.read_csv("your_data.csv")

# Create builder
builder = LangGraphDashboardBuilder()

# Generate dashboard
result = await builder.build_dashboard(
    df=df,
    dashboard_type="exploratory",  # or "executive", "data_quality"
    user_context="Sales analysis for Q4 2025",
    target_audience="analyst"
)

# Check result
if result["success"]:
    html_code = result["dashboard_html"]

    # Save to file
    with open("dashboard.html", "w") as f:
        f.write(html_code)

    # Get verification report
    verification = result.get("verification_report", {})
    print(f"Status: {verification.get('overall_status')}")
    print(f"Score: {verification.get('llm_review', {}).get('score')}/100")
else:
    print(f"Error: {result['error']}")
```

### Integration with FastAPI

```python
from fastapi import FastAPI, UploadFile
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder
import pandas as pd

app = FastAPI()

@app.post("/api/generate-dashboard")
async def generate_dashboard(
    file: UploadFile,
    dashboard_type: str = "exploratory"
):
    # Read uploaded CSV
    df = pd.read_csv(file.file)

    # Generate dashboard
    builder = LangGraphDashboardBuilder()
    result = await builder.build_dashboard(
        df=df,
        dashboard_type=dashboard_type,
        user_context=f"Analysis of {file.filename}",
        target_audience="analyst"
    )

    return {
        "success": result["success"],
        "dashboard_html": result.get("dashboard_html", ""),
        "verification": result.get("verification_report", {}),
        "insights": result.get("insights", [])
    }
```

## LLM Prompt Engineering

### Prompt Structure

The generator uses a comprehensive, structured prompt that includes:

1. **Role Definition**: Expert full-stack engineer specializing in data viz
2. **Output Format**: Explicit HTML or JSX format requirements
3. **Technical Requirements**:
   - Chart library (Plotly.js)
   - Layout specifications (CSS Grid)
   - Interactivity features
   - Responsive design
4. **Data Context**: Dataset metadata, columns, sample records
5. **Layout Configuration**: Grid structure, sections, styling
6. **Chart Specifications**: Detailed specs for each chart (type, columns, purpose)
7. **Insights**: Key findings to display
8. **Implementation Checklist**: Complete list of required features

### Example Prompt Excerpt

```
# ROLE
You are an expert full-stack engineer specializing in data visualization.
Generate a production-ready, interactive EXPLORATORY dashboard.

# TECHNICAL REQUIREMENTS
## Charts & Visualization
- Use Plotly.js (CDN: https://cdn.plot.ly/plotly-2.26.0.min.js)
- Each chart MUST have a unique ID (chart_0, chart_1, ...)
- Implement chart configurations based on specifications
- Make all charts fully responsive

## Layout & Styling
- Grid layout: 2 columns
- Use CSS Grid or Flexbox
- Color scheme: Modern, professional (#2563eb, #3b82f6)
- Ensure mobile responsiveness (768px, 1024px breakpoints)

...
```

## Verification System

### Heuristic Checks

The verifier performs automated checks:

- ✅ **Structure**: DOCTYPE, HTML/JSX tags, head/body sections
- ✅ **Charts**: Plotly integration, rendering calls, container IDs
- ✅ **Styling**: CSS presence, responsive design patterns
- ✅ **Interactivity**: Event handlers, functions
- ✅ **Data Integration**: Data variables, proper structure

### LLM Verification (Optional)

If enabled, the LLM reviewer:

1. Analyzes code quality, completeness, best practices
2. Returns a score (0-100)
3. Lists issues and strengths
4. Provides actionable summary

### Verification Report Example

```json
{
  "overall_status": "PASS",
  "critical_issues": [],
  "warnings": ["No event handlers detected"],
  "passed_checks": [
    "Code length adequate",
    "Valid HTML structure",
    "Plotly library integrated",
    "Chart containers found: chart_0, chart_1",
    "Styling present",
    "Responsive design patterns detected"
  ],
  "llm_review": {
    "valid": true,
    "score": 85,
    "issues": [],
    "strengths": [
      "Clean HTML structure",
      "Proper Plotly integration",
      "Responsive grid layout"
    ],
    "summary": "Well-structured dashboard with good chart integration"
  }
}
```

## Dashboard Types

### 1. Executive Dashboard

- **Purpose**: High-level business overview for executives
- **Features**:
  - KPI cards with trend indicators
  - Performance summary metrics
  - Business insights tailored to context
  - Clean, minimal design

### 2. Data Quality Dashboard

- **Purpose**: Data integrity and completeness assessment
- **Features**:
  - Missing data heatmaps
  - Outlier detection visualizations
  - Data type summaries
  - Quality score metrics
  - Improvement recommendations

### 3. Exploratory Dashboard

- **Purpose**: Comprehensive data analysis
- **Features**:
  - Correlation heatmaps
  - Distribution histograms
  - Scatter plots for relationships
  - Statistical summaries
  - Pattern detection

## Customization

### Extending Dashboard Types

Add new dashboard types by creating tools in `dashboard_tools.py`:

```python
class CustomDashboardTool:
    @staticmethod
    def analyze_custom_metrics(df: pd.DataFrame, context: str) -> Dict[str, Any]:
        # Your analysis logic
        return {
            "custom_metrics": [...],
            "custom_insights": [...]
        }

    @staticmethod
    def generate_custom_layout() -> Dict[str, Any]:
        return {
            "type": "custom",
            "grid_structure": {"columns": 3},
            "sections": [...]
        }
```

### Modifying LLM Prompt

Edit `_generate_code_via_llm()` in `langgraph_dashboard_builder.py`:

```python
prompt_lines = [
    "# Your custom instructions",
    "Generate a dashboard with...",
    # Add your specific requirements
]
```

## Troubleshooting

### Issue: NumPy Version Conflict

**Error**: `NumPy version >=1.22.4 and <2.3.0 is required`

**Solution**:

```powershell
pip install "numpy>=1.22.4,<2.3.0" --force-reinstall
```

### Issue: LangGraph Import Error

**Error**: `cannot import name 'ToolNode' from 'langgraph.prebuilt'`

**Solution**: Already fixed! The import has been removed as it was unused.

### Issue: LLM Generation Failing

**Symptoms**: Falls back to deterministic generator even with API key set

**Checks**:

1. Verify API key: `echo $env:OPENAI_API_KEY`
2. Check langchain version: `pip show langchain`
3. Review logs for specific error messages

**Solution**:

```powershell
# Reinstall langchain packages
pip install langchain langchain-openai --upgrade
```

### Issue: Dashboard Not Rendering Charts

**Symptoms**: HTML file opens but charts don't display

**Checks**:

1. Open browser console (F12) for JavaScript errors
2. Verify Plotly CDN is accessible
3. Check chart container IDs match rendering calls

**Solution**: Run verification on generated code to identify issues.

## Performance Considerations

### LLM Mode

- **Generation Time**: 10-30 seconds (depends on model and data size)
- **API Costs**: ~$0.01-0.05 per dashboard (GPT-3.5-turbo)
- **Quality**: High customization, context-aware layouts

### Fallback Mode

- **Generation Time**: <1 second
- **API Costs**: $0 (no API calls)
- **Quality**: Consistent, reliable, template-based

### Recommendations

- **Development**: Use fallback mode for fast iteration
- **Production**: Enable LLM for best quality, with fallback as safety net
- **High Volume**: Consider caching generated dashboards for similar datasets

## API Reference

### `LangGraphDashboardBuilder.build_dashboard()`

```python
async def build_dashboard(
    self,
    df: pd.DataFrame,              # Input DataFrame
    dashboard_type: str = "exploratory",  # "executive" | "data_quality" | "exploratory"
    user_context: str = "",        # Context for better generation
    target_audience: str = "analyst"  # Target user type
) -> Dict[str, Any]:
```

**Returns**:

```python
{
    "success": bool,
    "dashboard_html": str,         # Complete HTML code
    "session_id": str,
    "dashboard_type": str,
    "json_data": dict,             # Processed data
    "chart_specifications": list,  # Chart configs
    "insights": list,              # Generated insights
    "layout_config": dict,         # Layout structure
    "verification_report": dict,   # Verification results
    "generation_timestamp": str
}
```

## Contributing

### Adding New Chart Types

1. Add chart type to `ChartGenerationTools` in `langgraph_agents.py`
2. Implement Plotly configuration method
3. Update verification logic to recognize new chart type

### Improving Prompts

1. Test with various datasets
2. Identify common generation issues
3. Add specific instructions to prompt
4. Submit PR with before/after examples

## License

See main project LICENSE file.

## Support

For issues, questions, or feature requests:

- Open an issue on GitHub
- Review verification reports for debugging
- Check logs with `logging.DEBUG` enabled

---

**Built with**: LangGraph • LangChain • Plotly.js • FastAPI
