#!/usr/bin/env python3
"""
Inspect what tokens FTS5 actually indexed for the GitHub template
"""
import sqlite3
from pathlib import Path

home = Path.home()
cache_path = home / ".n8n_workflow_builder" / "template_cache.db"

conn = sqlite3.connect(str(cache_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

github_id = "github_enescingoz_awesome_n8n_templates_ai product imagines"

print("=" * 80)
print(f"🔍 FTS5 Token Analysis")
print("=" * 80)
print()

# Get the raw FTS5 data
cursor.execute("SELECT * FROM templates_fts WHERE id = ?", (github_id,))
row = cursor.fetchone()

if row:
    print("📋 Raw FTS5 Data:")
    print(f"  ID: {row['id']}")
    print(f"  Name: '{row['name']}'")
    print(f"  Description: '{row['description'][:80]}...'")
    print(f"  Category: '{row['category']}'")
    print(f"  Tags: '{row['tags']}'")
    print(f"  Author: '{row['author']}'")
    print()

    # Test what FTS5 actually searches in each column
    print("🧪 Column-specific FTS5 Tests:")

    test_cases = [
        ("name:AI*", "Search 'AI*' in name column"),
        ("name:product*", "Search 'product*' in name column"),
        ("tags:AI*", "Search 'AI*' in tags column"),
        ("tags:no-code-ai*", "Search 'no-code-ai*' in tags"),
        ("description:AI*", "Search 'AI*' in description"),
    ]

    for query, description in test_cases:
        try:
            cursor.execute("""
                SELECT id FROM templates_fts
                WHERE templates_fts MATCH ?
            """, (query,))
            results = cursor.fetchall()

            found = any(r["id"] == github_id for r in results)
            status = "✅ FOUND" if found else f"❌ NOT FOUND ({len(results)} others)"
            print(f"  {status}: {description}")
            print(f"         Query: '{query}'")

        except Exception as e:
            print(f"  ❌ ERROR: {description}")
            print(f"         Error: {e}")

        print()

else:
    print("❌ Template not found in FTS5 index!")

print("=" * 80)

# Try to understand FTS5 configuration
print("\n🔧 FTS5 Table Configuration:")
cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'templates_fts'")
result = cursor.fetchone()
if result:
    print(result["sql"])

conn.close()
