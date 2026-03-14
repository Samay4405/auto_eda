"""
Supabase and Database integration module for Automated EDA
Handles database connections, user authentication, and data persistence
"""

from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from pydantic import BaseModel
import uuid
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations with Supabase"""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not configured")
            self.client: Optional[Client] = None
        else:
            self.client = create_client(supabase_url, supabase_key)

    # User Management Methods
    async def create_user_profile(
        self, user_id: str, email: str, username: str = None, full_name: str = None
    ):
        """Create user profile after authentication"""
        try:
            if not self.client:
                return None

            data = {
                "id": user_id,
                "email": email,
                "username": username,
                "full_name": full_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            response = self.client.table("users").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return None

    async def get_user_profile(self, user_id: str):
        """Get user profile"""
        try:
            if not self.client:
                return None

            response = (
                self.client.table("users").select("*").eq("id", user_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None

    async def update_user_profile(self, user_id: str, **kwargs):
        """Update user profile"""
        try:
            if not self.client:
                return None

            kwargs["updated_at"] = datetime.now().isoformat()
            response = (
                self.client.table("users").update(kwargs).eq("id", user_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return None

    # Dataset Management Methods
    async def save_dataset_metadata(
        self,
        user_id: str,
        file_name: str,
        original_file_name: str,
        file_path: str,
        file_size: int,
        row_count: int,
        column_count: int,
        columns: List[str],
        dtypes: Dict,
    ):
        """Save dataset metadata to database"""
        try:
            if not self.client:
                return None

            data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "file_name": file_name,
                "original_file_name": original_file_name,
                "file_path": file_path,
                "file_size_bytes": file_size,
                "row_count": row_count,
                "column_count": column_count,
                "columns": columns,
                "dtypes": dtypes,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            response = self.client.table("datasets").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error saving dataset metadata: {str(e)}")
            return None

    async def get_user_datasets(self, user_id: str, limit: int = 50, offset: int = 0):
        """Get all datasets for a user"""
        try:
            if not self.client:
                return []

            response = (
                self.client.table("datasets")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching user datasets: {str(e)}")
            return []

    async def get_dataset(self, dataset_id: str, user_id: str = None):
        """Get a specific dataset"""
        try:
            if not self.client:
                return None

            query = self.client.table("datasets").select("*").eq("id", dataset_id)
            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching dataset: {str(e)}")
            return None

    async def delete_dataset(self, dataset_id: str, user_id: str):
        """Delete a dataset"""
        try:
            if not self.client:
                return False

            self.client.table("datasets").delete().eq("id", dataset_id).eq(
                "user_id", user_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting dataset: {str(e)}")
            return False

    # Dashboard Management Methods
    async def save_dashboard(
        self,
        user_id: str,
        dataset_id: str,
        title: str,
        dashboard_type: str,
        html_content: str,
        charts_config: Dict = None,
        ai_insights: Dict = None,
    ):
        """Save generated dashboard"""
        try:
            if not self.client:
                return None

            data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "dataset_id": dataset_id,
                "title": title,
                "dashboard_type": dashboard_type,
                "html_content": html_content,
                "charts_config": charts_config,
                "ai_insights": ai_insights,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            response = self.client.table("dashboards").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error saving dashboard: {str(e)}")
            return None

    async def get_user_dashboards(self, user_id: str, limit: int = 50, offset: int = 0):
        """Get all dashboards for a user"""
        try:
            if not self.client:
                return []

            response = (
                self.client.table("dashboards")
                .select("id, title, dashboard_type, created_at, updated_at, dataset_id")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching user dashboards: {str(e)}")
            return []

    async def get_dashboard(self, dashboard_id: str, user_id: str = None):
        """Get a specific dashboard"""
        try:
            if not self.client:
                return None

            query = self.client.table("dashboards").select("*").eq("id", dashboard_id)
            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching dashboard: {str(e)}")
            return None

    async def delete_dashboard(self, dashboard_id: str, user_id: str):
        """Delete a dashboard"""
        try:
            if not self.client:
                return False

            self.client.table("dashboards").delete().eq("id", dashboard_id).eq(
                "user_id", user_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting dashboard: {str(e)}")
            return False

    # Analysis Results Management
    async def save_analysis_result(
        self,
        user_id: str,
        dataset_id: str,
        analysis_type: str,
        parameters: Dict,
        results: Dict,
        charts: Dict = None,
    ):
        """Save analysis results"""
        try:
            if not self.client:
                return None

            data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "dataset_id": dataset_id,
                "analysis_type": analysis_type,
                "parameters": parameters,
                "results": results,
                "charts": charts,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            response = self.client.table("analyses").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error saving analysis result: {str(e)}")
            return None

    async def get_analysis_history(
        self, dataset_id: str, limit: int = 50, offset: int = 0
    ):
        """Get analysis history for a dataset"""
        try:
            if not self.client:
                return []

            response = (
                self.client.table("analyses")
                .select("*")
                .eq("dataset_id", dataset_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching analysis history: {str(e)}")
            return []


# Global database manager instance
db_manager = DatabaseManager()
