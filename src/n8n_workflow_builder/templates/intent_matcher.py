"""
Intent-Based Template Matching Engine

Provides semantic search and intent-based matching for templates,
going beyond simple keyword matching to understand user goals.
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class Intent:
    """Extracted user intent from natural language query"""

    # Primary goal
    goal: str  # e.g., "notification", "data_sync", "automation"

    # Trigger type preference
    trigger_type: Optional[str] = None  # "webhook", "schedule", "manual", "event"

    # Action types
    action_types: List[str] = None  # ["send_message", "store_data", "transform"]

    # Required services/nodes
    required_nodes: List[str] = None  # ["Slack", "GitHub", "OpenAI"]

    # Preferred services/nodes
    preferred_nodes: List[str] = None

    # Domain/category
    domain: Optional[str] = None  # "communication", "data_pipeline", "ai"

    # Complexity preference
    complexity: Optional[str] = None  # "beginner", "intermediate", "advanced"

    # Raw query
    raw_query: str = ""

    def __post_init__(self):
        if self.action_types is None:
            self.action_types = []
        if self.required_nodes is None:
            self.required_nodes = []
        if self.preferred_nodes is None:
            self.preferred_nodes = []


class IntentExtractor:
    """Extract intent from natural language queries"""

    # Goal keyword mappings
    GOAL_PATTERNS = {
        "notification": ["notify", "alert", "send message", "inform", "message", "email", "ping"],
        "data_sync": ["sync", "synchronize", "replicate", "copy data", "migrate", "transfer"],
        "automation": ["automate", "automatic", "schedule", "trigger", "run when"],
        "monitoring": ["monitor", "watch", "check", "observe", "track status"],
        "data_processing": ["process", "transform", "parse", "convert", "aggregate"],
        "integration": ["integrate", "connect", "link", "combine"],
        "reporting": ["report", "dashboard", "analytics", "metrics", "summarize"],
        "ai_processing": ["ai", "gpt", "claude", "openai", "generate", "llm", "intelligent"],
        "data_collection": ["collect", "gather", "fetch", "retrieve", "scrape"],
        "workflow": ["workflow", "pipeline", "sequence", "chain"],
    }

    # Trigger type patterns
    TRIGGER_PATTERNS = {
        "webhook": ["webhook", "http trigger", "when receive", "api call", "incoming request"],
        "schedule": ["schedule", "cron", "every", "daily", "hourly", "periodic", "regularly"],
        "manual": ["manual", "on demand", "when I run", "manually trigger"],
        "event": ["when", "on event", "after", "if"],
    }

    # Action type patterns
    ACTION_PATTERNS = {
        "send_message": ["send", "post", "message", "notify", "email"],
        "store_data": ["save", "store", "database", "persist", "write to"],
        "fetch_data": ["get", "fetch", "retrieve", "pull", "download"],
        "transform": ["transform", "convert", "parse", "format", "modify"],
        "analyze": ["analyze", "process", "calculate", "evaluate"],
        "generate": ["generate", "create", "produce", "make"],
    }

    # Node name patterns (common n8n nodes)
    NODE_PATTERNS = {
        "Slack": ["slack"],
        "GitHub": ["github"],
        "Gmail": ["gmail", "email", "google mail"],
        "HTTP Request": ["http", "api", "rest"],
        "OpenAI": ["openai", "gpt", "chatgpt"],
        "Anthropic": ["anthropic", "claude"],
        "Google Sheets": ["google sheets", "spreadsheet", "sheets"],
        "Postgres": ["postgres", "postgresql", "database"],
        "MongoDB": ["mongo", "mongodb"],
        "Webhook": ["webhook"],
        "Schedule Trigger": ["schedule", "cron"],
        "Code": ["code", "function", "javascript"],
        "Discord": ["discord"],
        "Telegram": ["telegram"],
        "Notion": ["notion"],
        "Airtable": ["airtable"],
        "Stripe": ["stripe"],
    }

    # Domain/category patterns
    DOMAIN_PATTERNS = {
        "communication": ["communication", "messaging", "chat", "email", "notification"],
        "data_pipeline": ["data", "etl", "pipeline", "database", "storage"],
        "ai": ["ai", "artificial intelligence", "machine learning", "gpt", "llm"],
        "automation": ["automation", "workflow", "automate"],
        "api": ["api", "rest", "http", "integration"],
        "monitoring": ["monitor", "alert", "health", "status"],
    }

    def extract(self, query: str) -> Intent:
        """
        Extract intent from natural language query

        Args:
            query: User's natural language description

        Returns:
            Extracted Intent object
        """
        query_lower = query.lower()

        # Extract goal (highest scoring)
        goal = self._extract_goal(query_lower)

        # Extract trigger type
        trigger_type = self._extract_trigger_type(query_lower)

        # Extract action types
        action_types = self._extract_action_types(query_lower)

        # Extract required/preferred nodes
        required_nodes, preferred_nodes = self._extract_nodes(query_lower)

        # Extract domain
        domain = self._extract_domain(query_lower)

        # Extract complexity preference
        complexity = self._extract_complexity(query_lower)

        return Intent(
            goal=goal,
            trigger_type=trigger_type,
            action_types=action_types,
            required_nodes=required_nodes,
            preferred_nodes=preferred_nodes,
            domain=domain,
            complexity=complexity,
            raw_query=query
        )

    def _extract_goal(self, query: str) -> str:
        """Extract primary goal from query"""
        scores = {}

        for goal, keywords in self.GOAL_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                scores[goal] = score

        if scores:
            return max(scores, key=scores.get)

        return "workflow"  # Default

    def _extract_trigger_type(self, query: str) -> Optional[str]:
        """Extract preferred trigger type"""
        for trigger_type, keywords in self.TRIGGER_PATTERNS.items():
            if any(keyword in query for keyword in keywords):
                return trigger_type
        return None

    def _extract_action_types(self, query: str) -> List[str]:
        """Extract action types from query"""
        actions = []

        for action, keywords in self.ACTION_PATTERNS.items():
            if any(keyword in query for keyword in keywords):
                actions.append(action)

        return actions

    def _extract_nodes(self, query: str) -> Tuple[List[str], List[str]]:
        """Extract required and preferred nodes"""
        required = []
        preferred = []

        for node_name, keywords in self.NODE_PATTERNS.items():
            for keyword in keywords:
                if keyword in query:
                    # Check if it's emphasized (required)
                    if any(prefix in query for prefix in ["must use", "need", "require", "using"]):
                        required.append(node_name)
                    else:
                        preferred.append(node_name)
                    break

        return required, preferred

    def _extract_domain(self, query: str) -> Optional[str]:
        """Extract domain/category"""
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            if any(keyword in query for keyword in keywords):
                return domain
        return None

    def _extract_complexity(self, query: str) -> Optional[str]:
        """Extract complexity preference"""
        if any(word in query for word in ["simple", "basic", "easy", "beginner"]):
            return "beginner"
        elif any(word in query for word in ["advanced", "complex", "sophisticated"]):
            return "advanced"
        elif "intermediate" in query:
            return "intermediate"
        return None


class IntentMatcher:
    """Match templates based on extracted intent"""

    def __init__(self):
        self.extractor = IntentExtractor()

    def match(
        self,
        query: str,
        templates: List[Dict],
        min_score: float = 0.3,
        limit: int = 20
    ) -> List[Tuple[Dict, float]]:
        """
        Match templates using intent-based scoring

        Args:
            query: Natural language query
            templates: List of template dictionaries
            min_score: Minimum score threshold (0.0-1.0)
            limit: Maximum results to return

        Returns:
            List of (template, score) tuples, sorted by score descending
        """
        # Extract intent from query
        intent = self.extractor.extract(query)

        # Score each template
        scored = []
        for template in templates:
            score = self._calculate_similarity(intent, template)
            if score >= min_score:
                scored.append((template, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:limit]

    def _calculate_similarity(self, intent: Intent, template: Dict) -> float:
        """
        Calculate intent similarity score between user intent and template

        Scoring breakdown:
        - Goal similarity: 30%
        - Node overlap: 25%
        - Trigger type match: 15%
        - Action type match: 15%
        - Domain match: 10%
        - Complexity match: 5%
        """
        score = 0.0

        # 1. Goal similarity (30%)
        score += self._score_goal_similarity(intent, template) * 0.30

        # 2. Node overlap (25%)
        score += self._score_node_overlap(intent, template) * 0.25

        # 3. Trigger type match (15%)
        score += self._score_trigger_match(intent, template) * 0.15

        # 4. Action type match (15%)
        score += self._score_action_match(intent, template) * 0.15

        # 5. Domain/category match (10%)
        score += self._score_domain_match(intent, template) * 0.10

        # 6. Complexity match (5%)
        score += self._score_complexity_match(intent, template) * 0.05

        return min(score, 1.0)  # Cap at 1.0

    def _score_goal_similarity(self, intent: Intent, template: Dict) -> float:
        """Score goal similarity"""
        # Check if goal appears in template name, description, or tags
        goal = intent.goal.replace("_", " ")

        name = template.get("name", "").lower()
        description = template.get("description", "").lower()
        category = template.get("category", "").lower()
        tags = [str(t).lower() for t in template.get("tags", [])]

        # Direct match in category or tags
        if goal in category or goal in tags:
            return 1.0

        # Match in name (high relevance)
        if goal in name:
            return 0.9

        # Match in description
        if goal in description:
            return 0.7

        # Partial match in tags
        goal_words = set(goal.split())
        for tag in tags:
            tag_words = set(tag.split())
            overlap = len(goal_words & tag_words)
            if overlap > 0:
                return 0.5 * (overlap / len(goal_words))

        return 0.0

    def _score_node_overlap(self, intent: Intent, template: Dict) -> float:
        """Score node overlap between intent and template"""
        template_nodes = template.get("nodes", [])

        # Extract node types from template
        template_node_types = set()
        for node in template_nodes:
            if isinstance(node, dict):
                node_type = node.get("type", "")
                # Extract node name (e.g., "n8n-nodes-base.slack" -> "Slack")
                if "." in node_type:
                    node_name = node_type.split(".")[-1]
                else:
                    node_name = node_type
                template_node_types.add(node_name.lower())

        # Check required nodes (must have all)
        required = set(n.lower() for n in intent.required_nodes)
        if required:
            if not required.issubset(template_node_types):
                return 0.0  # Missing required nodes = no match
            return 1.0  # All required nodes present

        # Check preferred nodes (bonus for matches)
        preferred = set(n.lower() for n in intent.preferred_nodes)
        if preferred:
            overlap = len(preferred & template_node_types)
            return overlap / len(preferred) if preferred else 0.0

        return 0.5  # Neutral if no node preferences

    def _score_trigger_match(self, intent: Intent, template: Dict) -> float:
        """Score trigger type match"""
        if not intent.trigger_type:
            return 0.5  # Neutral if no preference

        # Get template trigger info
        template_trigger = None
        metadata = template.get("metadata", {})

        # Check metadata first
        if isinstance(metadata, dict):
            template_trigger = metadata.get("trigger_type", "")

        # Fallback: check nodes
        if not template_trigger:
            for node in template.get("nodes", []):
                if isinstance(node, dict):
                    node_type = node.get("type", "").lower()
                    if "trigger" in node_type:
                        template_trigger = node_type
                        break

        if not template_trigger:
            return 0.3  # Template has no clear trigger

        template_trigger = str(template_trigger).lower()

        # Check for match
        if intent.trigger_type in template_trigger:
            return 1.0

        # Partial matches
        trigger_mappings = {
            "webhook": ["http", "webhook"],
            "schedule": ["cron", "schedule", "interval"],
            "event": ["trigger"],
        }

        intent_keywords = trigger_mappings.get(intent.trigger_type, [intent.trigger_type])
        if any(keyword in template_trigger for keyword in intent_keywords):
            return 0.7

        return 0.0

    def _score_action_match(self, intent: Intent, template: Dict) -> float:
        """Score action type match"""
        if not intent.action_types:
            return 0.5  # Neutral if no action preference

        # Extract actions from template nodes
        template_actions = []
        for node in template.get("nodes", []):
            if isinstance(node, dict):
                node_type = node.get("type", "").lower()
                node_name = node.get("name", "").lower()

                # Map node types to actions
                if any(t in node_type for t in ["slack", "email", "telegram", "discord"]):
                    template_actions.append("send_message")
                if any(t in node_type for t in ["database", "postgres", "mongo", "mysql"]):
                    template_actions.append("store_data")
                if any(t in node_type for t in ["http", "request", "api"]):
                    template_actions.append("fetch_data")
                if "function" in node_type or "code" in node_type:
                    template_actions.append("transform")
                if any(t in node_type for t in ["openai", "anthropic", "ai"]):
                    template_actions.append("generate")

        # Calculate overlap
        intent_actions = set(intent.action_types)
        template_actions_set = set(template_actions)

        if not template_actions_set:
            return 0.3

        overlap = len(intent_actions & template_actions_set)
        return overlap / len(intent_actions) if intent_actions else 0.5

    def _score_domain_match(self, intent: Intent, template: Dict) -> float:
        """Score domain/category match"""
        if not intent.domain:
            return 0.5  # Neutral

        template_category = template.get("category", "").lower()
        template_tags = [str(t).lower() for t in template.get("tags", [])]

        # Direct category match
        if intent.domain == template_category:
            return 1.0

        # Domain in tags
        if intent.domain in template_tags:
            return 0.8

        # Related domains
        domain_relations = {
            "communication": ["notification", "messaging", "email"],
            "data_pipeline": ["database", "etl", "data"],
            "ai": ["automation", "ai_processing"],
        }

        related = domain_relations.get(intent.domain, [])
        if template_category in related or any(r in template_tags for r in related):
            return 0.6

        return 0.0

    def _score_complexity_match(self, intent: Intent, template: Dict) -> float:
        """Score complexity match"""
        if not intent.complexity:
            return 0.5  # Neutral

        metadata = template.get("metadata", {})
        if isinstance(metadata, dict):
            template_complexity = metadata.get("complexity", "")
        else:
            # Fallback: infer from node count
            node_count = len(template.get("nodes", []))
            if node_count < 5:
                template_complexity = "beginner"
            elif node_count < 10:
                template_complexity = "intermediate"
            else:
                template_complexity = "advanced"

        if intent.complexity == template_complexity:
            return 1.0

        # Allow some flexibility (beginner can use intermediate, etc.)
        complexity_order = ["beginner", "intermediate", "advanced"]
        try:
            intent_idx = complexity_order.index(intent.complexity)
            template_idx = complexity_order.index(template_complexity)

            # Adjacent complexities get partial credit
            if abs(intent_idx - template_idx) == 1:
                return 0.5
        except ValueError:
            pass

        return 0.0

    def explain_match(self, intent: Intent, template: Dict) -> Dict[str, any]:
        """
        Explain why a template matches (or doesn't match) the intent

        Useful for debugging and showing users why templates were recommended
        """
        return {
            "template_name": template.get("name"),
            "template_id": template.get("id"),
            "total_score": self._calculate_similarity(intent, template),
            "breakdown": {
                "goal_similarity": self._score_goal_similarity(intent, template),
                "node_overlap": self._score_node_overlap(intent, template),
                "trigger_match": self._score_trigger_match(intent, template),
                "action_match": self._score_action_match(intent, template),
                "domain_match": self._score_domain_match(intent, template),
                "complexity_match": self._score_complexity_match(intent, template),
            },
            "intent": {
                "goal": intent.goal,
                "trigger_type": intent.trigger_type,
                "required_nodes": intent.required_nodes,
                "preferred_nodes": intent.preferred_nodes,
                "action_types": intent.action_types,
                "domain": intent.domain,
            }
        }
