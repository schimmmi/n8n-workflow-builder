#!/usr/bin/env python3
"""
Test script for Intent-Based Template Search

Demonstrates the new semantic search capabilities with
GitHub template integration.
"""
import asyncio
from src.n8n_workflow_builder.templates.tools import TemplateManager


async def test_intent_search():
    """Test intent-based template search"""
    print("🚀 Testing Intent-Based Template Search\n")

    # Initialize template manager
    manager = TemplateManager()

    # Sync templates first
    print("📥 Syncing templates from n8n official...")
    sync_result = await manager.sync_templates(source="n8n_official")
    print(f"✅ Synced {sync_result['total_templates']} templates\n")

    # Test queries
    test_queries = [
        "I need to automatically respond to customer emails with AI",
        "Send notifications to Slack when something happens",
        "Process data from GitHub and store in database",
        "Schedule a daily report and send via email",
    ]

    for query in test_queries:
        print(f"🔍 Query: \"{query}\"")
        print("-" * 80)

        # Search using intent-based matching
        results = await manager.search_templates_by_intent(
            query=query,
            min_score=0.3,
            limit=5
        )

        if results:
            print(f"Found {len(results)} matching templates:\n")
            for i, template in enumerate(results, 1):
                print(f"{i}. {template['name']} ({template['match_percentage']} match)")
                print(f"   Category: {template['category']}")
                print(f"   Tags: {', '.join(template.get('tags', [])[:5])}")
                print(f"   Nodes: {template.get('node_count', 0)} nodes")
                print()

            # Explain the top match
            if results:
                top_template = results[0]
                print(f"📊 Explanation for top match ({top_template['name']}):")
                explanation = manager.explain_template_match(query, top_template['id'])
                breakdown = explanation.get('breakdown', {})
                print(f"   Goal similarity: {breakdown.get('goal_similarity', 0):.2f}")
                print(f"   Node overlap: {breakdown.get('node_overlap', 0):.2f}")
                print(f"   Trigger match: {breakdown.get('trigger_match', 0):.2f}")
                print(f"   Action match: {breakdown.get('action_match', 0):.2f}")
                print()
        else:
            print("No templates found matching this query.\n")

        print("=" * 80)
        print()


async def test_github_discovery():
    """Test GitHub repository discovery"""
    print("\n🐙 Testing GitHub Template Discovery\n")

    manager = TemplateManager()

    print("🔍 Searching for n8n workflow repositories on GitHub...")
    repos = await manager.discover_github_templates(
        query="n8n workflows",
        limit=5
    )

    if repos:
        print(f"\n✅ Found {len(repos)} repositories:\n")
        for i, repo in enumerate(repos, 1):
            print(f"{i}. {repo['full_name']} ⭐ {repo['stars']}")
            print(f"   Description: {repo.get('description', 'No description')}")
            print(f"   URL: {repo['url']}")
            print(f"   Topics: {', '.join(repo.get('topics', [])[:5])}")
            print()
    else:
        print("⚠️  No repositories found. This might be due to GitHub API rate limiting.")
        print("    Consider setting GITHUB_TOKEN environment variable.")


async def test_github_import():
    """Test importing templates from a GitHub repository"""
    print("\n📦 Testing GitHub Repository Import\n")

    manager = TemplateManager()

    # Example: Try to import from a well-known n8n workflows repo
    repo_name = "n8n-io/n8n-docs"  # n8n official docs repo often has example workflows

    print(f"Attempting to import templates from {repo_name}...")

    try:
        result = await manager.import_github_repo(repo_name, add_to_sync=False)

        if result.get('success'):
            print(f"✅ Successfully imported {result['templates_imported']} templates")
            if result.get('templates'):
                print("\nImported templates:")
                for template in result['templates'][:3]:  # Show first 3
                    print(f"  - {template['name']} ({template['node_count']} nodes)")
        else:
            print(f"❌ Import failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error during import: {e}")


async def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 Intent-Based Template Search & GitHub Integration Test")
    print("=" * 80)
    print()

    try:
        # Test 1: Intent-based search
        await test_intent_search()

        # Test 2: GitHub discovery
        await test_github_discovery()

        # Test 3: GitHub import (commented out by default to avoid rate limiting)
        # await test_github_import()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
