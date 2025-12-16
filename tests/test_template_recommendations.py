#!/usr/bin/env python3
"""
Test Template Recommendation Engine
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from n8n_workflow_builder.server import TemplateRecommendationEngine, WORKFLOW_TEMPLATES


def test_recommend_templates():
    """Test template recommendation based on description"""
    print("\n=== Testing Template Recommendations ===\n")

    # Test case 1: API endpoint
    print("Test 1: Looking for API endpoint workflow")
    recommendations = TemplateRecommendationEngine.recommend_templates(
        "I need to create a REST API endpoint that receives webhook data and processes it",
        workflow_goal="Build API gateway"
    )

    print(f"Found {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"  - {rec['template']['name']}: {rec['match_percentage']}% match")

    assert len(recommendations) > 0, "Should find at least one recommendation"
    assert recommendations[0]['template_id'] == 'api_endpoint', "Top recommendation should be api_endpoint"

    # Test case 2: Database sync
    print("\nTest 2: Looking for database synchronization")
    recommendations = TemplateRecommendationEngine.recommend_templates(
        "sync data from API to database every hour"
    )

    print(f"Found {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"  - {rec['template']['name']}: {rec['match_percentage']}% match")

    assert len(recommendations) > 0, "Should find recommendations"
    # data_sync should be in top recommendations
    template_ids = [r['template_id'] for r in recommendations]
    assert 'data_sync' in template_ids, "data_sync should be recommended"

    # Test case 3: Email automation
    print("\nTest 3: Looking for email processing")
    recommendations = TemplateRecommendationEngine.recommend_templates(
        "process incoming emails and trigger actions based on content"
    )

    print(f"Found {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"  - {rec['template']['name']}: {rec['match_percentage']}% match")

    template_ids = [r['template_id'] for r in recommendations]
    assert 'email_automation' in template_ids, "email_automation should be recommended"

    print("\n✅ All recommendation tests passed!")


def test_search_templates():
    """Test template search functionality"""
    print("\n=== Testing Template Search ===\n")

    # Test search for 'notification'
    results = TemplateRecommendationEngine.search_templates("notification")
    print(f"Search 'notification': Found {len(results)} templates")
    for r in results:
        print(f"  - {r['name']}")

    assert len(results) > 0, "Should find notification-related templates"

    # Test search for 'database'
    results = TemplateRecommendationEngine.search_templates("database")
    print(f"\nSearch 'database': Found {len(results)} templates")
    for r in results:
        print(f"  - {r['name']}")

    assert len(results) > 0, "Should find database-related templates"

    print("\n✅ All search tests passed!")


def test_category_filtering():
    """Test getting templates by category"""
    print("\n=== Testing Category Filtering ===\n")

    # Test API category
    api_templates = TemplateRecommendationEngine.get_templates_by_category("api")
    print(f"API category: {len(api_templates)} templates")
    for t in api_templates:
        print(f"  - {t['name']}")

    assert len(api_templates) > 0, "Should have API templates"

    # Test reporting category
    reporting_templates = TemplateRecommendationEngine.get_templates_by_category("reporting")
    print(f"\nReporting category: {len(reporting_templates)} templates")
    for t in reporting_templates:
        print(f"  - {t['name']}")

    print("\n✅ All category filtering tests passed!")


def test_difficulty_filtering():
    """Test getting templates by difficulty"""
    print("\n=== Testing Difficulty Filtering ===\n")

    # Test each difficulty level
    for difficulty in ["beginner", "intermediate", "advanced"]:
        templates = TemplateRecommendationEngine.get_templates_by_difficulty(difficulty)
        print(f"{difficulty.title()}: {len(templates)} templates")
        for t in templates:
            print(f"  - {t['name']}")
        print()

    print("✅ All difficulty filtering tests passed!")


def test_relevance_scoring():
    """Test relevance score calculation"""
    print("\n=== Testing Relevance Scoring ===\n")

    # Test exact keyword match
    template = WORKFLOW_TEMPLATES['api_endpoint']
    score1 = TemplateRecommendationEngine.calculate_relevance_score(
        template,
        "I want to build a REST API endpoint with webhook",
        "Create API gateway"
    )
    print(f"API endpoint with exact keywords: {score1:.2f} ({int(score1*100)}%)")

    # Test partial match
    score2 = TemplateRecommendationEngine.calculate_relevance_score(
        template,
        "I need an HTTP interface",
        None
    )
    print(f"API endpoint with partial match: {score2:.2f} ({int(score2*100)}%)")

    # Test no match
    score3 = TemplateRecommendationEngine.calculate_relevance_score(
        template,
        "Send daily reports via email",
        None
    )
    print(f"API endpoint with no match: {score3:.2f} ({int(score3*100)}%)")

    assert score1 > score2 > score3, "Scores should decrease with relevance"

    print("\n✅ All scoring tests passed!")


def test_template_report():
    """Test template library report generation"""
    print("\n=== Testing Template Report Generation ===\n")

    report = TemplateRecommendationEngine.generate_template_report()

    # Check report contains expected sections
    assert "Template Library Report" in report
    assert "Categories:" in report
    assert "Difficulty Distribution:" in report
    assert "All Templates:" in report

    # Check all templates are listed
    for template_id in WORKFLOW_TEMPLATES.keys():
        assert template_id in report, f"Template {template_id} should be in report"

    print(f"Report generated successfully ({len(report)} characters)")
    print("\n✅ Template report test passed!")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Template Recommendation Engine Test Suite")
    print("="*60)

    try:
        test_relevance_scoring()
        test_recommend_templates()
        test_search_templates()
        test_category_filtering()
        test_difficulty_filtering()
        test_template_report()

        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
