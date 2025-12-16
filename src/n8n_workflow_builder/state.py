#!/usr/bin/env python3
"""
State Management Module
Manages persistent state for workflows and sessions
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("n8n-workflow-builder")
STATE_FILE = Path.home() / ".n8n_workflow_builder_state.json"


class StateManager:
    """Manages persistent state and context for workflow operations"""

    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load state file: {e}")
                return self._default_state()
        return self._default_state()

    def _default_state(self) -> Dict:
        """Get default state structure"""
        return {
            "current_workflow_id": None,
            "current_workflow_name": None,
            "last_execution_id": None,
            "recent_workflows": [],
            "session_history": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    def _save_state(self):
        """Save state to file"""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save state file: {e}")

    def set_current_workflow(self, workflow_id: str, workflow_name: str):
        """Set the current active workflow"""
        self.state["current_workflow_id"] = workflow_id
        self.state["current_workflow_name"] = workflow_name

        # Update recent workflows (keep last 10)
        workflow_entry = {
            "id": workflow_id,
            "name": workflow_name,
            "accessed_at": datetime.now().isoformat()
        }

        # Remove if already in list
        self.state["recent_workflows"] = [
            w for w in self.state["recent_workflows"]
            if w["id"] != workflow_id
        ]

        # Add to front
        self.state["recent_workflows"].insert(0, workflow_entry)
        self.state["recent_workflows"] = self.state["recent_workflows"][:10]

        self._save_state()
        logger.info(f"Set current workflow: {workflow_name} ({workflow_id})")

    def get_current_workflow(self) -> Optional[Dict]:
        """Get current workflow info"""
        if self.state["current_workflow_id"]:
            return {
                "id": self.state["current_workflow_id"],
                "name": self.state["current_workflow_name"]
            }
        return None

    def set_last_execution(self, execution_id: str):
        """Record last execution"""
        self.state["last_execution_id"] = execution_id
        self._save_state()

    def get_last_execution(self) -> Optional[str]:
        """Get last execution ID"""
        return self.state.get("last_execution_id")

    def log_action(self, action: str, details: Dict = None):
        """Log an action to session history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }

        self.state["session_history"].append(entry)

        # Keep last 50 entries
        self.state["session_history"] = self.state["session_history"][-50:]

        self._save_state()

    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """Get recent session history"""
        return self.state["session_history"][-limit:]

    def get_recent_workflows(self) -> List[Dict]:
        """Get recently accessed workflows"""
        return self.state["recent_workflows"]

    def clear_state(self):
        """Clear all state"""
        self.state = self._default_state()
        self._save_state()
        logger.info("State cleared")

    def get_state_summary(self) -> str:
        """Get a formatted summary of current state"""
        summary = "# Current Session State\n\n"

        current = self.get_current_workflow()
        if current:
            summary += f"**Active Workflow:** {current['name']} (`{current['id']}`)\n\n"
        else:
            summary += "**Active Workflow:** None\n\n"

        if self.state.get("last_execution_id"):
            summary += f"**Last Execution:** `{self.state['last_execution_id']}`\n\n"

        recent = self.get_recent_workflows()
        if recent:
            summary += "## Recent Workflows:\n\n"
            for wf in recent[:5]:
                summary += f"- {wf['name']} (`{wf['id']}`) - {wf['accessed_at']}\n"
            summary += "\n"

        history = self.get_session_history(5)
        if history:
            summary += "## Recent Actions:\n\n"
            for entry in reversed(history):
                summary += f"- **{entry['timestamp']}** - {entry['action']}\n"

        return summary

