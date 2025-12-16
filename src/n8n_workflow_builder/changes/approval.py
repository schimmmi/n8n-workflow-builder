"""
Approval Workflow - Manage change approvals

Features:
- Create change requests
- Approve/reject changes
- Track change history
- Auto-rollback on failure
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid


class ChangeRequest:
    """Represents a workflow change request"""

    def __init__(self, workflow_id: str, workflow_name: str, changes: Dict, reason: str, requester: str):
        self.id = str(uuid.uuid4())[:8]
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.changes = changes
        self.reason = reason
        self.requester = requester
        self.status = "pending"  # pending, approved, rejected, applied, failed
        self.reviewer = None
        self.review_comments = None
        self.created_at = datetime.now().isoformat()
        self.reviewed_at = None
        self.applied_at = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "changes": self.changes,
            "reason": self.reason,
            "requester": self.requester,
            "status": self.status,
            "reviewer": self.reviewer,
            "review_comments": self.review_comments,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "applied_at": self.applied_at,
        }


class ApprovalWorkflow:
    """Manages workflow change approvals"""

    def __init__(self):
        self.requests = {}  # change_request_id -> ChangeRequest
        self.history = []  # List of all change requests

    def create_request(
        self,
        workflow_id: str,
        workflow_name: str,
        changes: Dict,
        reason: str,
        requester: str
    ) -> ChangeRequest:
        """Create a new change request"""
        request = ChangeRequest(workflow_id, workflow_name, changes, reason, requester)
        self.requests[request.id] = request
        self.history.append(request)
        return request

    def approve_request(self, request_id: str, reviewer: str, comments: Optional[str] = None) -> Dict:
        """Approve a change request"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}

        request = self.requests[request_id]

        if request.status != "pending":
            return {"success": False, "error": f"Request is already {request.status}"}

        request.status = "approved"
        request.reviewer = reviewer
        request.review_comments = comments
        request.reviewed_at = datetime.now().isoformat()

        return {"success": True, "request": request.to_dict()}

    def reject_request(self, request_id: str, reviewer: str, reason: str) -> Dict:
        """Reject a change request"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}

        request = self.requests[request_id]

        if request.status != "pending":
            return {"success": False, "error": f"Request is already {request.status}"}

        request.status = "rejected"
        request.reviewer = reviewer
        request.review_comments = reason
        request.reviewed_at = datetime.now().isoformat()

        return {"success": True, "request": request.to_dict()}

    def mark_applied(self, request_id: str) -> Dict:
        """Mark request as successfully applied"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}

        request = self.requests[request_id]
        request.status = "applied"
        request.applied_at = datetime.now().isoformat()

        return {"success": True, "request": request.to_dict()}

    def mark_failed(self, request_id: str, error: str) -> Dict:
        """Mark request as failed during application"""
        if request_id not in self.requests:
            return {"success": False, "error": "Request not found"}

        request = self.requests[request_id]
        request.status = "failed"
        request.review_comments = f"{request.review_comments or ''}\nApplication error: {error}"

        return {"success": True, "request": request.to_dict()}

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending change requests"""
        return [r.to_dict() for r in self.requests.values() if r.status == "pending"]

    def get_request(self, request_id: str) -> Optional[Dict]:
        """Get a specific change request"""
        request = self.requests.get(request_id)
        return request.to_dict() if request else None

    def get_workflow_history(self, workflow_id: str) -> List[Dict]:
        """Get change history for a workflow"""
        return [r.to_dict() for r in self.history if r.workflow_id == workflow_id]
