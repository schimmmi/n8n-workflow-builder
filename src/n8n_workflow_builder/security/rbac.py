#!/usr/bin/env python3
"""
RBAC Manager Module
Role-Based Access Control for workflows
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

logger = logging.getLogger("n8n-workflow-builder")


class RBACManager:
    """Role-Based Access Control and Multi-Tenant Security Manager"""

    # Role definitions with permissions
    ROLES = {
        "admin": {
            "name": "Administrator",
            "permissions": [
                "workflow.create", "workflow.read", "workflow.update", "workflow.delete",
                "workflow.execute", "workflow.validate", "workflow.analyze",
                "execution.read", "execution.analyze",
                "state.read", "state.write", "state.clear",
                "approval.create", "approval.approve", "approval.reject",
                "user.manage", "role.manage", "audit.read"
            ],
            "description": "Full access to all operations"
        },
        "developer": {
            "name": "Developer",
            "permissions": [
                "workflow.create", "workflow.read", "workflow.update",
                "workflow.execute", "workflow.validate", "workflow.analyze",
                "execution.read", "execution.analyze",
                "state.read", "state.write",
                "approval.create"
            ],
            "description": "Can create, modify, and test workflows, but needs approval for critical operations"
        },
        "operator": {
            "name": "Operator",
            "permissions": [
                "workflow.read", "workflow.execute",
                "execution.read",
                "state.read"
            ],
            "description": "Can execute existing workflows and view results"
        },
        "viewer": {
            "name": "Viewer",
            "permissions": [
                "workflow.read",
                "execution.read",
                "state.read"
            ],
            "description": "Read-only access to workflows and executions"
        },
        "auditor": {
            "name": "Auditor",
            "permissions": [
                "workflow.read",
                "execution.read",
                "audit.read"
            ],
            "description": "Can view workflows, executions, and audit logs for compliance"
        }
    }

    # Critical operations requiring approval
    APPROVAL_REQUIRED_OPERATIONS = [
        "workflow.delete",
        "workflow.deploy_production",
        "workflow.modify_active",
        "state.clear"
    ]

    def __init__(self, state_file: Path = None):
        self.state_file = state_file or (Path.home() / ".n8n_rbac_state.json")
        self.rbac_state = self._load_rbac_state()

    def _load_rbac_state(self) -> Dict:
        """Load RBAC state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load RBAC state: {e}")
                return self._default_rbac_state()
        return self._default_rbac_state()

    def _default_rbac_state(self) -> Dict:
        """Default RBAC state structure"""
        return {
            "users": {
                "default": {
                    "username": "default",
                    "role": "admin",
                    "tenant_id": "default",
                    "created_at": datetime.now().isoformat()
                }
            },
            "tenants": {
                "default": {
                    "tenant_id": "default",
                    "name": "Default Tenant",
                    "workflows": [],
                    "users": ["default"],
                    "created_at": datetime.now().isoformat()
                }
            },
            "pending_approvals": [],
            "audit_log": [],
            "created_at": datetime.now().isoformat()
        }

    def _save_rbac_state(self):
        """Save RBAC state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.rbac_state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save RBAC state: {e}")

    def check_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return False

        role = user.get("role")
        if role not in self.ROLES:
            return False

        return permission in self.ROLES[role]["permissions"]

    def require_approval(self, operation: str) -> bool:
        """Check if operation requires approval"""
        return operation in self.APPROVAL_REQUIRED_OPERATIONS

    def create_approval_request(self, username: str, operation: str, details: Dict) -> str:
        """Create approval request for critical operation"""
        approval_id = f"approval-{datetime.now().timestamp()}"
        approval = {
            "id": approval_id,
            "username": username,
            "operation": operation,
            "details": details,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_by": None,
            "approved_at": None
        }

        self.rbac_state["pending_approvals"].append(approval)
        self._save_rbac_state()

        self._audit_log(username, "approval_request_created", {
            "approval_id": approval_id,
            "operation": operation
        })

        return approval_id

    def approve_request(self, approval_id: str, approver: str) -> Dict:
        """Approve a pending request"""
        approval = self._find_approval(approval_id)
        if not approval:
            return {"success": False, "error": "Approval request not found"}

        if approval["status"] != "pending":
            return {"success": False, "error": f"Approval already {approval['status']}"}

        # Check if approver has approval permission
        if not self.check_permission(approver, "approval.approve"):
            return {"success": False, "error": "Insufficient permissions to approve"}

        # Cannot approve own request
        if approver == approval["username"]:
            return {"success": False, "error": "Cannot approve your own request"}

        approval["status"] = "approved"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now().isoformat()

        self._save_rbac_state()

        self._audit_log(approver, "approval_approved", {
            "approval_id": approval_id,
            "requested_by": approval["username"],
            "operation": approval["operation"]
        })

        return {"success": True, "approval": approval}

    def reject_request(self, approval_id: str, rejector: str, reason: str = None) -> Dict:
        """Reject a pending request"""
        approval = self._find_approval(approval_id)
        if not approval:
            return {"success": False, "error": "Approval request not found"}

        if approval["status"] != "pending":
            return {"success": False, "error": f"Approval already {approval['status']}"}

        if not self.check_permission(rejector, "approval.reject"):
            return {"success": False, "error": "Insufficient permissions to reject"}

        approval["status"] = "rejected"
        approval["approved_by"] = rejector
        approval["approved_at"] = datetime.now().isoformat()
        approval["rejection_reason"] = reason

        self._save_rbac_state()

        self._audit_log(rejector, "approval_rejected", {
            "approval_id": approval_id,
            "requested_by": approval["username"],
            "operation": approval["operation"],
            "reason": reason
        })

        return {"success": True, "approval": approval}

    def _find_approval(self, approval_id: str) -> Optional[Dict]:
        """Find approval request by ID"""
        for approval in self.rbac_state["pending_approvals"]:
            if approval["id"] == approval_id:
                return approval
        return None

    def get_pending_approvals(self, username: str = None) -> List[Dict]:
        """Get pending approval requests"""
        pending = [a for a in self.rbac_state["pending_approvals"] if a["status"] == "pending"]

        if username:
            # Return requests for this user or requests they can approve
            can_approve = self.check_permission(username, "approval.approve")
            if can_approve:
                return pending
            else:
                return [a for a in pending if a["username"] == username]

        return pending

    def add_user(self, username: str, role: str, tenant_id: str = "default") -> Dict:
        """Add a new user"""
        if username in self.rbac_state["users"]:
            return {"success": False, "error": "User already exists"}

        if role not in self.ROLES:
            return {"success": False, "error": f"Invalid role: {role}"}

        user = {
            "username": username,
            "role": role,
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat()
        }

        self.rbac_state["users"][username] = user

        # Add user to tenant
        if tenant_id in self.rbac_state["tenants"]:
            self.rbac_state["tenants"][tenant_id]["users"].append(username)

        self._save_rbac_state()

        self._audit_log("system", "user_created", {
            "username": username,
            "role": role,
            "tenant_id": tenant_id
        })

        return {"success": True, "user": user}

    def create_tenant(self, tenant_id: str, name: str) -> Dict:
        """Create a new tenant"""
        if tenant_id in self.rbac_state["tenants"]:
            return {"success": False, "error": "Tenant already exists"}

        tenant = {
            "tenant_id": tenant_id,
            "name": name,
            "workflows": [],
            "users": [],
            "created_at": datetime.now().isoformat()
        }

        self.rbac_state["tenants"][tenant_id] = tenant
        self._save_rbac_state()

        self._audit_log("system", "tenant_created", {
            "tenant_id": tenant_id,
            "name": name
        })

        return {"success": True, "tenant": tenant}

    def check_tenant_access(self, username: str, workflow_id: str) -> bool:
        """Check if user has access to workflow based on tenant"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return False

        tenant_id = user["tenant_id"]
        tenant = self.rbac_state["tenants"].get(tenant_id)
        if not tenant:
            return False

        # Admin users can access all workflows
        if user["role"] == "admin":
            return True

        # Check if workflow belongs to user's tenant
        return workflow_id in tenant.get("workflows", [])

    def register_workflow(self, workflow_id: str, tenant_id: str):
        """Register workflow to tenant"""
        if tenant_id in self.rbac_state["tenants"]:
            tenant = self.rbac_state["tenants"][tenant_id]
            if workflow_id not in tenant["workflows"]:
                tenant["workflows"].append(workflow_id)
                self._save_rbac_state()

    def _audit_log(self, username: str, action: str, details: Dict):
        """Log security-relevant actions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "details": details
        }

        self.rbac_state["audit_log"].append(log_entry)

        # Keep last 500 entries
        self.rbac_state["audit_log"] = self.rbac_state["audit_log"][-500:]

        self._save_rbac_state()

        logger.info(f"AUDIT: {username} - {action} - {details}")

    def get_audit_log(self, limit: int = 50, username: str = None, action: str = None) -> List[Dict]:
        """Get audit log with filters"""
        logs = self.rbac_state["audit_log"]

        if username:
            logs = [l for l in logs if l["username"] == username]

        if action:
            logs = [l for l in logs if l["action"] == action]

        return logs[-limit:]

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        user = self.rbac_state["users"].get(username)
        if not user:
            return None

        role_info = self.ROLES.get(user["role"], {})
        return {
            **user,
            "role_name": role_info.get("name"),
            "permissions": role_info.get("permissions", []),
            "role_description": role_info.get("description")
        }

    def generate_rbac_report(self) -> str:
        """Generate RBAC status report"""
        report = "# 🔒 RBAC & Security Status\n\n"

        # Users summary
        users = self.rbac_state["users"]
        report += f"## 👥 Users: {len(users)}\n\n"
        role_counts = {}
        for user in users.values():
            role = user["role"]
            role_counts[role] = role_counts.get(role, 0) + 1

        for role, count in role_counts.items():
            role_name = self.ROLES.get(role, {}).get("name", role)
            report += f"- **{role_name}**: {count} users\n"

        # Tenants summary
        tenants = self.rbac_state["tenants"]
        report += f"\n## 🏢 Tenants: {len(tenants)}\n\n"
        for tenant in tenants.values():
            report += f"- **{tenant['name']}** (`{tenant['tenant_id']}`)\n"
            report += f"  - Users: {len(tenant['users'])}\n"
            report += f"  - Workflows: {len(tenant['workflows'])}\n"

        # Pending approvals
        pending = self.get_pending_approvals()
        report += f"\n## ⏳ Pending Approvals: {len(pending)}\n\n"
        if pending:
            for approval in pending[:5]:
                report += f"- **{approval['id']}** - {approval['operation']} (by {approval['username']})\n"

        # Recent audit log
        recent_logs = self.get_audit_log(limit=5)
        report += f"\n## 📋 Recent Audit Log:\n\n"
        for log in reversed(recent_logs):
            report += f"- **{log['timestamp']}** - {log['username']}: {log['action']}\n"

        return report

