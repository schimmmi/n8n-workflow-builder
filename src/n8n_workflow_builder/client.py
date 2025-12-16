#!/usr/bin/env python3
"""
N8n Client Module
HTTP client for n8n API interactions
"""
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("n8n-workflow-builder")


class N8nClient:
    """Client for n8n API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}
    
    async def get_workflows(self, active_only: bool = False) -> List[Dict]:
        """Get all workflows"""
        params = {}
        if active_only:
            params["active"] = "true"
        
        response = await self.client.get(
            f"{self.api_url}/api/v1/workflows",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def get_workflow(self, workflow_id: str) -> Dict:
        """Get a specific workflow"""
        response = await self.client.get(
            f"{self.api_url}/api/v1/workflows/{workflow_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    async def create_workflow(self, workflow: Dict) -> Dict:
        """Create a new workflow"""
        response = await self.client.post(
            f"{self.api_url}/api/v1/workflows",
            headers=self.headers,
            json=workflow
        )
        response.raise_for_status()
        return response.json()

    async def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """Execute a workflow (test run)

        Note: This triggers a workflow execution similar to the "Execute Workflow" button in the UI.
        For production workflows, they should be triggered via webhooks or schedule.
        """
        # n8n API endpoint for running/testing workflows
        # The correct endpoint might be /run or /test depending on n8n version
        try:
            # Try the /run endpoint first (newer n8n versions)
            response = await self.client.post(
                f"{self.api_url}/api/v1/workflows/{workflow_id}/run",
                headers=self.headers,
                json=data or {}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Try alternative endpoint /test (older versions)
                try:
                    response = await self.client.post(
                        f"{self.api_url}/api/v1/workflows/{workflow_id}/test",
                        headers=self.headers,
                        json=data or {}
                    )
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError:
                    # If both fail, provide helpful error message
                    raise Exception(
                        f"Cannot execute workflow via API. "
                        f"This workflow might need to be triggered via webhook or schedule, "
                        f"or use the 'Execute Workflow' button in the n8n UI."
                    )
            raise
    
    async def get_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get workflow executions (summary only, without full node data)"""
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id

        response = await self.client.get(
            f"{self.api_url}/api/v1/executions",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()["data"]

    async def get_execution(self, execution_id: str, include_data: bool = True) -> Dict:
        """Get detailed execution data including all node inputs/outputs

        Args:
            execution_id: The execution ID
            include_data: Whether to include full execution data (default: True)

        Returns:
            Full execution data with node data
        """
        # Add includeData parameter to get full node execution data
        params = {}
        if include_data:
            params['includeData'] = 'true'

        response = await self.client.get(
            f"{self.api_url}/api/v1/executions/{execution_id}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()

        result = response.json()

        # Log for debugging if data is still missing
        if not result.get('data', {}).get('resultData'):
            logger.warning(f"Execution {execution_id} has no resultData - execution data might not be saved by n8n")

        return result

    async def update_workflow(self, workflow_id: str, updates: Dict) -> Dict:
        """Update an existing workflow

        Args:
            workflow_id: ID of the workflow to update
            updates: Dictionary with fields to update (name, active, nodes, connections, settings, etc.)

        Returns:
            Updated workflow data
        """
        # First get the current workflow to merge with updates
        current_workflow = await self.get_workflow(workflow_id)

        # Whitelist of fields that are allowed by n8n API for updates
        # Note: 'active', 'tags', 'id', 'createdAt', 'updatedAt' etc. are read-only
        allowed_fields = ['name', 'nodes', 'connections', 'settings', 'staticData']

        # Build the update payload - start with required fields
        payload = {
            'name': current_workflow.get('name', 'Unnamed Workflow'),
            'nodes': current_workflow.get('nodes', []),
            'connections': current_workflow.get('connections', {}),
        }

        # Add optional allowed fields if they exist in current workflow
        for field in ['settings', 'staticData']:
            if field in current_workflow:
                payload[field] = current_workflow[field]

        # Apply updates - only allow whitelisted fields
        for key, value in updates.items():
            if key in allowed_fields:
                payload[key] = value
            else:
                logger.warning(f"Skipping field '{key}' - it's read-only or not supported by n8n API")

        # Ensure connections is always present and is a dict
        if 'connections' not in payload or payload['connections'] is None:
            payload['connections'] = {}

        # n8n API uses PUT for updates, not PATCH
        try:
            response = await self.client.put(
                f"{self.api_url}/api/v1/workflows/{workflow_id}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the detailed error response for debugging
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                error_detail = str(e)
            logger.error(f"Failed to update workflow {workflow_id}: {error_detail}")
            logger.error(f"Payload sent: {json.dumps(payload, indent=2)}")
            raise Exception(f"Failed to update workflow: {error_detail}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

