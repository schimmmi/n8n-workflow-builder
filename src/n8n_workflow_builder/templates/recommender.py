#!/usr/bin/env python3
"""
Template Recommendation Engine
AI-powered template recommendations based on workflow descriptions and goals
"""
from typing import Dict, List, Optional

# Enhanced Workflow Templates with metadata
WORKFLOW_TEMPLATES = {
    "api_endpoint": {
        "name": "Simple API Endpoint",
        "description": "RESTful API endpoint with data processing and external API integration",
        "category": "api",
        "difficulty": "beginner",
        "tags": ["api", "webhook", "http", "rest"],
        "use_cases": ["Create REST API", "API Gateway", "Webhook receiver", "Data transformation"],
        "keywords": ["api", "endpoint", "webhook", "http", "rest", "request", "response"],
        "estimated_time": "15 minutes",
        "nodes": [
            {"type": "webhook", "name": "Webhook"},
            {"type": "set", "name": "Process Data"},
            {"type": "http_request", "name": "Call External API"},
            {"type": "code", "name": "Transform Response"},
            {"type": "respond_to_webhook", "name": "Return Response"}
        ],
        "connections": "linear"
    },
    "scheduled_report": {
        "name": "Daily Report Generator",
        "description": "Automated report generation with database queries and Slack notifications",
        "category": "reporting",
        "difficulty": "intermediate",
        "tags": ["schedule", "report", "database", "slack", "automation"],
        "use_cases": ["Daily reports", "Analytics automation", "Team updates", "Data aggregation"],
        "keywords": ["report", "daily", "schedule", "database", "metrics", "analytics", "slack"],
        "estimated_time": "30 minutes",
        "nodes": [
            {"type": "schedule", "name": "Daily at 9AM"},
            {"type": "postgres", "name": "Fetch Data"},
            {"type": "function", "name": "Calculate Metrics"},
            {"type": "set", "name": "Format Report"},
            {"type": "slack", "name": "Send to Slack"}
        ],
        "connections": "linear"
    },
    "data_sync": {
        "name": "Database Sync",
        "description": "Periodic data synchronization between API and database with error notifications",
        "category": "integration",
        "difficulty": "intermediate",
        "tags": ["sync", "database", "api", "integration", "automation"],
        "use_cases": ["Data synchronization", "ETL pipelines", "Database updates", "API to DB sync"],
        "keywords": ["sync", "database", "api", "fetch", "update", "integration", "etl"],
        "estimated_time": "25 minutes",
        "nodes": [
            {"type": "schedule", "name": "Every Hour"},
            {"type": "http_request", "name": "Fetch from API"},
            {"type": "if", "name": "Has New Data?"},
            {"type": "postgres", "name": "Insert/Update"},
            {"type": "telegram", "name": "Notify on Errors"}
        ],
        "connections": "conditional"
    },
    "email_automation": {
        "name": "Email Automation & Processing",
        "description": "Monitor emails, extract data, and trigger actions based on content",
        "category": "communication",
        "difficulty": "intermediate",
        "tags": ["email", "gmail", "automation", "processing"],
        "use_cases": ["Email monitoring", "Invoice processing", "Support automation", "Email to task"],
        "keywords": ["email", "gmail", "inbox", "read", "parse", "automation", "trigger"],
        "estimated_time": "20 minutes",
        "nodes": [
            {"type": "gmail_trigger", "name": "Gmail Trigger"},
            {"type": "code", "name": "Parse Email Content"},
            {"type": "if", "name": "Check Conditions"},
            {"type": "http_request", "name": "Process Data"},
            {"type": "gmail", "name": "Send Response"}
        ],
        "connections": "conditional"
    },
    "webhook_to_database": {
        "name": "Webhook to Database Pipeline",
        "description": "Capture webhook data, validate, and store in database",
        "category": "data_pipeline",
        "difficulty": "beginner",
        "tags": ["webhook", "database", "storage", "validation"],
        "use_cases": ["Form submissions", "Event logging", "Data collection", "Integration endpoints"],
        "keywords": ["webhook", "database", "store", "save", "persist", "collect"],
        "estimated_time": "15 minutes",
        "nodes": [
            {"type": "webhook", "name": "Receive Data"},
            {"type": "set", "name": "Validate & Transform"},
            {"type": "postgres", "name": "Save to Database"},
            {"type": "respond_to_webhook", "name": "Acknowledge"}
        ],
        "connections": "linear"
    },
    "notification_system": {
        "name": "Multi-Channel Notification System",
        "description": "Send notifications to multiple channels (Slack, Telegram, Email)",
        "category": "notification",
        "difficulty": "beginner",
        "tags": ["notification", "slack", "telegram", "email", "alert"],
        "use_cases": ["System alerts", "Status updates", "Error notifications", "User notifications"],
        "keywords": ["notify", "alert", "message", "send", "slack", "telegram", "email"],
        "estimated_time": "20 minutes",
        "nodes": [
            {"type": "webhook", "name": "Trigger"},
            {"type": "set", "name": "Format Message"},
            {"type": "slack", "name": "Send to Slack"},
            {"type": "telegram", "name": "Send to Telegram"},
            {"type": "gmail", "name": "Send Email"}
        ],
        "connections": "parallel"
    },
    "data_enrichment": {
        "name": "Data Enrichment Pipeline",
        "description": "Fetch data, enrich with external APIs, and aggregate results",
        "category": "data_pipeline",
        "difficulty": "advanced",
        "tags": ["data", "enrichment", "api", "aggregation", "processing"],
        "use_cases": ["Lead enrichment", "Data augmentation", "API mashup", "Information gathering"],
        "keywords": ["enrich", "enhance", "augment", "api", "data", "combine", "merge"],
        "estimated_time": "35 minutes",
        "nodes": [
            {"type": "webhook", "name": "Input"},
            {"type": "http_request", "name": "Fetch Primary Data"},
            {"type": "http_request", "name": "Enrich from API 1"},
            {"type": "http_request", "name": "Enrich from API 2"},
            {"type": "code", "name": "Merge & Process"},
            {"type": "set", "name": "Format Output"},
            {"type": "respond_to_webhook", "name": "Return Result"}
        ],
        "connections": "complex"
    },
    "error_handler": {
        "name": "Global Error Handler",
        "description": "Catch and handle errors from any workflow with logging and notifications",
        "category": "monitoring",
        "difficulty": "intermediate",
        "tags": ["error", "monitoring", "logging", "alert"],
        "use_cases": ["Error tracking", "Failure notifications", "Debug logging", "Error recovery"],
        "keywords": ["error", "fail", "exception", "catch", "handle", "monitor", "log"],
        "estimated_time": "25 minutes",
        "nodes": [
            {"type": "error_trigger", "name": "Error Trigger"},
            {"type": "set", "name": "Extract Error Info"},
            {"type": "code", "name": "Format Error Log"},
            {"type": "http_request", "name": "Log to Service"},
            {"type": "slack", "name": "Alert Team"}
        ],
        "connections": "linear"
    },
    "api_rate_limiter": {
        "name": "API Rate Limiter & Queue",
        "description": "Queue API requests and process with rate limiting",
        "category": "api",
        "difficulty": "advanced",
        "tags": ["rate_limit", "queue", "api", "throttle"],
        "use_cases": ["Rate-limited APIs", "Bulk processing", "Request queuing", "API compliance"],
        "keywords": ["rate", "limit", "queue", "throttle", "batch", "delay", "wait"],
        "estimated_time": "40 minutes",
        "nodes": [
            {"type": "webhook", "name": "Queue Endpoint"},
            {"type": "redis", "name": "Add to Queue"},
            {"type": "schedule", "name": "Process Queue"},
            {"type": "redis", "name": "Get from Queue"},
            {"type": "wait", "name": "Rate Limit Delay"},
            {"type": "http_request", "name": "Call API"},
            {"type": "if", "name": "Check Success"},
            {"type": "redis", "name": "Update Status"}
        ],
        "connections": "complex"
    },
    "file_processor": {
        "name": "File Upload & Processing",
        "description": "Accept file uploads, process content, and store results",
        "category": "file_processing",
        "difficulty": "intermediate",
        "tags": ["file", "upload", "processing", "storage"],
        "use_cases": ["CSV processing", "Image processing", "Document parsing", "File conversion"],
        "keywords": ["file", "upload", "csv", "parse", "process", "convert", "read"],
        "estimated_time": "30 minutes",
        "nodes": [
            {"type": "webhook", "name": "File Upload"},
            {"type": "code", "name": "Parse File"},
            {"type": "function", "name": "Process Data"},
            {"type": "postgres", "name": "Store Results"},
            {"type": "respond_to_webhook", "name": "Send Response"}
        ],
        "connections": "linear"
    }
}


