from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import json
import os
import aiofiles
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import asyncio

from services.data_processor import DataProcessor
from services.ai_agent import AIAgent
from services.chart_generator import ChartGenerator
from services.dashboard_builder import DashboardBuilder
from services.mcp_dashboard_server import DashboardMCPInterface

# Import new LangGraph-powered services
from services.langgraph_dashboard_builder import LangGraphDashboardBuilder
from services.langgraph_chart_generator import LangGraphChartGenerator
from services.langgraph_agents import LangGraphAgentOrchestrator


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


router = APIRouter(prefix="/api", tags=["EDA"])

# In-memory storage for uploaded files (use database in production)
uploaded_files = {}


def initialize_uploaded_files():
    """Initialize uploaded_files from existing files in uploads directory"""
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.endswith(".csv"):
                # Extract file_id from filename (format: {file_id}_{original_name}.csv)
                if "_" in filename:
                    file_id = filename.split("_")[0]
                    file_path = os.path.join(uploads_dir, filename)
                    original_name = (
                        "_".join(filename.split("_")[1:]).replace(".csv", "") + ".csv"
                    )

                    # Get file modification time as upload time
                    upload_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Try reading basic metadata
                    shape = None
                    columns = None
                    dtypes = None
                    try:
                        df_meta = pd.read_csv(file_path, nrows=5)
                        columns = df_meta.columns.tolist()
                        # Get dtypes by reading a sample
                        dtypes = df_meta.dtypes.astype(str).to_dict()
                        # Get full shape efficiently by counting lines
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            row_count = sum(1 for _ in f) - 1  # minus header
                        shape = (max(row_count, 0), len(columns or []))
                    except Exception:
                        pass

                    uploaded_files[file_id] = {
                        "file_path": file_path,
                        "filename": original_name,
                        "original_filename": original_name,
                        "upload_time": upload_time,
                        "shape": shape,
                        "columns": columns,
                        "dtypes": dtypes,
                    }


# Initialize from existing files
initialize_uploaded_files()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file for EDA processing"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    file_id = str(uuid.uuid4())
    file_path = f"uploads/{file_id}_{file.filename}"

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # Load and validate CSV
    try:
        df = pd.read_csv(file_path)

        # Store file metadata
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_time": datetime.now(),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        return {
            "file_id": file_id,
            "filename": file.filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": df.head().to_dict("records"),
        }

    except Exception as e:
        # Clean up file if CSV parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")


