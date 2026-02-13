#!/usr/bin/env python3
"""
Security & Compliance Tool Handlers
Handles security auditing, RBAC, and compliance checking
"""
import json
from typing import Any, TYPE_CHECKING

from mcp.types import TextContent

from .base import BaseTool, ToolError

if TYPE_CHECKING:
    from ..dependencies import Dependencies


class SecurityTools(BaseTool):
    """Handler for security audit and RBAC tools"""
    
    async def handle(self, name: str, arguments: dict) -> list[TextContent]:
        """Route security tool calls to appropriate handler methods
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            List of TextContent responses
        """
        handlers = {
            # Security Audit tools
            "audit_workflow_security": self.audit_workflow_security,
            "get_security_summary": self.get_security_summary,
            "check_compliance": self.check_compliance,
            "get_critical_findings": self.get_critical_findings,
            
            # RBAC tools
            "rbac_get_status": self.rbac_get_status,
            "rbac_add_user": self.rbac_add_user,
            "rbac_get_user_info": self.rbac_get_user_info,
            "rbac_check_permission": self.rbac_check_permission,
            "rbac_create_approval_request": self.rbac_create_approval_request,
            "rbac_approve_request": self.rbac_approve_request,
            "rbac_reject_request": self.rbac_reject_request,
            "rbac_get_pending_approvals": self.rbac_get_pending_approvals,
            "rbac_create_tenant": self.rbac_create_tenant,
            "rbac_get_audit_log": self.rbac_get_audit_log,
        }
        
        handler = handlers.get(name)
        if not handler:
            raise ToolError("UNKNOWN_TOOL", f"Tool '{name}' not found in security tools")
        
        return await handler(arguments)
    
    # Security Audit Tools
    
    async def audit_workflow_security(self, arguments: dict) -> list[TextContent]:
        """Run comprehensive security audit on a workflow"""
        workflow_id = arguments["workflow_id"]
        report_format = arguments.get("format", "markdown")
        
        workflow_data = await self.deps.client.get_workflow(workflow_id)
        report, score = self.deps.security_auditor.audit_and_report(
            workflow_data,
            format=report_format
        )
        
        return [TextContent(type="text", text=report)]
    
    async def get_security_summary(self, arguments: dict) -> list[TextContent]:
        """Get concise security summary for a workflow"""
        workflow_id = arguments["workflow_id"]
        
        workflow_data = await self.deps.client.get_workflow(workflow_id)
        summary = self.deps.security_auditor.get_summary(workflow_data)
        
        result = f"# 🔐 Security Summary\n\n"
        result += f"**Workflow:** {summary['workflow_name']}\n"
        result += f"**Score:** {summary['score']}/100 ({summary['grade']})\n"
        result += f"**Risk Level:** {summary['risk_level'].upper()}\n\n"
        result += f"**Total Findings:** {summary['total_findings']}\n\n"
        result += "**By Category:**\n"
        result += f"- Secrets: {summary['findings_by_category']['secrets']}\n"
        result += f"- Authentication: {summary['findings_by_category']['authentication']}\n"
        result += f"- Exposure: {summary['findings_by_category']['exposure']}\n\n"
        result += "**By Severity:**\n"
        result += f"- 🔴 Critical: {summary['findings_by_severity']['critical']}\n"
        result += f"- 🟠 High: {summary['findings_by_severity']['high']}\n"
        result += f"- 🟡 Medium: {summary['findings_by_severity']['medium']}\n"
        result += f"- 🟢 Low: {summary['findings_by_severity']['low']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def check_compliance(self, arguments: dict) -> list[TextContent]:
        """Check if workflow meets security compliance standards"""
        workflow_id = arguments["workflow_id"]
        standard = arguments.get("standard", "basic")
        
        workflow_data = await self.deps.client.get_workflow(workflow_id)
        is_compliant, violations = self.deps.security_auditor.validate_compliance(
            workflow_data,
            standard=standard
        )
        
        result = f"# ✅ Compliance Check\n\n"
        result += f"**Standard:** {standard.upper()}\n"
        result += f"**Status:** {'✅ COMPLIANT' if is_compliant else '❌ NON-COMPLIANT'}\n\n"
        
        if violations:
            result += "## Violations:\n\n"
            for violation in violations:
                result += f"- {violation}\n"
        else:
            result += "✅ No violations found - workflow meets compliance standards.\n"
        
        return [TextContent(type="text", text=result)]
    
    async def get_critical_findings(self, arguments: dict) -> list[TextContent]:
        """Get only critical and high severity security findings"""
        workflow_id = arguments["workflow_id"]
        
        workflow_data = await self.deps.client.get_workflow(workflow_id)
        findings = self.deps.security_auditor.get_critical_findings(workflow_data)
        
        total = (len(findings['secrets']) + len(findings['authentication']) +
                len(findings['exposure']))
        
        result = f"# 🚨 Critical Security Findings\n\n"
        result += f"**Total Critical/High Findings:** {total}\n\n"
        
        if findings['secrets']:
            result += f"## 🔑 Hardcoded Secrets ({len(findings['secrets'])})\n\n"
            for f in findings['secrets']:
                result += f"- **{f.secret_type.value}** in `{f.node_name}`: {f.field_path}\n"
                result += f"  Confidence: {f.confidence:.0%}, Severity: {f.severity.value}\n\n"
        
        if findings['authentication']:
            result += f"## 🔒 Authentication Issues ({len(findings['authentication'])})\n\n"
            for f in findings['authentication']:
                result += f"- **{f.issue_type.value}** in `{f.node_name}`\n"
                result += f"  Risk: {f.risk_level.value}, Severity: {f.severity.value}\n\n"
        
        if findings['exposure']:
            result += f"## 🌐 Data Exposure Risks ({len(findings['exposure'])})\n\n"
            for f in findings['exposure']:
                result += f"- **{f.exposure_type.value}** in `{f.node_name}`\n"
                result += f"  {f.description}\n\n"
        
        if total == 0:
            result += "✅ No critical or high severity findings - good security posture!\n"
        
        return [TextContent(type="text", text=result)]
    
    # RBAC Tools
    
    async def rbac_get_status(self, arguments: dict) -> list[TextContent]:
        """Get RBAC status report"""
        report = self.deps.rbac_manager.generate_rbac_report()
        return [TextContent(type="text", text=report)]
    
    async def rbac_add_user(self, arguments: dict) -> list[TextContent]:
        """Add a new user with specified role"""
        username = arguments["username"]
        role = arguments["role"]
        tenant_id = arguments.get("tenant_id", "default")
        
        result_data = self.deps.rbac_manager.add_user(username, role, tenant_id)
        
        if not result_data["success"]:
            return [TextContent(type="text", text=f"❌ Failed to add user: {result_data['error']}")]
        
        user = result_data["user"]
        result = f"✅ User created successfully!\n\n"
        result += f"**Username:** {user['username']}\n"
        result += f"**Role:** {role}\n"
        result += f"**Tenant:** {tenant_id}\n"
        result += f"**Created:** {user['created_at']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_get_user_info(self, arguments: dict) -> list[TextContent]:
        """Get detailed information about a user"""
        username = arguments["username"]
        user_info = self.deps.rbac_manager.get_user_info(username)
        
        if not user_info:
            return [TextContent(type="text", text=f"❌ User '{username}' not found")]
        
        result = f"# User Information: {username}\n\n"
        result += f"**Role:** {user_info['role_name']} ({user_info['role']})\n"
        result += f"**Tenant:** {user_info['tenant_id']}\n"
        result += f"**Created:** {user_info['created_at']}\n\n"
        result += f"## Permissions ({len(user_info['permissions'])}):\n\n"
        for perm in user_info['permissions']:
            result += f"- {perm}\n"
        result += f"\n**Description:** {user_info['role_description']}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_check_permission(self, arguments: dict) -> list[TextContent]:
        """Check if user has a specific permission"""
        username = arguments["username"]
        permission = arguments["permission"]
        
        has_permission = self.deps.rbac_manager.check_permission(username, permission)
        
        if has_permission:
            result = f"✅ User '{username}' HAS permission: `{permission}`"
        else:
            result = f"❌ User '{username}' DOES NOT HAVE permission: `{permission}`"
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_create_approval_request(self, arguments: dict) -> list[TextContent]:
        """Create an approval request for privileged operation"""
        username = arguments["username"]
        operation = arguments["operation"]
        details = arguments["details"]
        
        approval_id = self.deps.rbac_manager.create_approval_request(username, operation, details)
        
        result = f"📝 Approval request created!\n\n"
        result += f"**Approval ID:** `{approval_id}`\n"
        result += f"**Operation:** {operation}\n"
        result += f"**Requested by:** {username}\n"
        result += f"**Status:** Pending\n\n"
        result += "This request needs approval from an admin before the operation can proceed."
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_approve_request(self, arguments: dict) -> list[TextContent]:
        """Approve a pending approval request"""
        approval_id = arguments["approval_id"]
        approver = arguments["approver"]
        
        result_data = self.deps.rbac_manager.approve_request(approval_id, approver)
        
        if not result_data["success"]:
            return [TextContent(type="text", text=f"❌ Failed to approve: {result_data['error']}")]
        
        approval = result_data["approval"]
        result = f"✅ Approval request APPROVED!\n\n"
        result += f"**Approval ID:** `{approval['id']}`\n"
        result += f"**Operation:** {approval['operation']}\n"
        result += f"**Requested by:** {approval['username']}\n"
        result += f"**Approved by:** {approver}\n"
        result += f"**Approved at:** {approval['approved_at']}\n\n"
        result += "The operation can now proceed."
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_reject_request(self, arguments: dict) -> list[TextContent]:
        """Reject a pending approval request"""
        approval_id = arguments["approval_id"]
        rejector = arguments["rejector"]
        reason = arguments.get("reason", "No reason provided")
        
        result_data = self.deps.rbac_manager.reject_request(approval_id, rejector, reason)
        
        if not result_data["success"]:
            return [TextContent(type="text", text=f"❌ Failed to reject: {result_data['error']}")]
        
        approval = result_data["approval"]
        result = f"❌ Approval request REJECTED\n\n"
        result += f"**Approval ID:** `{approval['id']}`\n"
        result += f"**Operation:** {approval['operation']}\n"
        result += f"**Requested by:** {approval['username']}\n"
        result += f"**Rejected by:** {rejector}\n"
        result += f"**Rejected at:** {approval['approved_at']}\n"
        result += f"**Reason:** {reason}\n"
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_get_pending_approvals(self, arguments: dict) -> list[TextContent]:
        """Get list of pending approval requests"""
        username = arguments.get("username")
        pending = self.deps.rbac_manager.get_pending_approvals(username)
        
        if not pending:
            result = "✅ No pending approval requests"
            if username:
                result += f" for user '{username}'"
            return [TextContent(type="text", text=result)]
        
        result = f"# Pending Approval Requests ({len(pending)})\n\n"
        for approval in pending:
            result += f"## `{approval['id']}`\n\n"
            result += f"**Operation:** {approval['operation']}\n"
            result += f"**Requested by:** {approval['username']}\n"
            result += f"**Created:** {approval['created_at']}\n"
            if approval.get('details'):
                result += f"**Details:** {json.dumps(approval['details'], indent=2)}\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_create_tenant(self, arguments: dict) -> list[TextContent]:
        """Create a new tenant for multi-tenancy"""
        tenant_id = arguments["tenant_id"]
        name = arguments["name"]
        
        result_data = self.deps.rbac_manager.create_tenant(tenant_id, name)
        
        if not result_data["success"]:
            return [TextContent(type="text", text=f"❌ Failed to create tenant: {result_data['error']}")]
        
        tenant = result_data["tenant"]
        result = f"✅ Tenant created successfully!\n\n"
        result += f"**Tenant ID:** `{tenant['tenant_id']}`\n"
        result += f"**Name:** {tenant['name']}\n"
        result += f"**Created:** {tenant['created_at']}\n\n"
        result += "You can now add users to this tenant."
        
        return [TextContent(type="text", text=result)]
    
    async def rbac_get_audit_log(self, arguments: dict) -> list[TextContent]:
        """Get RBAC audit log entries"""
        limit = arguments.get("limit", 50)
        username = arguments.get("username")
        action = arguments.get("action")
        
        logs = self.deps.rbac_manager.get_audit_log(limit, username, action)
        
        if not logs:
            result = "📋 No audit log entries found"
            if username:
                result += f" for user '{username}'"
            if action:
                result += f" with action '{action}'"
            return [TextContent(type="text", text=result)]
        
        result = f"# Audit Log ({len(logs)} entries)\n\n"
        for log in reversed(logs):
            result += f"**{log['timestamp']}**\n"
            result += f"- User: `{log['username']}`\n"
            result += f"- Action: `{log['action']}`\n"
            if log.get('details'):
                details_str = ", ".join([f"{k}={v}" for k, v in log['details'].items()])
                result += f"- Details: {details_str}\n"
            result += "\n"
        
        return [TextContent(type="text", text=result)]
