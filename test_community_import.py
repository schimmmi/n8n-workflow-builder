#!/usr/bin/env python3
"""
Test Community URL Template Import

Tests importing n8n workflow templates from direct URLs.
"""
import asyncio
from src.n8n_workflow_builder.templates.sources.github import GitHubSource
from src.n8n_workflow_builder.templates.cache import TemplateCache


async def test_community_url_import():
    """Test importing a workflow from a direct URL"""
    print("=" * 80)
    print("🌐 TEST: Community URL Template Import")
    print("=" * 80)
    print()

    # Example URLs (these would need to be actual n8n workflow JSON files)
    test_urls = [
        # n8n.io shared workflows typically have this structure
        "https://n8n.io/workflows/123.json",  # This might not work, just an example

        # GitHub raw content URLs work
        "https://raw.githubusercontent.com/n8n-io/n8n-docs/main/docs/workflows/example.json",
    ]

    github_source = GitHubSource()

    for url in test_urls:
        print(f"📥 Attempting to import from URL:")
        print(f"   {url}")
        print("-" * 80)

        try:
            # Fetch the workflow JSON
            response = await github_source.client.get(url)

            if response.status_code == 200:
                workflow_data = response.json()

                # Validate it's an n8n workflow
                if github_source._is_valid_n8n_workflow(workflow_data):
                    print("✅ Valid n8n workflow detected!")
                    print(f"   Name: {workflow_data.get('name', 'Unknown')}")
                    print(f"   Nodes: {len(workflow_data.get('nodes', []))}")
                    print(f"   Has connections: {'✅' if workflow_data.get('connections') else '❌'}")

                    # Here you would normally save it to cache
                    # cache.add_template(template_dict)
                else:
                    print("❌ Not a valid n8n workflow (missing nodes or connections)")
            elif response.status_code == 404:
                print("❌ URL not found (404)")
            else:
                print(f"❌ HTTP error: {response.status_code}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("=" * 80)
    print()


async def test_import_from_user_input():
    """Test importing workflow from user-provided JSON"""
    print("=" * 80)
    print("📝 TEST: Import from User JSON")
    print("=" * 80)
    print()

    # Example minimal n8n workflow
    example_workflow = {
        "name": "Community Example Workflow",
        "nodes": [
            {
                "parameters": {},
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "url": "https://api.example.com/data",
                    "method": "GET"
                },
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [440, 300]
            }
        ],
        "connections": {
            "Start": {
                "main": [[{"node": "HTTP Request", "type": "main", "index": 0}]]
            }
        },
        "meta": {
            "description": "Example workflow for testing community import"
        }
    }

    github_source = GitHubSource()
    cache = TemplateCache()

    print("📋 Validating example workflow...")
    if github_source._is_valid_n8n_workflow(example_workflow):
        print("✅ Valid n8n workflow structure!")
        print()

        # Create template metadata
        template_id = "community_example_001"
        print(f"💾 Saving to cache with ID: {template_id}")

        template_dict = {
            "id": template_id,
            "source": "community_url",
            "name": example_workflow["name"],
            "description": example_workflow.get("meta", {}).get("description", ""),
            "category": "integration",
            "tags": ["community", "example"],
            "nodes": example_workflow["nodes"],
            "author": "Community User",
            "source_url": "user_provided",
            "totalViews": 0,
            "createdAt": None,
            "metadata": {
                "complexity": "beginner",
                "node_count": len(example_workflow["nodes"]),
                "estimated_setup_time": "5 minutes",
                "trigger_type": "manual",
                "has_error_handling": False,
                "has_documentation": True,
                "uses_credentials": False,
            }
        }

        success = cache.add_template(template_dict)

        if success:
            print("✅ Template saved to cache successfully!")
            print()

            # Verify we can retrieve it
            print("🔍 Retrieving template from cache...")
            retrieved = cache.get_template(template_id)

            if retrieved:
                print("✅ Template retrieved successfully!")
                print(f"   Name: {retrieved['name']}")
                print(f"   Nodes: {len(retrieved.get('nodes', []))}")
                print(f"   Tags: {', '.join(retrieved.get('tags', []))}")
            else:
                print("❌ Failed to retrieve template")

            # Clean up
            print()
            print("🧹 Cleaning up test template...")
            cache.clear_cache("community_url")
            print("✅ Cleanup complete")
        else:
            print("❌ Failed to save template to cache")
    else:
        print("❌ Invalid workflow structure")

    print()
    print("=" * 80)
    print()


async def main():
    """Run all community import tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 22 + "🌐 Community Template Import Tests" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        # Test 1: URL import (might fail due to non-existent URLs)
        # await test_community_url_import()

        # Test 2: Import from user JSON (should work)
        await test_import_from_user_input()

    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 30 + "✅ Tests Complete!" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")
    print()


if __name__ == "__main__":
    asyncio.run(main())