@router.get("/file/{file_id}/info")
async def get_file_info(file_id: str):
    """Get basic information about uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    processor = DataProcessor()
    basic_info = processor.get_basic_info(df)

    return basic_info


@router.get("/files/list")
async def list_uploaded_files():
    """Debug endpoint to list all available files"""
    return {
        "uploaded_files_count": len(uploaded_files),
        "uploaded_files": {
            file_id: info["original_filename"]
            for file_id, info in uploaded_files.items()
        },
        "uploads_directory": os.listdir("uploads") if os.path.exists("uploads") else [],
    }


@router.post("/process")
async def process_data(
    file_id: str = Form(...),
    operation: str = Form(...),  # 'clean', 'transform', 'classify', 'visualize'
    mode: str = Form(...),  # 'manual', 'ai'
    options: Optional[str] = Form(None),  # JSON string of options
):
    """Process data based on operation and mode"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    # Parse options if provided
    processed_options = json.loads(options) if options else {}

    processor = DataProcessor()
    chart_generator = ChartGenerator()

    try:
        if mode == "ai":
            ai_agent = AIAgent()
            result = await ai_agent.process_data(df, operation, processed_options)
        else:
            # Manual mode processing
            if operation == "clean":
                result = processor.clean_data(df, processed_options)
            elif operation == "transform":
                result = processor.transform_data(df, processed_options)
            elif operation == "classify":
                result = processor.classify_data(df, processed_options)
            elif operation == "visualize":
                result = chart_generator.generate_charts(df, processed_options)
            else:
                raise HTTPException(status_code=400, detail="Invalid operation")

        # Convert NumPy types to native Python types before returning
        return convert_numpy_types(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/charts/{file_id}")
async def get_charts(file_id: str, chart_types: Optional[str] = None):
    """Generate charts for visualization using LangGraph intelligent chart generation"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Use new LangGraph chart generator
        langgraph_chart_gen = LangGraphChartGenerator()
        result = await langgraph_chart_gen.generate_charts(
            df=df,
            chart_purpose="exploration",
            target_audience="analyst",
            max_charts=8
        )

        if result["success"]:
            # Convert LangGraph chart format to legacy format for compatibility
            legacy_charts = []
            for chart in result["charts"]:
                if chart.get("status") == "success" and "chart_data" in chart:
                    chart_data = chart["chart_data"]
                    
                    # Ensure data is in JSON string format (frontend expects this)
                    if "plotly_json" in chart_data:
                        # Use plotly_json if available (already a string)
                        data_string = chart_data["plotly_json"]
                    elif "data" in chart_data:
                        # Convert data dict to JSON string
                        data_obj = chart_data["data"]
                        data_string = json.dumps(data_obj) if isinstance(data_obj, dict) else data_obj
                    else:
                        # Fallback: convert entire chart_data to JSON
                        data_string = json.dumps(chart_data)
                    
                    legacy_charts.append({
                        "type": chart["chart_type"],
                        "config": chart.get("config", {}),
                        "data": data_string,  # JSON string format
                        "id": chart.get("id", ""),
                        "title": chart.get("config", {}).get("title", chart["chart_type"].replace("_", " ").title()),
                        "description": chart.get("purpose", ""),
                        "purpose": chart.get("purpose", ""),
                        "priority": chart.get("priority", "medium")
                    })

            return {
                "charts": convert_numpy_types(legacy_charts),
                "metadata": {
                    "generation_method": "langgraph_ai",
                    "total_charts": len(legacy_charts),
                    "data_characteristics": result.get("data_characteristics", {}),
                    "chart_recommendations": result.get("chart_recommendations", [])
                }
            }
        else:
            # Fallback to original chart generator
            chart_generator = ChartGenerator()
            charts = chart_generator.generate_all_charts(df, chart_types)
            return {"charts": charts}

    except Exception as e:
        # Fallback to original implementation on error
        try:
            chart_generator = ChartGenerator()
            charts = chart_generator.generate_all_charts(df, chart_types)
            return {
                "charts": charts,
                "metadata": {
                    "generation_method": "fallback_legacy",
                    "error_note": f"LangGraph failed: {str(e)}"
                }
            }
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(fallback_error)}")


@router.get("/insights/{file_id}")
async def get_ai_insights(file_id: str):
    """Get AI-generated insights about the dataset using LangGraph agents"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Use new LangGraph agent orchestrator
        langgraph_orchestrator = LangGraphAgentOrchestrator()
        result = await langgraph_orchestrator.process_data_to_json(df)

        if result["success"]:
            # Generate insights from the data analysis
            insights = [
                f"Dataset contains {len(df)} records across {len(df.columns)} variables",
                f"Data quality score: {result.get('quality_score', 'N/A')}%",
                f"Processing completed with {len(result.get('processing_steps', []))} steps"
            ]

            # Add data-specific insights
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numerical_cols) > 0:
                insights.append(f"Found {len(numerical_cols)} numerical variables for quantitative analysis")
            
            if len(categorical_cols) > 0:
                insights.append(f"Identified {len(categorical_cols)} categorical variables for segmentation")

            missing_percent = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            if missing_percent > 0:
                insights.append(f"Data completeness: {100-missing_percent:.1f}% (consider handling missing values)")
            else:
                insights.append("Excellent data completeness with no missing values")

            return {
                "insights": convert_numpy_types(insights),
                "metadata": {
                    "generation_method": "langgraph_agent",
                    "data_summary": result.get("data_summary", {}),
                    "processing_steps": result.get("processing_steps", [])
                }
            }
        else:
            # Fallback to original AI agent
            ai_agent = AIAgent()
            insights = await ai_agent.generate_insights(df)
            return {"insights": insights}

    except Exception as e:
        # Fallback to original implementation on error
        try:
            ai_agent = AIAgent()
            insights = await ai_agent.generate_insights(df)
            return {
                "insights": insights,
                "metadata": {
                    "generation_method": "fallback_legacy",
                    "error_note": f"LangGraph failed: {str(e)}"
                }
            }
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(fallback_error)}")


