#!/usr/bin/env python3
"""
Test Semantic Workflow Analyzer
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from n8n_workflow_builder.server import SemanticWorkflowAnalyzer


def test_http_retry_patterns():
    """Test HTTP request retry detection"""
    print("\n=== Testing HTTP Retry Patterns ===\n")

    # Workflow without retry
    workflow = {
        'name': 'Test HTTP',
        'nodes': [
            {
                'name': 'HTTP Request',
                'type': 'n8n-nodes-base.httpRequest',
                'parameters': {
                    'url': 'https://api.example.com'
                },
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    print(f"Issues found: {len(analysis['issues'])}")
    assert len(analysis['issues']) >= 2, "Should detect missing retry and timeout"

    # Check for specific issues
    issues_text = str(analysis['issues'])
    assert 'retry' in issues_text.lower(), "Should detect missing retry"
    assert 'timeout' in issues_text.lower(), "Should detect missing timeout"

    print("✅ HTTP retry detection working")


def test_split_in_batches_completion():
    """Test SplitInBatches loop detection"""
    print("\n=== Testing SplitInBatches Completion ===\n")

    # SplitInBatches without loop back
    workflow = {
        'name': 'Test Batch',
        'nodes': [
            {
                'name': 'Start',
                'type': 'n8n-nodes-base.manualTrigger',
                'parameters': {},
                'position': [100, 100]
            },
            {
                'name': 'Split',
                'type': 'n8n-nodes-base.splitInBatches',
                'parameters': {'batchSize': 10},
                'position': [200, 100]
            },
            {
                'name': 'Process',
                'type': 'n8n-nodes-base.set',
                'parameters': {},
                'position': [300, 100]
            }
        ],
        'connections': {
            'Start': {'main': [[{'node': 'Split', 'type': 'main', 'index': 0}]]},
            'Split': {'main': [[{'node': 'Process', 'type': 'main', 'index': 0}]]}
        }
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    critical_issues = [i for i in analysis['issues'] if i['severity'] == 'critical']
    print(f"Critical issues: {len(critical_issues)}")

    assert len(critical_issues) >= 1, "Should detect missing loop back"
    assert any('SplitInBatches' in i['issue'] for i in critical_issues), "Should mention SplitInBatches"

    print("✅ SplitInBatches detection working")


def test_cron_timezone():
    """Test Schedule Trigger timezone detection"""
    print("\n=== Testing Cron Timezone ===\n")

    workflow = {
        'name': 'Test Schedule',
        'nodes': [
            {
                'name': 'Schedule',
                'type': 'n8n-nodes-base.scheduleTrigger',
                'parameters': {
                    'rule': {'interval': [{'field': 'hours', 'hoursInterval': 1}]}
                },
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    medium_issues = [i for i in analysis['issues'] if i['severity'] == 'medium']
    print(f"Medium issues: {len(medium_issues)}")

    assert any('timezone' in i['issue'].lower() for i in analysis['issues']), "Should detect missing timezone"

    print("✅ Timezone detection working")


def test_if_node_default_path():
    """Test IF node path detection"""
    print("\n=== Testing IF Node Default Path ===\n")

    # IF node with only true path
    workflow = {
        'name': 'Test IF',
        'nodes': [
            {
                'name': 'Start',
                'type': 'n8n-nodes-base.manualTrigger',
                'parameters': {},
                'position': [100, 100]
            },
            {
                'name': 'IF',
                'type': 'n8n-nodes-base.if',
                'parameters': {'conditions': {}},
                'position': [200, 100]
            },
            {
                'name': 'True Action',
                'type': 'n8n-nodes-base.set',
                'parameters': {},
                'position': [300, 100]
            }
        ],
        'connections': {
            'Start': {'main': [[{'node': 'IF', 'type': 'main', 'index': 0}]]},
            'IF': {'main': [[{'node': 'True Action', 'type': 'main', 'index': 0}]]}
        }
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    high_issues = [i for i in analysis['issues'] if i['severity'] == 'high']
    print(f"High issues: {len(high_issues)}")

    assert any('false path' in i['issue'].lower() for i in analysis['issues']), "Should detect missing false path"

    print("✅ IF node path detection working")


def test_webhook_authentication():
    """Test webhook authentication detection"""
    print("\n=== Testing Webhook Authentication ===\n")

    workflow = {
        'name': 'Test Webhook',
        'nodes': [
            {
                'name': 'Webhook',
                'type': 'n8n-nodes-base.webhook',
                'parameters': {
                    'path': 'test',
                    'authentication': 'none'
                },
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    security_issues = [i for i in analysis['issues'] if i['category'] == 'security']
    print(f"Security issues: {len(security_issues)}")

    assert len(security_issues) >= 1, "Should detect missing authentication"
    assert any('authentication' in i['issue'].lower() for i in security_issues), "Should mention authentication"

    print("✅ Webhook authentication detection working")


def test_credential_usage():
    """Test hardcoded credential detection"""
    print("\n=== Testing Credential Usage ===\n")

    workflow = {
        'name': 'Test Credentials',
        'nodes': [
            {
                'name': 'HTTP Request',
                'type': 'n8n-nodes-base.httpRequest',
                'parameters': {
                    'url': 'https://api.example.com',
                    'authentication': 'genericCredentialType',
                    'genericAuthType': 'httpHeaderAuth',
                    'httpHeaderAuth': {
                        'name': 'Authorization',
                        'value': 'Bearer sk-1234567890abcdefghijklmnopqrstuvwxyz'
                    }
                },
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    critical_security = [i for i in analysis['issues']
                         if i['severity'] == 'critical' and i['category'] == 'security']
    print(f"Critical security issues: {len(critical_security)}")

    # Should detect hardcoded token (sk- pattern)
    assert len(critical_security) >= 1, "Should detect hardcoded credentials"

    print("✅ Credential detection working")


def test_llm_friendly_fixes():
    """Test that LLM-friendly fixes are generated"""
    print("\n=== Testing LLM-Friendly Fixes ===\n")

    workflow = {
        'name': 'Test Fixes',
        'nodes': [
            {
                'name': 'HTTP',
                'type': 'n8n-nodes-base.httpRequest',
                'parameters': {'url': 'https://api.example.com'},
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    print(f"Total fixes: {len(analysis['llm_fixes'])}")

    assert len(analysis['llm_fixes']) > 0, "Should generate LLM fixes"

    # Check fix format
    for fix in analysis['llm_fixes']:
        assert 'node' in fix, "Fix should have node field"
        assert 'issue' in fix, "Fix should have issue field"
        assert 'fix' in fix, "Fix should have fix field"
        assert 'category' in fix, "Fix should have category field"

        # Fix should contain code or instructions
        assert len(fix['fix']) > 50, "Fix should be detailed"

    print("✅ LLM-friendly fixes working")


def test_report_formatting():
    """Test report formatting"""
    print("\n=== Testing Report Formatting ===\n")

    workflow = {
        'name': 'Test Report',
        'nodes': [
            {
                'name': 'HTTP',
                'type': 'n8n-nodes-base.httpRequest',
                'parameters': {},
                'position': [100, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)
    report = SemanticWorkflowAnalyzer.format_analysis_report(analysis, 'Test Report')

    print(f"Report length: {len(report)} characters")

    # Check report structure
    assert 'Semantic Workflow Analysis' in report, "Should have title"
    assert 'Total Issues Found' in report, "Should have summary"
    assert 'Critical' in report, "Should show critical count"
    assert 'High' in report, "Should show high count"

    if analysis['issues']:
        assert 'How to fix' in report or 'fix' in report.lower(), "Should include fixes"

    if sum(analysis['severity'].values()) == 0:
        assert 'Excellent' in report or 'No' in report, "Should indicate success"

    print("✅ Report formatting working")


def test_severity_levels():
    """Test severity categorization"""
    print("\n=== Testing Severity Levels ===\n")

    workflow = {
        'name': 'Test Severity',
        'nodes': [
            {
                'name': 'SplitBatch',
                'type': 'n8n-nodes-base.splitInBatches',
                'parameters': {},
                'position': [100, 100]
            },
            {
                'name': 'HTTP',
                'type': 'n8n-nodes-base.httpRequest',
                'parameters': {},
                'position': [200, 100]
            },
            {
                'name': 'Schedule',
                'type': 'n8n-nodes-base.scheduleTrigger',
                'parameters': {},
                'position': [300, 100]
            }
        ],
        'connections': {}
    }

    analysis = SemanticWorkflowAnalyzer.analyze_workflow_semantics(workflow)

    print(f"Severity breakdown:")
    print(f"  Critical: {analysis['severity']['critical']}")
    print(f"  High: {analysis['severity']['high']}")
    print(f"  Medium: {analysis['severity']['medium']}")
    print(f"  Low: {analysis['severity']['low']}")

    # Should have at least critical (SplitInBatches) and high (HTTP retry)
    assert analysis['severity']['critical'] >= 1, "Should have critical issues"
    assert analysis['severity']['high'] >= 1, "Should have high issues"

    print("✅ Severity levels working")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Semantic Workflow Analyzer Test Suite")
    print("="*60)

    try:
        test_http_retry_patterns()
        test_split_in_batches_completion()
        test_cron_timezone()
        test_if_node_default_path()
        test_webhook_authentication()
        test_credential_usage()
        test_llm_friendly_fixes()
        test_report_formatting()
        test_severity_levels()

        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
