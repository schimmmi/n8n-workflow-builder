#!/usr/bin/env python3
"""
Debug script to inspect FTS5 index
"""
import sqlite3
from pathlib import Path

# Connect to cache database
home = Path.home()
cache_path = home / ".n8n_workflow_builder" / "template_cache.db"

conn = sqlite3.connect(str(cache_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("📊 FTS5 Index Debug")
print("=" * 80)
print()

# Check templates table
cursor.execute("SELECT COUNT(*) as count FROM templates")
total = cursor.fetchone()["count"]
print(f"Total templates in main table: {total}")

# Check FTS5 table
cursor.execute("SELECT COUNT(*) as count FROM templates_fts")
fts_total = cursor.fetchone()["count"]
print(f"Total templates in FTS5 index: {fts_total}")
print()

if total != fts_total:
    print(f"⚠️  MISMATCH! {total} in main table but {fts_total} in FTS5 index!")
    print()

# Show GitHub templates in main table
print("GitHub Templates in main table:")
cursor.execute("SELECT id, name, category FROM templates WHERE source = 'github'")
for row in cursor.fetchall():
    print(f"  - {row['id']}: {row['name']} (category: {row['category']})")
print()

# Show GitHub templates in FTS5 index
print("GitHub Templates in FTS5 index:")
cursor.execute("SELECT id, name FROM templates_fts WHERE id LIKE 'github%'")
fts_github = cursor.fetchall()
if fts_github:
    for row in fts_github:
        print(f"  - {row['id']}: {row['name']}")
else:
    print("  ❌ NO GITHUB TEMPLATES IN FTS5 INDEX!")
print()

# Try direct FTS5 query for "AI"
print("Testing FTS5 query for 'AI*':")
try:
    cursor.execute("SELECT id, name FROM templates_fts WHERE templates_fts MATCH 'AI*' LIMIT 5")
    results = cursor.fetchall()
    if results:
        for row in results:
            print(f"  ✅ {row['id']}: {row['name']}")
    else:
        print("  ❌ No matches")
except Exception as e:
    print(f"  ❌ Query failed: {e}")
print()

# Show all FTS5 content for GitHub template
cursor.execute("SELECT id FROM templates WHERE source = 'github' LIMIT 1")
github_id_row = cursor.fetchone()
if github_id_row:
    github_id = github_id_row["id"]
    print(f"FTS5 content for GitHub template {github_id}:")
    cursor.execute("SELECT * FROM templates_fts WHERE id = ?", (github_id,))
    fts_row = cursor.fetchone()
    if fts_row:
        print(f"  name: '{fts_row['name']}'")
        print(f"  description: '{fts_row['description'][:100]}...'")
        print(f"  category: '{fts_row['category']}'")
        print(f"  tags: '{fts_row['tags']}'")
        print(f"  author: '{fts_row['author']}'")
    else:
        print("  ❌ NOT FOUND IN FTS5!")
print()

conn.close()

print("=" * 80)
print("Debug complete!")
print("=" * 80)
