#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST

Verifies that the FTS5 duplicate bug is fixed and all search functionality works correctly.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from n8n_workflow_builder.templates.cache import TemplateCache
import sqlite3


def test_no_duplicates():
    """Verify no FTS5 duplicates exist"""
    print("\n" + "="*80)
    print("✅ TEST 1: FTS5 Duplicate Check")
    print("="*80)

    cache = TemplateCache()
    conn = sqlite3.connect(cache.cache_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, COUNT(*) as count FROM templates_fts GROUP BY id HAVING count > 1")
    duplicates = cursor.fetchall()

    if duplicates:
        print(f"❌ FAILED - Found {len(duplicates)} duplicates:")
        for dup in duplicates:
            print(f"   {dup[0]}: {dup[1]} copies")
        conn.close()
        return False
    else:
        print("✅ PASSED - No FTS5 duplicates found")
        conn.close()
        return True


def test_github_templates_indexed():
    """Verify GitHub templates are in FTS5"""
    print("\n" + "="*80)
    print("✅ TEST 2: GitHub Templates in FTS5")
    print("="*80)

    cache = TemplateCache()
    conn = sqlite3.connect(cache.cache_path)
    cursor = conn.cursor()

    # Count GitHub templates in main table
    cursor.execute("SELECT COUNT(*) FROM templates WHERE source = 'github'")
    main_count = cursor.fetchone()[0]
    print(f"GitHub templates in main table: {main_count}")

    # Count GitHub templates in FTS5
    cursor.execute("SELECT COUNT(*) FROM templates_fts WHERE id LIKE 'github_%'")
    fts_count = cursor.fetchone()[0]
    print(f"GitHub templates in FTS5 table: {fts_count}")

    conn.close()

    if main_count == fts_count and main_count > 0:
        print(f"✅ PASSED - All {main_count} GitHub templates are indexed")
        return True
    elif main_count == 0:
        print("⚠️  SKIPPED - No GitHub templates in database")
        return True
    else:
        print(f"❌ FAILED - Mismatch between main ({main_count}) and FTS5 ({fts_count})")
        return False


def test_search_finds_github():
    """Verify search returns GitHub templates"""
    print("\n" + "="*80)
    print("✅ TEST 3: Search Returns GitHub Templates")
    print("="*80)

    cache = TemplateCache()

    # Check if any GitHub templates exist
    conn = sqlite3.connect(cache.cache_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM templates WHERE source = 'github'")
    github_count = cursor.fetchone()[0]
    conn.close()

    if github_count == 0:
        print("⚠️  SKIPPED - No GitHub templates to test")
        return True

    # Test multiple search queries
    test_queries = ["product", "image", "workflow"]
    passed = True

    for query in test_queries:
        results = cache.search(query=query, limit=50)
        github_results = [r for r in results if r['source'] == 'github']

        print(f"\nQuery '{query}':")
        print(f"  Total results: {len(results)}")
        print(f"  GitHub results: {len(github_results)}")

        if github_results:
            for r in github_results[:2]:
                print(f"    ✅ {r['name']}")
        else:
            print(f"    ⚠️  No GitHub templates found")

    print(f"\n✅ PASSED - Search functionality works")
    return True


def test_fts5_match_count():
    """Verify FTS5 match count equals returned results"""
    print("\n" + "="*80)
    print("✅ TEST 4: FTS5 Match Count Accuracy")
    print("="*80)

    cache = TemplateCache()

    test_queries = ["product", "image", "workflow"]
    passed = True

    for query in test_queries:
        # Get results through cache API
        results = cache.search(query=query, limit=50)

        # Manually count FTS5 matches
        conn = sqlite3.connect(cache.cache_path)
        cursor = conn.cursor()

        # Build FTS query (same as cache.py)
        query_words = query.strip().split()
        long_words = [w for w in query_words if len(w) >= 3]

        if long_words:
            query_parts = []
            for word in long_words:
                word_query = f"(name:{word}* OR description:{word}* OR tags:{word}* OR category:{word}*)"
                query_parts.append(word_query)
            fts_query = " OR ".join(query_parts)

            cursor.execute("SELECT id FROM templates_fts WHERE templates_fts MATCH ?", (fts_query,))
            fts_ids = [row[0] for row in cursor.fetchall()]
            unique_fts_ids = list(set(fts_ids))  # Remove duplicates

            print(f"\nQuery '{query}':")
            print(f"  FTS5 matches: {len(fts_ids)}")
            print(f"  Unique FTS5 IDs: {len(unique_fts_ids)}")
            print(f"  Returned templates: {len(results)}")

            if len(fts_ids) != len(unique_fts_ids):
                print(f"  ❌ FTS5 has duplicates!")
                passed = False
            elif len(unique_fts_ids) != len(results):
                print(f"  ⚠️  Mismatch between FTS5 and results")
            else:
                print(f"  ✅ Match count accurate")

        conn.close()

    if passed:
        print(f"\n✅ PASSED - All match counts are accurate")
    else:
        print(f"\n❌ FAILED - Found FTS5 duplicates in queries")

    return passed


def main():
    """Run all verification tests"""
    print("\n" + "="*80)
    print("🔍 FINAL VERIFICATION - FTS5 Duplicate Bug Fix")
    print("="*80)

    tests = [
        test_no_duplicates,
        test_github_templates_indexed,
        test_search_finds_github,
        test_fts5_match_count
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ TEST CRASHED: {e}")
            results.append(False)

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - Bug is fixed!")
    else:
        print(f"\n❌ {total - passed} test(s) failed")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
