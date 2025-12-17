#!/usr/bin/env python3
"""
Test GitHub Template Discovery & Import

Tests the new GitHub adapter functionality for discovering
and importing n8n workflows from GitHub repositories.
"""
import asyncio
import os
from src.n8n_workflow_builder.templates.tools import TemplateManager


async def test_github_discovery():
    """Test discovering n8n workflow repositories on GitHub"""
    print("=" * 80)
    print("🐙 TEST: GitHub Repository Discovery")
    print("=" * 80)
    print()

    manager = TemplateManager()

    # Test different search queries
    queries = [
        "n8n workflows",
        "n8n automation templates",
        "n8n examples"
    ]

    for query in queries:
        print(f"🔍 Searching for: '{query}'")
        print("-" * 80)

        try:
            repos = await manager.discover_github_templates(query=query, limit=5)

            if repos:
                print(f"✅ Found {len(repos)} repositories:\n")
                for i, repo in enumerate(repos, 1):
                    print(f"{i}. {repo['full_name']}")
                    print(f"   ⭐ Stars: {repo['stars']}")
                    print(f"   📝 Description: {repo.get('description', 'No description')[:80]}")
                    print(f"   🔗 URL: {repo['url']}")
                    topics = repo.get('topics', [])
                    if topics:
                        print(f"   🏷️  Topics: {', '.join(topics[:5])}")
                    print()
            else:
                print("⚠️  No repositories found.")
                print("   This might be due to GitHub API rate limiting.")
                print("   Consider setting GITHUB_TOKEN environment variable.\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")

        print()

    print("=" * 80)
    print()


async def test_github_repo_import():
    """Test importing templates from a specific GitHub repository"""
    print("=" * 80)
    print("📦 TEST: GitHub Repository Import")
    print("=" * 80)
    print()

    manager = TemplateManager()

    # List of known repos with n8n workflows to test
    test_repos = [
        "n8n-io/n8n-docs",  # Official n8n docs (might have examples)
        "n8n-io/n8n",       # Main n8n repo (might have workflow examples)
    ]

    for repo_name in test_repos:
        print(f"📥 Attempting to import from: {repo_name}")
        print("-" * 80)

        try:
            result = await manager.import_github_repo(repo_name, add_to_sync=False)

            if result.get('success'):
                print(f"✅ Successfully imported {result['templates_imported']} templates")

                if result['templates_imported'] > 0:
                    print("\n📋 Imported templates:")
                    for template in result.get('templates', [])[:5]:  # Show first 5
                        print(f"  • {template['name']}")
                        print(f"    Category: {template.get('category', 'unknown')}")
                        print(f"    Nodes: {template.get('node_count', 0)}")
                        print(f"    Complexity: {template.get('complexity', 'unknown')}")
                        print()
                else:
                    print("ℹ️  No workflow files found in this repository.")
                    print("   The repo might not contain n8n workflows in standard paths.")
            else:
                print(f"❌ Import failed: {result.get('error')}")

        except Exception as e:
            print(f"❌ Error during import: {e}")

        print()
        print("=" * 80)
        print()


async def test_github_source_sync():
    """Test syncing GitHub templates via TemplateManager"""
    print("=" * 80)
    print("🔄 TEST: GitHub Template Sync")
    print("=" * 80)
    print()

    manager = TemplateManager()

    # Add some repos to the GitHub source
    print("📌 Adding test repositories to GitHub source...")
    manager.github_source.add_repo("n8n-io/n8n-docs")
    print("   ✅ Added: n8n-io/n8n-docs")
    print()

    # Sync GitHub templates
    print("🔄 Syncing GitHub templates...")
    try:
        result = await manager.sync_templates(source="github", force=True)

        print(f"\n📊 Sync Results:")
        print(f"   Sources synced: {', '.join(result['synced_sources'])}")
        print(f"   Total templates: {result['total_templates']}")

        if result['errors']:
            print(f"\n⚠️  Errors:")
            for error in result['errors']:
                print(f"   • {error}")

    except Exception as e:
        print(f"❌ Sync failed: {e}")

    print()
    print("=" * 80)
    print()


async def test_github_template_search():
    """Test searching imported GitHub templates"""
    print("=" * 80)
    print("🔎 TEST: Search GitHub Templates")
    print("=" * 80)
    print()

    manager = TemplateManager()

    # First sync some templates
    print("📥 Syncing templates first...")
    await manager.sync_templates(source="all", force=False)
    print()

    # Search for GitHub templates
    print("🔍 Searching for templates from GitHub source...")
    results = await manager.search_templates(source="github", limit=10)

    if results:
        print(f"✅ Found {len(results)} GitHub templates:\n")
        for template in results[:5]:
            print(f"  • {template['name']}")
            print(f"    Source: {template['source']}")
            print(f"    URL: {template.get('source_url', 'N/A')}")
            print()
    else:
        print("ℹ️  No GitHub templates found yet.")
        print("   Try importing repositories first using test_github_repo_import()")

    print("=" * 80)
    print()


async def test_github_stats():
    """Test GitHub template statistics"""
    print("=" * 80)
    print("📊 TEST: GitHub Template Statistics")
    print("=" * 80)
    print()

    manager = TemplateManager()

    # Get overall stats
    stats = manager.get_template_stats()

    print("📈 Template Statistics:")
    print(f"   Total templates: {stats.get('total_templates', 0)}")
    print()

    print("📦 Templates by source:")
    by_source = stats.get('by_source', {})
    for source, count in by_source.items():
        print(f"   {source}: {count} templates")
    print()

    print("🔄 Sync status:")
    sync_status = stats.get('sync_status', {})
    for source, status in sync_status.items():
        if isinstance(status, dict) and status.get('synced') is not False:
            print(f"   {source}:")
            print(f"      Last sync: {status.get('last_sync', 'Never')}")
            print(f"      Templates: {status.get('template_count', 0)}")
            print(f"      Success: {'✅' if status.get('success') else '❌'}")

    print()
    print("=" * 80)
    print()


async def main():
    """Run all GitHub integration tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🐙 GitHub Template Integration Tests" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Check for GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        print("✅ GITHUB_TOKEN found - API rate limits will be higher")
    else:
        print("⚠️  GITHUB_TOKEN not set - GitHub API rate limits may apply")
        print("   Set with: export GITHUB_TOKEN='your_token_here'")
    print()

    try:
        # Test 1: Discovery
        await test_github_discovery()

        # Test 2: Import (might be slow, commented out by default)
        # await test_github_repo_import()

        # Test 3: Sync
        # await test_github_source_sync()

        # Test 4: Search
        # await test_github_template_search()

        # Test 5: Stats
        await test_github_stats()

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
