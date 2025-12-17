#!/usr/bin/env python3
"""
Rebuild FTS5 index from scratch
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
print("🔧 Rebuilding FTS5 Index")
print("=" * 80)
print()

# Delete all FTS5 entries
print("Clearing FTS5 index...")
cursor.execute("DELETE FROM templates_fts")
conn.commit()
print("✅ FTS5 index cleared")
print()

# Get all templates from main table
print("Fetching all templates from main table...")
cursor.execute("SELECT * FROM templates")
templates = cursor.fetchall()
print(f"Found {len(templates)} templates")
print()

# Rebuild FTS5 index
print("Rebuilding FTS5 index...")
for template in templates:
    template_id = template["id"]
    name = template["name"]
    description = template["description"] or ""
    category = template["category"] or ""
    author = template["author"] or ""

    # Get tags
    cursor.execute("SELECT tag FROM template_tags WHERE template_id = ?", (template_id,))
    tags = [row["tag"] for row in cursor.fetchall()]
    tags_str = " ".join(tags)

    # Insert into FTS5
    cursor.execute("""
        INSERT INTO templates_fts (id, name, description, category, author, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (template_id, name, description, category, author, tags_str))

    print(f"  ✅ {template_id}: {name[:50]}")

conn.commit()
print()
print("=" * 80)
print(f"✅ FTS5 index rebuilt! {len(templates)} templates indexed")
print("=" * 80)

conn.close()
