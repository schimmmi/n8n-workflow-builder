#!/usr/bin/env python3
"""Direct search test to debug why MCP tool doesn't find GitHub templates"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from n8n_workflow_builder.templates.cache import TemplateCache

cache = TemplateCache()

print("\n" + "="*80)
print("🔍 DIRECT SEARCH TEST")
print("="*80 + "\n")

# Test 1: Search "product"
print("Test 1: cache.search(query='product', limit=20)")
print("-"*80)
results = cache.search(query="product", limit=20)
print(f"Results: {len(results)}")
for r in results:
    print(f"  - {r['id']}: {r['name']} (source: {r['source']})")

print("\n" + "="*80)

# Test 2: Search "AI"
print("Test 2: cache.search(query='AI', limit=20)")
print("-"*80)
results = cache.search(query="AI", limit=20)
print(f"Results: {len(results)}")
github_results = [r for r in results if r['source'] == 'github']
print(f"GitHub results: {len(github_results)}")
for r in github_results:
    print(f"  - {r['id']}: {r['name']}")

print("\n" + "="*80)

# Test 3: Category filter
print("Test 3: cache.search(category='ai', limit=20)")
print("-"*80)
results = cache.search(category="ai", limit=20)
print(f"Results: {len(results)}")
for r in results:
    print(f"  - {r['id']}: {r['name']} (source: {r['source']})")

print("\n" + "="*80)
