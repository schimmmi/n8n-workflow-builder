#!/usr/bin/env python3
"""
Test GitHub Template Import with Comprehensive Logging

This script imports a GitHub repo and traces every step of the FTS5 indexing process.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging to see EVERYTHING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/github_import_debug.log', mode='w')
    ]
)

logger = logging.getLogger("n8n-workflow-builder")
logger.setLevel(logging.INFO)

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from n8n_workflow_builder.templates.tools import TemplateManager


async def test_github_import_with_logging():
    """Import GitHub repo and trace all logging"""
    print("\n" + "="*80)
    print("🔍 GITHUB TEMPLATE IMPORT - DETAILED TRACE")
    print("="*80 + "\n")

    manager = TemplateManager()

    # Test repo - using one we know has workflows (from previous tests)
    repo = "saiteki-tech/n8n-workflows"

    print(f"📦 Importing from: {repo}")
    print(f"Cache instance ID: {id(manager.cache)}")
    print(f"GitHub cache instance ID: {id(manager.github_source.persistent_cache)}")
    print()

    # Check if they're the same instance
    if id(manager.cache) == id(manager.github_source.persistent_cache):
        print("✅ Cache instances are SHARED (correct)")
    else:
        print("❌ Cache instances are DIFFERENT (BUG!)")

    print("\n" + "-"*80)
    print("Starting import...")
    print("-"*80 + "\n")

    # Import templates
    result = await manager.import_github_repo(repo)

    print("\n" + "-"*80)
    print("Import completed!")
    print("-"*80)
    print(f"Result: {result}")
    print()

    # Now test search
    print("\n" + "="*80)
    print("🔍 TESTING SEARCH AFTER IMPORT")
    print("="*80 + "\n")

    # Search for "AI"
    print("Searching for 'AI'...")
    results = manager.cache.search(query="AI", limit=10)
    print(f"Found {len(results)} results")

    if results:
        print("\nMatches:")
        for r in results[:5]:
            print(f"  - {r['id']}: {r['name']} (source: {r['source']})")
    else:
        print("❌ No results!")

        # Check if GitHub templates exist in DB
        print("\nChecking main templates table...")
        import sqlite3
        conn = sqlite3.connect(manager.cache.cache_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, source FROM templates WHERE source = 'github'")
        github_templates = cursor.fetchall()
        print(f"GitHub templates in main table: {len(github_templates)}")
        if github_templates:
            print("Sample:")
            for t in github_templates[:3]:
                print(f"  - {t[0]}: {t[1]}")

        # Check FTS5 table
        print("\nChecking FTS5 table...")
        cursor.execute("SELECT id, name FROM templates_fts WHERE id LIKE 'github_%'")
        fts_templates = cursor.fetchall()
        print(f"GitHub templates in FTS5: {len(fts_templates)}")
        if fts_templates:
            print("Sample:")
            for t in fts_templates[:3]:
                print(f"  - {t[0]}: {t[1]}")

        conn.close()

    print("\n" + "="*80)
    print("📝 Full log written to: /tmp/github_import_debug.log")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_github_import_with_logging())
