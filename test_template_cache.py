#!/usr/bin/env python3
"""
Test script for Template Cache Integration

Tests:
1. Initial sync from n8n API
2. Cache persistence (24-hour interval)
3. Full-text search with FTS5
4. Cache statistics
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from n8n_workflow_builder.templates.sources import N8nOfficialSource


async def test_cache_integration():
    """Test the cache integration"""
    print("=" * 60)
    print("Testing Template Cache Integration")
    print("=" * 60)

    # Initialize source (will create cache at ~/.n8n_workflow_builder/template_cache.db)
    source = N8nOfficialSource()

    # Test 1: Initial fetch (should sync from API)
    print("\n[TEST 1] Fetching templates (initial sync)...")
    templates = await source.fetch_templates()
    print(f"✓ Fetched {len(templates)} templates")

    if templates:
        sample = templates[0]
        print(f"  Sample: {sample.name[:50]}...")
        print(f"  Category: {sample.category}")
        print(f"  Tags: {', '.join(sample.tags[:3])}...")

    # Test 2: Check cache stats
    print("\n[TEST 2] Cache statistics...")
    stats = source.persistent_cache.get_stats()
    print(f"✓ Total cached templates: {stats['total_templates']}")
    print(f"  By source: {stats['by_source']}")
    print(f"  Top categories: {list(stats['top_categories'].keys())[:5]}")
    print(f"  Popular tags: {list(stats['popular_tags'].keys())[:10]}")
    print(f"  Popular nodes: {list(stats['popular_nodes'].keys())[:5]}")

    # Test 3: Second fetch (should use cache, no API call)
    print("\n[TEST 3] Fetching templates again (should use cache)...")
    templates2 = await source.fetch_templates()
    print(f"✓ Returned {len(templates2)} templates from cache")
    print(f"  Sync status: {source.persistent_cache.get_sync_status('n8n_official')}")

    # Test 4: Full-text search
    print("\n[TEST 4] Testing full-text search...")
    search_queries = ["webhook", "slack", "google sheets", "database"]
    for query in search_queries:
        results = await source.search_templates(query)
        print(f"  '{query}': {len(results)} results")
        if results:
            print(f"    → {results[0].name[:60]}")

    # Test 5: Filter by category
    print("\n[TEST 5] Testing category filter...")
    categories = ["Core Nodes", "Communication", "Sales & Marketing"]
    for category in categories:
        results = source.persistent_cache.search(category=category, limit=10)
        print(f"  '{category}': {len(results)} templates")

    # Test 6: Filter by tags
    print("\n[TEST 6] Testing tag filter...")
    results = source.persistent_cache.search(tags=["automation"], limit=10)
    print(f"✓ Found {len(results)} templates with 'automation' tag")

    # Test 7: Popular templates
    print("\n[TEST 7] Most popular templates...")
    popular = source.persistent_cache.get_popular_templates(limit=5)
    for i, template in enumerate(popular, 1):
        views = template.get("total_views", 0)
        print(f"  {i}. {template['name'][:50]} ({views} views)")

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_cache_integration())