class TemplateRecommendationEngine:
    """AI-powered template recommendation system"""

    @staticmethod
    def calculate_relevance_score(template: Dict, description: str, workflow_goal: str = None) -> float:
        """Calculate relevance score between template and user requirements

        Args:
            template: Template data with keywords, tags, use_cases
            description: User's workflow description
            workflow_goal: Optional specific goal/objective

        Returns:
            Relevance score between 0.0 and 1.0
        """
        description_lower = description.lower()
        goal_lower = workflow_goal.lower() if workflow_goal else ""
        combined_input = f"{description_lower} {goal_lower}"

        score = 0.0
        max_score = 0.0

        # Keyword matching (weight: 40%)
        keywords = template.get('keywords', [])
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw.lower() in combined_input)
            keyword_score = keyword_matches / len(keywords)
            score += keyword_score * 0.4
        max_score += 0.4

        # Tag matching (weight: 20%)
        tags = template.get('tags', [])
        if tags:
            tag_matches = sum(1 for tag in tags if tag.lower() in combined_input)
            tag_score = tag_matches / len(tags)
            score += tag_score * 0.2
        max_score += 0.2

        # Use case matching (weight: 30%)
        use_cases = template.get('use_cases', [])
        if use_cases:
            use_case_matches = sum(1 for uc in use_cases if any(word in combined_input for word in uc.lower().split()))
            use_case_score = use_case_matches / len(use_cases)
            score += use_case_score * 0.3
        max_score += 0.3

        # Category affinity (weight: 10%)
        category = template.get('category', '')
        category_keywords = {
            'api': ['api', 'endpoint', 'rest', 'http', 'webhook'],
            'reporting': ['report', 'analytics', 'metrics', 'dashboard'],
            'integration': ['sync', 'integration', 'connect', 'import', 'export'],
            'communication': ['email', 'notification', 'message', 'alert'],
            'data_pipeline': ['pipeline', 'etl', 'transform', 'process'],
            'monitoring': ['monitor', 'track', 'log', 'error', 'alert'],
            'file_processing': ['file', 'upload', 'csv', 'document', 'parse']
        }

        if category in category_keywords:
            if any(kw in combined_input for kw in category_keywords[category]):
                score += 0.1
        max_score += 0.1

        # Normalize score
        return score / max_score if max_score > 0 else 0.0

    @staticmethod
    def recommend_templates(description: str, workflow_goal: str = None,
                          min_score: float = 0.3, max_results: int = 5) -> List[Dict]:
        """Recommend templates based on description and goal

        Args:
            description: User's workflow description
            workflow_goal: Optional workflow goal/objective
            min_score: Minimum relevance score (0.0-1.0)
            max_results: Maximum number of recommendations

        Returns:
            List of recommended templates with scores
        """
        recommendations = []

        for template_id, template in WORKFLOW_TEMPLATES.items():
            score = TemplateRecommendationEngine.calculate_relevance_score(
                template, description, workflow_goal
            )

            if score >= min_score:
                recommendations.append({
                    'template_id': template_id,
                    'template': template,
                    'relevance_score': score,
                    'match_percentage': int(score * 100)
                })

        # Sort by relevance score (descending)
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)

        return recommendations[:max_results]

    @staticmethod
    def find_best_template(description: str, workflow_goal: str = None) -> Optional[Dict]:
        """Find single best matching template

        Args:
            description: User's workflow description
            workflow_goal: Optional workflow goal

        Returns:
            Best matching template or None
        """
        recommendations = TemplateRecommendationEngine.recommend_templates(
            description, workflow_goal, min_score=0.2, max_results=1
        )

        return recommendations[0] if recommendations else None

    @staticmethod
    def get_templates_by_category(category: str) -> List[Dict]:
        """Get all templates in a specific category

        Args:
            category: Category name (api, reporting, integration, etc.)

        Returns:
            List of templates in category
        """
        return [
            {'template_id': tid, **template}
            for tid, template in WORKFLOW_TEMPLATES.items()
            if template.get('category') == category
        ]

    @staticmethod
    def get_templates_by_difficulty(difficulty: str) -> List[Dict]:
        """Get templates by difficulty level

        Args:
            difficulty: beginner, intermediate, or advanced

        Returns:
            List of templates at difficulty level
        """
        return [
            {'template_id': tid, **template}
            for tid, template in WORKFLOW_TEMPLATES.items()
            if template.get('difficulty') == difficulty
        ]

    @staticmethod
    def search_templates(query: str) -> List[Dict]:
        """Full-text search across all template fields

        Args:
            query: Search query

        Returns:
            Matching templates
        """
        query_lower = query.lower()
        results = []

        for template_id, template in WORKFLOW_TEMPLATES.items():
            # Search in name, description, tags, keywords, use_cases
            searchable_text = " ".join([
                template.get('name', ''),
                template.get('description', ''),
                " ".join(template.get('tags', [])),
                " ".join(template.get('keywords', [])),
                " ".join(template.get('use_cases', []))
            ]).lower()

            if query_lower in searchable_text:
                results.append({
                    'template_id': template_id,
                    **template
                })

        return results

    @staticmethod
    def generate_template_report() -> str:
        """Generate comprehensive template library report

        Returns:
            Formatted markdown report
        """
        report = "# 📚 Template Library Report\n\n"
        report += f"**Total Templates:** {len(WORKFLOW_TEMPLATES)}\n\n"

        # Group by category
        categories = {}
        difficulties = {'beginner': 0, 'intermediate': 0, 'advanced': 0}

        for template_id, template in WORKFLOW_TEMPLATES.items():
            cat = template.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({'id': template_id, **template})

            diff = template.get('difficulty', 'intermediate')
            difficulties[diff] = difficulties.get(diff, 0) + 1

        # Category breakdown
        report += "## Categories:\n\n"
        for category, templates in sorted(categories.items()):
            report += f"- **{category.replace('_', ' ').title()}**: {len(templates)} templates\n"

        # Difficulty breakdown
        report += "\n## Difficulty Distribution:\n\n"
        for diff, count in sorted(difficulties.items()):
            report += f"- **{diff.title()}**: {count} templates\n"

        # List all templates
        report += "\n## All Templates:\n\n"
        for template_id, template in sorted(WORKFLOW_TEMPLATES.items()):
            report += f"### {template['name']}\n"
            report += f"- **ID**: `{template_id}`\n"
            report += f"- **Category**: {template.get('category', 'N/A')}\n"
            report += f"- **Difficulty**: {template.get('difficulty', 'N/A')}\n"
            report += f"- **Estimated Time**: {template.get('estimated_time', 'N/A')}\n"
            report += f"- **Description**: {template.get('description', 'N/A')}\n"
            report += f"- **Use Cases**: {', '.join(template.get('use_cases', []))}\n"
            report += f"- **Tags**: {', '.join(template.get('tags', []))}\n\n"

        return report
