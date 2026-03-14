"""
MCP Server for Automated Dashboard Building
Provides model context protocol interface for dashboard automation
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from datetime import datetime
import os

from .dashboard_builder import DashboardBuilder, convert_numpy_types

class MCPDashboardServer:
    """MCP Server for automated dashboard building"""
    
    def __init__(self):
        self.dashboard_builder = DashboardBuilder()
        self.capabilities = {
            "tools": [
                {
                    "name": "analyze_requirements",
                    "description": "Analyze dataset and determine optimal dashboard requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to CSV file"},
                            "dashboard_type": {"type": "string", "enum": ["auto", "executive_summary", "data_quality", "exploratory"], "default": "auto"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "generate_dashboard",
                    "description": "Generate automated dashboard based on requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to CSV file"},
                            "dashboard_type": {"type": "string", "enum": ["auto", "executive_summary", "data_quality", "exploratory"], "default": "auto"},
                            "customizations": {"type": "object", "description": "Custom dashboard options"}
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "get_templates",
                    "description": "Get available dashboard templates",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "customize_dashboard",
                    "description": "Apply customizations to existing dashboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dashboard_id": {"type": "string", "description": "Dashboard ID"},
                            "customizations": {"type": "object", "description": "Customization options"}
                        },
                        "required": ["dashboard_id", "customizations"]
                    }
                },
                {
                    "name": "export_dashboard",
                    "description": "Export dashboard in specified format",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dashboard_id": {"type": "string", "description": "Dashboard ID"},
                            "format": {"type": "string", "enum": ["html", "json"], "default": "html"}
                        },
                        "required": ["dashboard_id"]
                    }
                },
                {
                    "name": "list_dashboards",
                    "description": "List all created dashboards",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "smart_dashboard_recommendation",
                    "description": "Get AI-powered dashboard recommendations based on data characteristics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to CSV file"},
                            "business_context": {"type": "string", "description": "Business context or use case"}
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        }
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        
        try:
            if method == "analyze_requirements":
                return await self._handle_analyze_requirements(params)
            elif method == "generate_dashboard":
                return await self._handle_generate_dashboard(params)
            elif method == "get_templates":
                return await self._handle_get_templates(params)
            elif method == "customize_dashboard":
                return await self._handle_customize_dashboard(params)
            elif method == "export_dashboard":
                return await self._handle_export_dashboard(params)
            elif method == "list_dashboards":
                return await self._handle_list_dashboards(params)
            elif method == "smart_dashboard_recommendation":
                return await self._handle_smart_recommendation(params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown method: {method}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": method
            }
    
    async def _handle_analyze_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dataset requirements for dashboard generation"""
        
        file_path = params.get("file_path")
        dashboard_type = params.get("dashboard_type", "auto")
        
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            df = pd.read_csv(file_path)
            requirements = await self.dashboard_builder.analyze_dashboard_requirements(df, dashboard_type)
            
            return {
                "success": True,
                "requirements": requirements,
                "dataset_info": {
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "data_types": df.dtypes.astype(str).to_dict()
                }
            }
        
        except Exception as e:
            return {"success": False, "error": f"Analysis failed: {str(e)}"}
    
    async def _handle_generate_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated dashboard"""
        
        file_path = params.get("file_path")
        dashboard_type = params.get("dashboard_type", "auto")
        customizations = params.get("customizations", {})
        
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            df = pd.read_csv(file_path)
            
            # Analyze requirements
            requirements = await self.dashboard_builder.analyze_dashboard_requirements(df, dashboard_type)
            
            # Generate dashboard
            dashboard = await self.dashboard_builder.generate_dashboard(df, requirements, customizations)
            
            return {
                "success": True,
                "dashboard": {
                    "id": dashboard["id"],
                    "type": dashboard["type"],
                    "html": dashboard["html"],
                    "metadata": dashboard["metadata"]
                },
                "charts_generated": len(dashboard["charts"]),
                "insights_generated": len(dashboard["insights"])
            }
        
        except Exception as e:
            return {"success": False, "error": f"Dashboard generation failed: {str(e)}"}
    
    async def _handle_get_templates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get available dashboard templates"""
        
        templates = {
            "executive_summary": {
                "name": "Executive Summary",
                "description": "High-level overview with key metrics and insights for executives",
                "best_for": ["Business reporting", "High-level overview", "Key metrics focus"],
                "features": ["Metric cards", "Priority charts", "Key insights", "Clean layout"]
            },
            "data_quality": {
                "name": "Data Quality Report", 
                "description": "Comprehensive data quality assessment and recommendations",
                "best_for": ["Data validation", "Quality assessment", "Data cleaning planning"],
                "features": ["Quality score", "Missing data analysis", "Outlier detection", "Data consistency checks"]
            },
            "exploratory": {
                "name": "Exploratory Analysis",
                "description": "Detailed exploratory data analysis with comprehensive visualizations",
                "best_for": ["Data exploration", "Pattern discovery", "Detailed analysis", "Research"],
                "features": ["Multiple chart types", "Distribution analysis", "Correlation analysis", "Pattern insights"]
            }
        }
        
        return {
            "success": True,
            "templates": templates,
            "recommendations": {
                "small_datasets": "executive_summary",
                "quality_issues": "data_quality", 
                "research_analysis": "exploratory"
            }
        }
    
    async def _handle_customize_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to existing dashboard"""
        
        dashboard_id = params.get("dashboard_id")
        customizations = params.get("customizations", {})
        
        dashboard = await self.dashboard_builder.get_dashboard(dashboard_id)
        if not dashboard:
            return {"success": False, "error": "Dashboard not found"}
        
        try:
            # Apply customizations (would involve re-rendering with new options)
            # For now, return updated metadata
            dashboard["metadata"]["customizations"] = customizations
            dashboard["metadata"]["last_updated"] = datetime.now().isoformat()
            
            await self.dashboard_builder._save_dashboard(dashboard)
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "customizations_applied": customizations,
                "updated_at": dashboard["metadata"]["last_updated"]
            }
        
        except Exception as e:
            return {"success": False, "error": f"Customization failed: {str(e)}"}
    
    async def _handle_export_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard in specified format"""
        
        dashboard_id = params.get("dashboard_id")
        format = params.get("format", "html")
        
        try:
            export_result = await self.dashboard_builder.export_dashboard(dashboard_id, format)
            
            return {
                "success": True,
                "export": export_result,
                "dashboard_id": dashboard_id
            }
        
        except Exception as e:
            return {"success": False, "error": f"Export failed: {str(e)}"}
    
    async def _handle_list_dashboards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all created dashboards"""
        
        try:
            dashboards = await self.dashboard_builder.list_dashboards()
            
            return {
                "success": True,
                "dashboards": dashboards,
                "total_count": len(dashboards)
            }
        
        except Exception as e:
            return {"success": False, "error": f"Failed to list dashboards: {str(e)}"}
    
    async def _handle_smart_recommendation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered dashboard recommendations"""
        
        file_path = params.get("file_path")
        business_context = params.get("business_context", "")
        
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            df = pd.read_csv(file_path)
            
            # Analyze data characteristics
            numerical_cols = len(df.select_dtypes(include=['number']).columns)
            categorical_cols = len(df.select_dtypes(include=['object']).columns)
            missing_percentage = (df.isnull().sum().sum() / df.size) * 100
            data_size = df.shape[0]
            
            # Generate smart recommendations
            recommendations = []
            
            # Dashboard type recommendation
            if missing_percentage > 15 or df.duplicated().sum() > 0:
                recommendations.append({
                    "type": "dashboard_type",
                    "recommendation": "data_quality",
                    "reason": f"Dataset has {missing_percentage:.1f}% missing values or duplicates",
                    "priority": "high"
                })
            elif numerical_cols > 3 and categorical_cols > 1:
                recommendations.append({
                    "type": "dashboard_type", 
                    "recommendation": "exploratory",
                    "reason": f"Rich dataset with {numerical_cols} numerical and {categorical_cols} categorical variables",
                    "priority": "medium"
                })
            else:
                recommendations.append({
                    "type": "dashboard_type",
                    "recommendation": "executive_summary", 
                    "reason": "Suitable for high-level overview and key insights",
                    "priority": "medium"
                })
            
            # Chart recommendations
            if numerical_cols > 1:
                recommendations.append({
                    "type": "chart",
                    "recommendation": "correlation_heatmap",
                    "reason": "Multiple numerical variables present for correlation analysis",
                    "priority": "high"
                })
            
            if categorical_cols > 0:
                recommendations.append({
                    "type": "chart",
                    "recommendation": "categorical_analysis",
                    "reason": f"{categorical_cols} categorical variables for distribution analysis",
                    "priority": "medium"
                })
            
            # Performance recommendations
            if data_size > 50000:
                recommendations.append({
                    "type": "performance",
                    "recommendation": "sampling",
                    "reason": f"Large dataset ({data_size:,} rows) may benefit from sampling for faster rendering",
                    "priority": "low"
                })
            
            # Business context recommendations
            if business_context:
                context_lower = business_context.lower()
                if any(word in context_lower for word in ["sales", "revenue", "profit", "business"]):
                    recommendations.append({
                        "type": "template",
                        "recommendation": "executive_summary",
                        "reason": "Business context suggests executive-level reporting needs",
                        "priority": "high"
                    })
                elif any(word in context_lower for word in ["research", "analysis", "study", "explore"]):
                    recommendations.append({
                        "type": "template",
                        "recommendation": "exploratory",
                        "reason": "Research context suggests detailed exploratory analysis",
                        "priority": "high"
                    })
                elif any(word in context_lower for word in ["quality", "clean", "validate"]):
                    recommendations.append({
                        "type": "template",
                        "recommendation": "data_quality",
                        "reason": "Quality-focused context suggests data quality assessment",
                        "priority": "high"
                    })
            
            return {
                "success": True,
                "recommendations": recommendations,
                "data_profile": {
                    "rows": data_size,
                    "numerical_columns": numerical_cols,
                    "categorical_columns": categorical_cols,
                    "missing_percentage": round(missing_percentage, 2),
                    "has_duplicates": df.duplicated().sum() > 0
                },
                "suggested_dashboard_type": recommendations[0]["recommendation"] if recommendations else "executive_summary"
            }
        
        except Exception as e:
            return {"success": False, "error": f"Smart recommendation failed: {str(e)}"}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return server capabilities for MCP protocol"""
        return self.capabilities

class DashboardMCPInterface:
    """Simplified interface for dashboard MCP operations"""
    
    def __init__(self):
        self.mcp_server = MCPDashboardServer()
    
    async def auto_generate_dashboard(self, file_path: str, business_context: str = "") -> Dict[str, Any]:
        """Automatically generate the best dashboard for a dataset"""
        
        # Get smart recommendations
        recommendations = await self.mcp_server.handle_request("smart_dashboard_recommendation", {
            "file_path": file_path,
            "business_context": business_context
        })
        
        if not recommendations["success"]:
            return recommendations
        
        # Use recommended dashboard type
        suggested_type = recommendations["suggested_dashboard_type"]
        
        # Generate dashboard
        dashboard_result = await self.mcp_server.handle_request("generate_dashboard", {
            "file_path": file_path,
            "dashboard_type": suggested_type
        })
        
        if dashboard_result["success"]:
            dashboard_result["recommendations"] = recommendations["recommendations"]
            dashboard_result["data_profile"] = recommendations["data_profile"]
        
        return convert_numpy_types(dashboard_result)
    
    async def generate_all_dashboard_types(self, file_path: str) -> Dict[str, Any]:
        """Generate all three dashboard types for comparison"""
        
        dashboard_types = ["executive_summary", "data_quality", "exploratory"]
        results = {}
        
        for dashboard_type in dashboard_types:
            result = await self.mcp_server.handle_request("generate_dashboard", {
                "file_path": file_path,
                "dashboard_type": dashboard_type
            })
            
            results[dashboard_type] = result
        
        return {
            "success": True,
            "dashboards": results,
            "total_generated": len([r for r in results.values() if r.get("success")])
        }
    
    async def get_dashboard_recommendations(self, file_path: str, context: str = "") -> Dict[str, Any]:
        """Get comprehensive dashboard recommendations"""
        
        return await self.mcp_server.handle_request("smart_dashboard_recommendation", {
            "file_path": file_path,
            "business_context": context
        })