@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]

    # Remove file from disk
    if os.path.exists(file_info["file_path"]):
        os.remove(file_info["file_path"])

    # Remove from memory
    del uploaded_files[file_id]

    return {"message": "File deleted successfully"}


@router.post("/cleanup-session")
async def cleanup_session():
    """Clean up all uploaded files and session data"""
    try:
        deleted_count = 0
        for file_id, file_info in list(uploaded_files.items()):
            try:
                # Remove file from disk
                if os.path.exists(file_info["file_path"]):
                    os.remove(file_info["file_path"])
                deleted_count += 1
            except OSError:
                pass  # File might already be deleted

        # Clear all from memory
        uploaded_files.clear()

        return {
            "success": True,
            "message": f"Session cleaned up successfully. {deleted_count} files removed.",
            "deleted_count": deleted_count,
        }
    except Exception as e:
        return {"success": False, "message": f"Error during cleanup: {str(e)}"}


# === AUTOMATED DASHBOARD ENDPOINTS ===


@router.post("/dashboard/auto-generate")
async def auto_generate_dashboard(
    file_id: str = Form(...), business_context: Optional[str] = Form(None)
):
    """Automatically generate the optimal dashboard for a dataset using MCP"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.auto_generate_dashboard(
            file_path, business_context or ""
        )

        if result["success"]:
            return convert_numpy_types(
                {
                    "success": True,
                    "dashboard": result["dashboard"],
                    "recommendations": result.get("recommendations", []),
                    "data_profile": result.get("data_profile", {}),
                    "charts_generated": result.get("charts_generated", 0),
                    "insights_generated": result.get("insights_generated", 0),
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/generate-interactive")
async def generate_interactive_dashboard(
    file_id: str = Form(...),
    include_raw_data: bool = Form(False),
    business_context: str = Form(""),
):
    """Generate an AI-powered interactive dashboard using an agentic pipeline"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Generate charts using chart generator
        chart_generator = ChartGenerator()
        charts = chart_generator.generate_all_charts(df, "all")

        # Prepare summary statistics
        data_processor = DataProcessor()
        summary_stats = {
            "total_rows": len(df),
            "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
            "categorical_columns": df.select_dtypes(
                include=["object"]
            ).columns.tolist(),
            "column_stats": {},
            "missing_data": {
                "percentage": float((df.isnull().sum().sum() / df.size) * 100)
            },
        }

        # Add column statistics with proper type conversion
        for col in summary_stats["numeric_columns"]:
            if not df[col].isnull().all():  # Only if column has data
                summary_stats["column_stats"][col] = {
                    "mean": (
                        float(df[col].mean()) if not pd.isna(df[col].mean()) else 0.0
                    ),
                    "std": float(df[col].std()) if not pd.isna(df[col].std()) else 0.0,
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else 0.0,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else 0.0,
                }

        # Prepare raw data for filtering (if requested)
        raw_data = None
        if include_raw_data:
            # Convert dataframe data to native Python types
            df_sample = df.head(1000)  # Limit to first 1000 rows
            raw_data = {
                "data": convert_numpy_types(df_sample.to_dict("records")),
                "columns": df.columns.tolist(),
                "numeric_columns": summary_stats["numeric_columns"],
                "categorical_columns": summary_stats["categorical_columns"],
                "unique_categories": {},
                "unique_dates": [],
            }

            # Add unique values for filtering
            for col in summary_stats["categorical_columns"][
                :5
            ]:  # Limit to 5 categorical columns
                unique_vals = (
                    df[col].dropna().unique()[:20].tolist()
                )  # Limit to 20 unique values
                raw_data["unique_categories"][col] = convert_numpy_types(unique_vals)

        # Build AI-powered interactive dashboard
        dashboard_builder = DashboardBuilder()
        dashboard_html = await dashboard_builder.build_ai_interactive_dashboard(
            dataset_name=file_info["filename"],
            df=df,
            charts=convert_numpy_types(charts),
            summary_stats=convert_numpy_types(summary_stats),
            raw_data=convert_numpy_types(raw_data) if raw_data else None,
            business_context=business_context,
        )

        return {
            "success": True,
            "dashboard": {
                "id": str(uuid.uuid4()),
                "html": dashboard_html,
                "type": "ai_interactive",
                "charts_count": len(charts),
                "features": {
                    "ai_powered": True,
                    "dynamic_filtering": True,
                    "kpi_cards": True,
                    "responsive_layout": True,
                    "real_time_updates": include_raw_data,
                    "agentic_ai": True,
                },
                "metadata": convert_numpy_types(
                    {
                        "dataset_name": file_info["filename"],
                        "total_rows": len(df),
                        "total_columns": len(df.columns),
                        "dataset_shape": [len(df), len(df.columns)],
                        "dashboard_sections": 6,
                        "interactive_features": [
                            "ai_insights",
                            "filters",
                            "kpis",
                            "drill_down",
                        ],
                        "generated_at": datetime.now().isoformat(),
                    }
                ),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Interactive dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/generate")
async def generate_dashboard(
    file_id: str = Form(...),
    dashboard_type: str = Form(
        "auto"
    ),  # auto, executive_summary, data_quality, exploratory
    customizations: Optional[str] = Form(None),  # JSON string
):
    """Generate specific type of dashboard"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    # Parse customizations
    custom_options = json.loads(customizations) if customizations else {}

    try:
        dashboard_builder = DashboardBuilder()

        # Analyze requirements
        requirements = await dashboard_builder.analyze_dashboard_requirements(
            df, dashboard_type
        )

        # Generate dashboard
        dashboard = await dashboard_builder.generate_dashboard(
            df, requirements, custom_options
        )

        return {
            "success": True,
            "dashboard": {
                "id": dashboard["id"],
                "type": dashboard["type"],
                "html": dashboard["html"],
                "metadata": dashboard["metadata"],
            },
            "charts_generated": len(dashboard["charts"]),
            "insights_generated": len(dashboard["insights"]),
            "requirements": requirements,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )


@router.post("/dashboard/analyze-requirements")
async def analyze_dashboard_requirements(file_id: str = Form(...)):
    """Analyze dataset and get dashboard recommendations"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        dashboard_builder = DashboardBuilder()
        requirements = await dashboard_builder.analyze_dashboard_requirements(df)

        return convert_numpy_types(
            {
                "success": True,
                "requirements": requirements,
                "dataset_info": {
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict(),
                },
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Requirements analysis failed: {str(e)}"
        )


@router.get("/dashboard/templates")
async def get_dashboard_templates():
    """Get available dashboard templates and their descriptions"""
    dashboard_interface = DashboardMCPInterface()
    result = await dashboard_interface.mcp_server.handle_request("get_templates", {})

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])


@router.post("/dashboard/recommendations")
async def get_dashboard_recommendations(
    file_id: str = Form(...), business_context: Optional[str] = Form(None)
):
    """Get AI-powered dashboard recommendations"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.get_dashboard_recommendations(
            file_path, business_context or ""
        )

        if result["success"]:
            return convert_numpy_types(result)
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get specific dashboard by ID"""
    try:
        dashboard_builder = DashboardBuilder()
        dashboard = await dashboard_builder.get_dashboard(dashboard_id)

        if dashboard:
            return {"success": True, "dashboard": dashboard}
        else:
            raise HTTPException(status_code=404, detail="Dashboard not found")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@router.get("/dashboard/{dashboard_id}/export")
async def export_dashboard(dashboard_id: str, format: str = "html"):
    """Export dashboard in specified format"""
    try:
        dashboard_builder = DashboardBuilder()
        export_result = await dashboard_builder.export_dashboard(dashboard_id, format)

        return {"success": True, "export": export_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/dashboards")
async def list_dashboards():
    """List all created dashboards"""
    try:
        dashboard_builder = DashboardBuilder()
        dashboards = await dashboard_builder.list_dashboards()

        return {
            "success": True,
            "dashboards": dashboards,
            "total_count": len(dashboards),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list dashboards: {str(e)}"
        )


@router.post("/dashboard/generate-all-types")
async def generate_all_dashboard_types(file_id: str = Form(...)):
    """Generate all three dashboard types for comparison"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    file_path = file_info["file_path"]

    try:
        dashboard_interface = DashboardMCPInterface()
        result = await dashboard_interface.generate_all_dashboard_types(file_path)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to generate dashboards")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard generation failed: {str(e)}"
        )


# === NEW LANGGRAPH-POWERED ENDPOINTS ===

@router.post("/langgraph/dashboard/generate")
async def langgraph_generate_dashboard(
    file_id: str = Form(...),
    dashboard_type: str = Form("exploratory"),  # executive, data_quality, exploratory, correlation, time_series
    user_context: str = Form(""),
    target_audience: str = Form("analyst"),  # executive, analyst, data_scientist, business_user
):
    """Generate dashboard using LangGraph AI agent workflows"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Initialize LangGraph dashboard builder
        langgraph_builder = LangGraphDashboardBuilder()
        
        # Generate dashboard using LangGraph workflow
        result = await langgraph_builder.build_dashboard(
            df=df,
            dashboard_type=dashboard_type,
            user_context=user_context,
            target_audience=target_audience
        )

        if result["success"]:
            return convert_numpy_types({
                "success": True,
                "dashboard": {
                    "id": result["session_id"],
                    "type": dashboard_type,
                    "html": result["dashboard_html"],
                    "metadata": {
                        "dashboard_type": result["dashboard_type"],
                        "target_audience": target_audience,
                        "chart_count": len(result.get("chart_specifications", [])),
                        "insights_count": len(result.get("insights", [])),
                        "generation_timestamp": result["generation_timestamp"],
                        "layout_config": result.get("layout_config", {}),
                        "json_data_size": len(str(result.get("json_data", {})))
                    }
                },
                "charts_generated": len(result.get("chart_specifications", [])),
                "insights": result.get("insights", []),
                "llm_insights": result.get("llm_insights", {}),  # NEW: Structured LLM insights
                "workflow_type": "langgraph_ai_agent"
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Dashboard generation failed"))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LangGraph dashboard generation failed: {str(e)}"
        )


@router.post("/langgraph/charts/generate")
async def langgraph_generate_charts(
    file_id: str = Form(...),
    chart_purpose: str = Form("exploration"),  # exploration, presentation, analysis
    target_audience: str = Form("analyst"),
    max_charts: int = Form(8)
):
    """Generate charts using LangGraph intelligent chart recommendation"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Initialize LangGraph chart generator
        langgraph_chart_gen = LangGraphChartGenerator()
        
        # Generate charts using AI workflow
        result = await langgraph_chart_gen.generate_charts(
            df=df,
            chart_purpose=chart_purpose,
            target_audience=target_audience,
            max_charts=max_charts
        )

        if result["success"]:
            return convert_numpy_types({
                "success": True,
                "charts": result["charts"],
                "session_id": result["session_id"],
                "data_characteristics": result["data_characteristics"],
                "chart_recommendations": result["chart_recommendations"],
                "performance_metrics": result["performance_metrics"],
                "generation_timestamp": result["generation_timestamp"],
                "workflow_type": "langgraph_intelligent_charts"
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Chart generation failed"))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LangGraph chart generation failed: {str(e)}"
        )


@router.post("/langgraph/data/process")
async def langgraph_process_data(
    file_id: str = Form(...),
    operation_type: str = Form("comprehensive_analysis")  # comprehensive_analysis, json_conversion, data_quality
):
    """Process data using LangGraph AI agent workflows"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Initialize LangGraph agent orchestrator
        langgraph_orchestrator = LangGraphAgentOrchestrator()
        
        if operation_type == "json_conversion":
            # Convert data to optimized JSON structure
            result = await langgraph_orchestrator.process_data_to_json(df)
        elif operation_type == "dashboard_generation":
            # Generate dashboard using agent workflow
            result = await langgraph_orchestrator.generate_dashboard(
                df=df,
                dashboard_type="exploratory",
                user_context="",
                target_audience="analyst"
            )
        else:
            # Default comprehensive analysis
            result = await langgraph_orchestrator.process_data_to_json(df)

        if result["success"]:
            return convert_numpy_types({
                "success": True,
                "result": result,
                "operation_type": operation_type,
                "workflow_type": "langgraph_agent_processing"
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Data processing failed"))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LangGraph data processing failed: {str(e)}"
        )


@router.get("/langgraph/chart/single/{file_id}")
async def langgraph_generate_single_chart(
    file_id: str,
    chart_type: str = "histogram",  # histogram, scatter_plot, bar_chart, correlation_heatmap, etc.
    columns: str = "",  # comma-separated column names
    title: str = ""
):
    """Generate a single chart using LangGraph chart builder"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Parse columns
        column_list = [col.strip() for col in columns.split(",") if col.strip()] if columns else []
        
        # If no columns specified, auto-select based on chart type
        if not column_list:
            if chart_type == "histogram":
                numerical_cols = df.select_dtypes(include=[np.number]).columns
                column_list = [numerical_cols[0]] if len(numerical_cols) > 0 else []
            elif chart_type == "scatter_plot":
                numerical_cols = df.select_dtypes(include=[np.number]).columns
                column_list = numerical_cols[:2].tolist() if len(numerical_cols) >= 2 else []
            elif chart_type == "bar_chart":
                categorical_cols = df.select_dtypes(include=['object']).columns
                column_list = [categorical_cols[0]] if len(categorical_cols) > 0 else []

        # Initialize LangGraph chart generator
        langgraph_chart_gen = LangGraphChartGenerator()
        
        # Generate single chart
        result = langgraph_chart_gen.generate_single_chart(
            df=df,
            chart_type=chart_type,
            columns=column_list,
            config={"title": title} if title else None
        )

        if result["success"]:
            return convert_numpy_types({
                "success": True,
                "chart": result["chart"],
                "chart_type": chart_type,
                "columns_used": column_list,
                "workflow_type": "langgraph_single_chart"
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Single chart generation failed"))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LangGraph single chart generation failed: {str(e)}"
        )


@router.get("/langgraph/dashboard/types")
async def get_langgraph_dashboard_types():
    """Get available LangGraph dashboard types and their descriptions"""
    return {
        "success": True,
        "dashboard_types": {
            "executive": {
                "name": "Executive Summary",
                "description": "High-level KPIs and business metrics for executive audiences",
                "features": ["KPI cards", "trend analysis", "business insights", "minimal complexity"],
                "target_audience": ["executive", "business_user"],
                "use_cases": ["board presentations", "executive reports", "strategic overview"]
            },
            "data_quality": {
                "name": "Data Quality Assessment", 
                "description": "Comprehensive data quality analysis and recommendations",
                "features": ["completeness analysis", "outlier detection", "consistency checks", "quality recommendations"],
                "target_audience": ["analyst", "data_scientist"],
                "use_cases": ["data validation", "quality assessment", "preprocessing guidance"]
            },
            "exploratory": {
                "name": "Exploratory Data Analysis",
                "description": "Comprehensive EDA with distributions, correlations, and patterns",
                "features": ["distribution analysis", "correlation matrix", "pattern detection", "statistical insights"],
                "target_audience": ["analyst", "data_scientist"],
                "use_cases": ["data exploration", "hypothesis generation", "feature analysis"]
            },
            "correlation": {
                "name": "Correlation Analysis",
                "description": "Deep dive into variable relationships and correlations",
                "features": ["correlation matrix", "relationship analysis", "multicollinearity detection", "network analysis"],
                "target_audience": ["data_scientist", "analyst"],
                "use_cases": ["feature selection", "relationship mapping", "predictive modeling prep"]
            },
            "time_series": {
                "name": "Time Series Analysis",
                "description": "Temporal pattern analysis and trend detection",
                "features": ["trend analysis", "seasonality detection", "forecasting potential", "temporal insights"],
                "target_audience": ["analyst", "data_scientist"],
                "use_cases": ["time series forecasting", "trend analysis", "temporal patterns"]
            }
        },
        "target_audiences": {
            "executive": "Business leaders and executives",
            "analyst": "Data analysts and business analysts", 
            "data_scientist": "Data scientists and ML engineers",
            "business_user": "General business users"
        },
        "chart_purposes": {
            "exploration": "Data exploration and discovery",
            "presentation": "Executive and stakeholder presentations",
            "analysis": "Detailed analytical investigation"
        }
    }


@router.post("/langgraph/dashboard/requirements")
async def analyze_langgraph_requirements(file_id: str = Form(...)):
    """Analyze dataset using LangGraph agents and provide dashboard recommendations"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")

    file_info = uploaded_files[file_id]
    df = pd.read_csv(file_info["file_path"])

    try:
        # Initialize LangGraph chart generator to analyze data characteristics
        langgraph_chart_gen = LangGraphChartGenerator()
        
        # Analyze data characteristics
        from services.langgraph_chart_generator import DataCharacteristicsAnalyzer
        analyzer = DataCharacteristicsAnalyzer()
        data_characteristics = analyzer.analyze_data_structure(df)

        # Get chart recommendations
        from services.langgraph_chart_generator import ChartRecommendationEngine
        rec_engine = ChartRecommendationEngine()
        chart_recommendations = rec_engine.recommend_charts(
            data_characteristics, 
            chart_purpose="exploration",
            target_audience="analyst"
        )

        return convert_numpy_types({
            "success": True,
            "file_info": {
                "filename": file_info["filename"],
                "shape": df.shape,
                "columns": df.columns.tolist()
            },
            "data_characteristics": data_characteristics,
            "chart_recommendations": chart_recommendations,
            "dashboard_recommendations": {
                "primary_type": "exploratory" if len(data_characteristics["column_types"]["numerical"]) > 2 else "executive",
                "alternative_types": ["data_quality", "correlation"] if len(data_characteristics["column_types"]["numerical"]) > 3 else ["data_quality"],
                "recommended_audience": "analyst" if len(df.columns) > 5 else "business_user",
                "complexity_level": "advanced" if len(df.columns) > 10 else "intermediate"
            },
            "workflow_type": "langgraph_requirements_analysis"
        })

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LangGraph requirements analysis failed: {str(e)}"
        )


# === ERROR HANDLING AND UTILITY FUNCTIONS ===

def handle_langgraph_error(operation_name: str, error: Exception, fallback_func=None):
    """Centralized error handling for LangGraph operations"""
    error_msg = f"LangGraph {operation_name} failed: {str(error)}"
    
    # Log the error
    import logging
    logger = logging.getLogger(__name__)
    logger.error(error_msg, exc_info=True)
    
    # If fallback function provided, try it
    if fallback_func:
        try:
            result = fallback_func()
            result["metadata"] = result.get("metadata", {})
            result["metadata"]["generation_method"] = "fallback_legacy"
            result["metadata"]["langgraph_error"] = str(error)
            return result
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500, 
                detail=f"{operation_name} failed (LangGraph: {str(error)}, Fallback: {str(fallback_error)})"
            )
    else:
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/langgraph/test")
async def test_langgraph_services():
    """Test endpoint to verify LangGraph services are working"""
    try:
        # Create test DataFrame
        test_data = {
            'numerical_col1': [1, 2, 3, 4, 5],
            'numerical_col2': [2, 4, 6, 8, 10],
            'categorical_col': ['A', 'B', 'A', 'C', 'B']
        }
        test_df = pd.DataFrame(test_data)
        
        # Test LangGraph services
        test_results = {}
        
        # Test LangGraph agent orchestrator
        try:
            langgraph_orchestrator = LangGraphAgentOrchestrator()
            agent_result = await langgraph_orchestrator.process_data_to_json(test_df)
            test_results["agent_orchestrator"] = {
                "status": "success" if agent_result["success"] else "failed",
                "details": agent_result
            }
        except Exception as e:
            test_results["agent_orchestrator"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test LangGraph chart generator  
        try:
            langgraph_chart_gen = LangGraphChartGenerator()
            chart_result = await langgraph_chart_gen.generate_charts(
                df=test_df,
                chart_purpose="exploration",
                target_audience="analyst",
                max_charts=3
            )
            test_results["chart_generator"] = {
                "status": "success" if chart_result["success"] else "failed",
                "charts_generated": len(chart_result.get("charts", [])) if chart_result["success"] else 0
            }
        except Exception as e:
            test_results["chart_generator"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test LangGraph dashboard builder
        try:
            langgraph_builder = LangGraphDashboardBuilder()
            dashboard_result = await langgraph_builder.build_dashboard(
                df=test_df,
                dashboard_type="exploratory",
                user_context="test dashboard",
                target_audience="analyst"
            )
            test_results["dashboard_builder"] = {
                "status": "success" if dashboard_result["success"] else "failed",
                "dashboard_generated": bool(dashboard_result.get("dashboard_html")) if dashboard_result["success"] else False
            }
        except Exception as e:
            test_results["dashboard_builder"] = {
                "status": "error", 
                "error": str(e)
            }
        
        # Overall status
        all_success = all(result["status"] == "success" for result in test_results.values())
        
        return {
            "success": all_success,
            "message": "All LangGraph services working" if all_success else "Some LangGraph services have issues",
            "test_results": test_results,
            "test_data_shape": test_df.shape,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"LangGraph service test failed: {str(e)}"
        )


@router.post("/langgraph/configure")
async def configure_langgraph_services(
    chart_generation_config: Optional[str] = Form(None),  # JSON config for chart generation
    dashboard_config: Optional[str] = Form(None),         # JSON config for dashboard generation  
    agent_config: Optional[str] = Form(None)              # JSON config for agent orchestrator
):
    """Configure LangGraph services with custom parameters"""
    try:
        configuration_applied = {}
        
        # Parse configurations
        chart_config = json.loads(chart_generation_config) if chart_generation_config else {}
        dash_config = json.loads(dashboard_config) if dashboard_config else {}
        agent_cfg = json.loads(agent_config) if agent_config else {}
        
        # Apply chart generation configuration
        if chart_config:
            configuration_applied["chart_generation"] = {
                "max_charts": chart_config.get("max_charts", 8),
                "default_purpose": chart_config.get("default_purpose", "exploration"),
                "default_audience": chart_config.get("default_audience", "analyst"),
                "chart_priorities": chart_config.get("chart_priorities", ["high", "medium"]),
                "performance_optimization": chart_config.get("performance_optimization", True)
            }
        
        # Apply dashboard configuration
        if dash_config:
            configuration_applied["dashboard_builder"] = {
                "default_type": dash_config.get("default_type", "exploratory"),
                "default_audience": dash_config.get("default_audience", "analyst"),
                "styling_preferences": dash_config.get("styling_preferences", {"color_scheme": "modern"}),
                "layout_optimization": dash_config.get("layout_optimization", True),
                "include_interactivity": dash_config.get("include_interactivity", True)
            }
        
        # Apply agent orchestrator configuration
        if agent_cfg:
            configuration_applied["agent_orchestrator"] = {
                "processing_mode": agent_cfg.get("processing_mode", "comprehensive"),
                "quality_threshold": agent_cfg.get("quality_threshold", 0.8),
                "enable_caching": agent_cfg.get("enable_caching", True),
                "max_processing_time": agent_cfg.get("max_processing_time", 300)  # seconds
            }
        
        return {
            "success": True,
            "message": "LangGraph services configured successfully",
            "configuration_applied": configuration_applied,
            "timestamp": datetime.now().isoformat(),
            "services_configured": list(configuration_applied.keys())
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JSON configuration: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Configuration failed: {str(e)}"
        )
