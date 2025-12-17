#!/usr/bin/env python3
"""
Test searching for existing GitHub templates with detailed logging
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/search_debug.log', mode='w')
    ]
)

logger = logging.getLogger("n8n-workflow-builder")
logger.setLevel(logging.INFO)

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from n8n_workflow_builder.templates.cache import TemplateCache


def test_search_existing_github_templates():
    """Search for GitHub templates that we know exist in DB"""
    print("\n" + "="*80)
    print("🔍 SEARCH TEST - Existing GitHub Templates")
    print("="*80 + "\n")

    cache = TemplateCache()

    # Check what's in the database
    print("📊 Database Status:")
    print("-"*80)

    import sqlite3
    conn = sqlite3.connect(cache.cache_path)
    cursor = conn.cursor()

    # Main templates table
    cursor.execute("SELECT COUNT(*) FROM templates WHERE source = 'github'")
    github_count = cursor.fetchone()[0]
    print(f"GitHub templates in main table: {github_count}")

    if github_count > 0:
        cursor.execute("SELECT id, name FROM templates WHERE source = 'github' LIMIT 3")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")

    # FTS5 table
    cursor.execute("SELECT COUNT(*) FROM templates_fts WHERE id LIKE 'github_%'")
    fts_count = cursor.fetchone()[0]
    print(f"\nGitHub templates in FTS5 table: {fts_count}")

    if fts_count > 0:
        cursor.execute("SELECT id, name FROM templates_fts WHERE id LIKE 'github_%' LIMIT 3")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")

    conn.close()

    # Now test searches
    print("\n" + "="*80)
    print("🔍 SEARCH TESTS")
    print("="*80 + "\n")

    # Test 1: Search for "AI" (should find GitHub template "AI product Images")
    print("Test 1: Search for 'AI'")
    print("-"*80)
    results = cache.search(query="AI", limit=20)
    print(f"Found: {len(results)} templates")
    github_results = [r for r in results if r['source'] == 'github']
    print(f"GitHub templates: {len(github_results)}")
    if github_results:
        for r in github_results:
            print(f"  ✅ {r['id']}: {r['name']}")
    else:
        print("  ❌ No GitHub templates found!")

    # Test 2: Search for "product"
    print("\nTest 2: Search for 'product'")
    print("-"*80)
    results = cache.search(query="product", limit=20)
    print(f"Found: {len(results)} templates")
    github_results = [r for r in results if r['source'] == 'github']
    print(f"GitHub templates: {len(github_results)}")
    if github_results:
        for r in github_results:
            print(f"  ✅ {r['id']}: {r['name']}")
    else:
        print("  ❌ No GitHub templates found!")

    # Test 3: Search for "image"
    print("\nTest 3: Search for 'image'")
    print("-"*80)
    results = cache.search(query="image", limit=20)
    print(f"Found: {len(results)} templates")
    github_results = [r for r in results if r['source'] == 'github']
    print(f"GitHub templates: {len(github_results)}")
    if github_results:
        for r in github_results:
            print(f"  ✅ {r['id']}: {r['name']}")
    else:
        print("  ❌ No GitHub templates found!")

    # Test 4: Direct FTS5 query with column prefix
    print("\nTest 4: Direct FTS5 query (column-specific)")
    print("-"*80)
    conn = sqlite3.connect(cache.cache_path)
    cursor = conn.cursor()

    # Try column-specific queries
    queries = [
        ("name:product*", "name:product*"),
        ("name:AI*", "name:AI*"),
        ("tags:AI*", "tags:AI*"),
        ("product*", "product* (no column)"),
        ("AI*", "AI* (no column)")
    ]

    for fts_query, label in queries:
        try:
            cursor.execute("SELECT id, name FROM templates_fts WHERE templates_fts MATCH ?", (fts_query,))
            matches = cursor.fetchall()
            print(f"  {label}: {len(matches)} matches")
            if matches:
                for m in matches[:2]:
                    print(f"    - {m[0]}: {m[1]}")
        except Exception as e:
            print(f"  {label}: ERROR - {e}")

    conn.close()

    print("\n" + "="*80)
    print("📝 Full log written to: /tmp/search_debug.log")
    print("="*80)


if __name__ == "__main__":
    test_search_existing_github_templates()
