#!/usr/bin/env python3
"""
Test script for n8n Workflow Builder MCP Server
Quick verification that everything works
"""
import asyncio
import os
from dotenv import load_dotenv
import httpx

async def test_n8n_connection():
    """Test n8n API connection"""
    load_dotenv()
    
    api_url = os.getenv("N8N_API_URL")
    api_key = os.getenv("N8N_API_KEY")
    
    print("🧪 Testing n8n Connection...")
    print(f"📍 API URL: {api_url}")
    print(f"🔑 API Key: {api_key[:20]}..." if api_key and len(api_key) > 20 else "🔑 API Key: NOT SET!")
    
    if not api_url or not api_key:
        print("❌ ERROR: N8N_API_URL or N8N_API_KEY not set in .env")
        print("\n💡 Quick Fix:")
        print("1. Copy .env.example to .env")
        print("2. Add your n8n URL and API Key")
        print("3. Get API Key from: n8n Settings > API > Create New API Key")
        return False
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test API connection
            print("\n📡 Testing API connection...")
            headers = {"X-N8N-API-KEY": api_key}
            response = await client.get(
                f"{api_url}/api/v1/workflows",
                headers=headers
            )
            
            if response.status_code == 200:
                workflows = response.json()
                print(f"✅ Connection successful!")
                print(f"📊 Found {len(workflows.get('data', []))} workflows")
                
                # List first 3 workflows
                if workflows.get('data'):
                    print("\n🔍 Your workflows:")
                    for wf in workflows['data'][:3]:
                        status = "🟢" if wf.get('active') else "⚪"
                        print(f"  {status} {wf.get('name')} (ID: {wf.get('id')})")
                    
                    if len(workflows['data']) > 3:
                        print(f"  ... and {len(workflows['data']) - 3} more")
                else:
                    print("📝 No workflows found yet - create one in n8n!")
                
                return True
            
            elif response.status_code == 401:
                print("❌ Authentication failed!")
                print("\n💡 Your API Key is invalid or expired.")
                print("Fix: Go to n8n Settings > API > Create New API Key")
                return False
            
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
    
    except httpx.ConnectError:
        print(f"❌ Cannot connect to {api_url}")
        print("\n💡 Possible issues:")
        print("- n8n instance not running?")
        print("- Wrong URL in .env?")
        print("- Firewall/VPN blocking?")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_workflow_builder():
    """Test workflow builder logic"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from n8n_workflow_builder.server import WorkflowBuilder
    
    print("\n\n🧠 Testing Workflow Builder AI...")
    
    builder = WorkflowBuilder()
    
    # Test 1: Node suggestions
    print("\n📝 Test 1: Node Suggestions")
    description = "daily report from postgres to slack"
    suggestions = builder.suggest_nodes(description)
    
    if suggestions:
        print(f"✅ Found {len(suggestions)} node suggestions:")
        for node in suggestions[:3]:
            print(f"  • {node['name']}")
    else:
        print("⚠️ No suggestions found")
    
    # Test 2: Workflow analysis
    print("\n📝 Test 2: Workflow Analysis")
    test_workflow = {
        "nodes": [
            {"name": "Webhook", "type": "webhook"},
            {"name": "HTTP Request", "type": "http"},
            {"name": "Set", "type": "set"}
        ]
    }
    analysis = builder.analyze_workflow(test_workflow)
    print(f"✅ Analysis complete:")
    print(f"  • Nodes: {analysis['total_nodes']}")
    print(f"  • Complexity: {analysis['complexity']}")
    print(f"  • Issues: {len(analysis['issues'])}")
    print(f"  • Suggestions: {len(analysis['suggestions'])}")
    
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 n8n Workflow Builder MCP Server - Test Suite")
    print("=" * 60)
    
    # Test 1: API Connection
    api_ok = await test_n8n_connection()
    
    # Test 2: Workflow Builder
    builder_ok = await test_workflow_builder()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"n8n API Connection: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"Workflow Builder:   {'✅ PASS' if builder_ok else '❌ FAIL'}")
    
    if api_ok and builder_ok:
        print("\n🎉 All tests passed! You're ready to go!")
        print("\n📚 Next steps:")
        print("1. Add MCP config to Claude Desktop (see README.md)")
        print("2. Restart Claude")
        print("3. Ask Claude: 'Show me my n8n workflows'")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("💡 See QUICKSTART.md for troubleshooting tips")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
