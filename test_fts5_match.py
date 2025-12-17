#!/usr/bin/env python3
"""
Test FTS5 matching for GitHub template
"""
import sqlite3
from pathlib import Path

# Connect to cache database
home = Path.home()
cache_path = home / ".n8n_workflow_builder" / "template_cache.db"

conn = sqlite3.connect(str(cache_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

github_id = "github_enescingoz_awesome_n8n_templates_ai product imagines"

print("=" * 80)
print(f"🧪 Testing FTS5 Queries for Template: {github_id}")
print("=" * 80)
print()

# Test various queries
test_queries = [
    "AI",
    "AI*",
    "product",
    "product*",
    "image",
    "images",
    "Images",
    '"AI product"',
    "AI OR product",
    "AI* OR product*",
    f'id:"{github_id}"',
]

for query in test_queries:
    print(f"Query: '{query}'")
    try:
        cursor.execute(f"""
            SELECT id, name
            FROM templates_fts
            WHERE templates_fts MATCH ?
            LIMIT 10
        """, (query,))
        results = cursor.fetchall()

        github_found = any(row["id"] == github_id for row in results)

        if github_found:
            print(f"  ✅ FOUND GitHub template!")
        else:
            print(f"  ❌ GitHub template NOT in results (found {len(results)} others)")

        if len(results) <= 3:
            for row in results:
                marker = "🎯" if row["id"] == github_id else "  "
                print(f"    {marker} {row['name'][:60]}")

    except Exception as e:
        print(f"  ❌ Query failed: {e}")

    print()

conn.close()

print("=" * 80)
print("Test complete!")
print("=" * 80)
