#!/usr/bin/env python3
"""
Test Security Audit System
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from n8n_workflow_builder.security import SecurityAuditor


def test_security_audit():
    """Test security audit on example workflow"""

    # Example workflow with security issues
    workflow = {
        "id": "test-workflow-123",
        "name": "Test Payment Workflow",
        "nodes": [
            {
                "id": "webhook-1",
                "name": "Payment Webhook",
                "type": "n8n-nodes-base.webhook",
                "parameters": {
                    "path": "payment",
                    "httpMethod": "POST",
                    "authentication": "none"  # ❌ No authentication
                }
            },
            {
                "id": "http-1",
                "name": "Call Stripe API",
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "https://api.stripe.com/v1/charges",
                    "authentication": "none",
                    "headers": {
                        "Authorization": "Bearer sk_test_51234567890abcdef"  # ❌ Hardcoded secret
                    }
                }
            },
            {
                "id": "postgres-1",
                "name": "Save to Database",
                "type": "n8n-nodes-base.postgres",
                "parameters": {
                    "connectionString": "postgresql://admin:password123@db.example.com/payments"  # ❌ Hardcoded credentials
                }
            },
            {
                "id": "respond-1",
                "name": "Send Response",
                "type": "n8n-nodes-base.respond",
                "parameters": {
                    "options": {
                        "responseData": "{{$json}}"  # ⚠️ Might expose sensitive data
                    }
                }
            }
        ],
        "connections": {}
    }

    print("\n" + "="*80)
    print("🔐 SECURITY AUDIT TEST")
    print("="*80 + "\n")

    auditor = SecurityAuditor()

    # Run audit
    report, score = auditor.audit_and_report(workflow, format="markdown")

    print(report)

    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Score: {score.score}/100")
    print(f"Risk Level: {score.risk_level.value}")
    print(f"Findings: {sum(score.findings_count.values())}")
    print("="*80 + "\n")

    # Test compliance check
    print("\n" + "-"*80)
    print("COMPLIANCE CHECK")
    print("-"*80)

    is_compliant, violations = auditor.validate_compliance(workflow, standard="enterprise")
    print(f"Enterprise Compliance: {'✅ PASS' if is_compliant else '❌ FAIL'}")
    if violations:
        print("\nViolations:")
        for violation in violations:
            print(f"  - {violation}")
    print("-"*80)


if __name__ == "__main__":
    test_security_audit()
