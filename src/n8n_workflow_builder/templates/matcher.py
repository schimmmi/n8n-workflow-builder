"""Intent-based Template Matching - The Game Changer"""
from typing import List, Dict, Tuple
import re
from .sources.base import TemplateMetadata
from .intent_extractor import TemplateIntentExtractor


class TemplateMatcher:
    """
    Matches user intent to templates using semantic similarity

    NOT: "User selects template X"
    BUT: "User describes goal → MCP suggests templates"

    Example:
        User: "I want to regularly fetch data from an API and store it in Notion"

        MCP:
          1. API to Notion Sync (95% match)
             Why: Schedule trigger + HTTP request + Notion integration
          2. Database to Notion (70% match)
             Why: Similar pattern but uses database instead of API
          3. Slack to Notion (60% match)
             Why: Shares Notion integration but different source
    """

    def __init__(self, templates: List[TemplateMetadata]):
        self.templates = templates

        # Enrich templates with intent if not already done
        for template in self.templates:
            if not template.intent:
                intent_data = TemplateIntentExtractor.extract_intent(template)
                template.intent = intent_data["intent"]
                template.purpose = intent_data["purpose"]
                template.assumptions = intent_data["assumptions"]
                template.risks = intent_data["risks"]
                template.external_systems = intent_data["external_systems"]
                template.trigger_type = intent_data["trigger_type"]
                template.data_flow = intent_data["data_flow"]

    def match(self, user_query: str, top_k: int = 5) -> List[Tuple[TemplateMetadata, float, str]]:
        """
        Match user query to templates

        Args:
            user_query: Natural language description of what user wants
            top_k: Number of top matches to return

        Returns:
            List of (template, score, reason) tuples, sorted by score
        """
        scores = []

        for template in self.templates:
            score, reason = self._calculate_match_score(user_query, template)
            scores.append((template, score, reason))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]

    def _calculate_match_score(self, query: str, template: TemplateMetadata) -> Tuple[float, str]:
        """
        Calculate match score between query and template

        Returns:
            (score, reason) where score is 0.0-1.0 and reason explains the match
        """
        query_lower = query.lower()
        score = 0.0
        reasons = []
        penalties = []

        # 1. Intent/Purpose matching (40% weight)
        intent_score = self._score_text_similarity(
            query_lower,
            [template.intent or "", template.purpose or "", template.description, template.name]
        )
        score += intent_score * 0.40

        if intent_score > 0.2:
            reasons.append(f"Intent matches ({int(intent_score * 100)}%)")

        # 2. Trigger type matching (30% weight) - CRITICAL for workflow type
        trigger_score = self._score_trigger_type(query_lower, template)

        # Detect if user specified a trigger type
        user_wants_schedule = any(word in query_lower for word in ["schedule", "daily", "hourly", "cron", "periodic", "regularly", "automated", "every"])
        user_wants_webhook = any(word in query_lower for word in ["webhook", "http", "api endpoint", "trigger", "receive"])
        user_wants_manual = any(word in query_lower for word in ["manual", "on-demand", "button"])

        template_trigger = (template.trigger_type or "").lower()
        has_schedule = "schedule" in template_trigger or "cron" in template_trigger
        has_webhook = "webhook" in template_trigger or "http" in template_trigger
        has_manual = "manual" in template_trigger

        # Apply trigger matching/penalty
        if user_wants_schedule:
            if has_schedule:
                score += 0.30  # Perfect match bonus
                reasons.append(f"✅ Trigger: schedule (matches query)")
            else:
                score += 0.05  # Heavy penalty for wrong trigger
                penalties.append("⚠️ Wrong trigger (has {}, need schedule)".format(template_trigger or "none"))
        elif user_wants_webhook:
            if has_webhook:
                score += 0.30
                reasons.append(f"✅ Trigger: webhook (matches query)")
            else:
                score += 0.05
                penalties.append("⚠️ Wrong trigger (has {}, need webhook)".format(template_trigger or "none"))
        elif user_wants_manual:
            if has_manual:
                score += 0.30
                reasons.append(f"✅ Trigger: manual (matches query)")
            else:
                score += 0.05
                penalties.append("⚠️ Wrong trigger (has {}, need manual)".format(template_trigger or "none"))
        else:
            # No specific trigger mentioned - use normal scoring
            score += trigger_score * 0.30
            if trigger_score > 0.5:
                reasons.append(f"Trigger: {template.trigger_type}")

        # 3. Keyword matching (20% weight) - reduced from 25%
        keyword_score = self._score_keywords(query_lower, template)
        score += keyword_score * 0.20

        if keyword_score > 0.3:
            reasons.append(f"Keywords match ({int(keyword_score * 100)}%)")

        # 4. External systems matching (10% weight) - reduced from 25%
        systems_score = self._score_external_systems(query_lower, template)
        score += systems_score * 0.10

        if systems_score > 0.3:
            matched_systems = [s for s in template.external_systems or [] if s.lower() in query_lower]
            if matched_systems:
                reasons.append(f"Uses: {', '.join(matched_systems[:3])}")

        # Build reason string
        all_feedback = reasons + penalties
        reason_str = " | ".join(all_feedback) if all_feedback else "General match"

        return min(score, 1.0), reason_str

    def _score_text_similarity(self, query: str, texts: List[str]) -> float:
        """Score text similarity using simple word overlap"""
        query_words = set(self._tokenize(query))
        if not query_words:
            return 0.0

        max_score = 0.0

        for text in texts:
            if not text:
                continue

            text_words = set(self._tokenize(text))
            if not text_words:
                continue

            # Jaccard similarity
            intersection = query_words & text_words
            union = query_words | text_words

            if union:
                score = len(intersection) / len(union)
                max_score = max(max_score, score)

        return max_score

    def _score_keywords(self, query: str, template: TemplateMetadata) -> float:
        """Score keyword matches with synonym support"""
        # Keyword synonyms for better matching
        synonyms = {
            "ai": ["artificial intelligence", "ml", "machine learning", "llm", "gpt", "claude"],
            "notification": ["notify", "alert", "message", "send", "telegram", "slack", "email"],
            "monitoring": ["track", "watch", "observe", "sensor", "iot", "device"],
            "analysis": ["analyze", "process", "evaluate", "calculate", "compute"],
            "sync": ["synchronize", "replicate", "copy", "mirror", "backup"],
            "api": ["http", "rest", "endpoint", "webhook", "request"],
            "database": ["db", "postgres", "mysql", "sql", "storage"],
            "schedule": ["cron", "timer", "periodic", "daily", "hourly", "automated"]
        }

        # Extract important keywords
        keywords = []
        keywords.extend(template.tags or [])
        keywords.append(template.category)
        keywords.extend(template.external_systems or [])

        if template.trigger_type:
            keywords.append(template.trigger_type)

        # Count matches (including synonyms)
        matches = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Direct match
            if keyword_lower in query:
                matches += 1
                continue

            # Synonym match
            for base_word, synonym_list in synonyms.items():
                if keyword_lower in synonym_list or keyword_lower == base_word:
                    if any(syn in query for syn in synonym_list) or base_word in query:
                        matches += 0.7  # Partial credit for synonym match
                        break

        # Normalize
        if not keywords:
            return 0.0

        return min(matches / len(keywords), 1.0)

    def _score_external_systems(self, query: str, template: TemplateMetadata) -> float:
        """Score external system matches"""
        if not template.external_systems:
            return 0.0

        matches = sum(1 for system in template.external_systems if system.lower() in query)

        return min(matches / len(template.external_systems), 1.0)

    def _score_trigger_type(self, query: str, template: TemplateMetadata) -> float:
        """Score trigger type match"""
        if not template.trigger_type:
            return 0.0

        trigger_keywords = {
            "schedule": ["schedule", "regularly", "daily", "hourly", "cron", "periodic"],
            "webhook": ["webhook", "http", "api call", "trigger", "event"],
            "manual": ["manual", "on-demand", "button"]
        }

        trigger_type = template.trigger_type.lower()

        for trigger, keywords in trigger_keywords.items():
            if trigger in trigger_type:
                if any(keyword in query for keyword in keywords):
                    return 1.0

        return 0.0

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Remove special characters, convert to lowercase, split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()

        # Remove stop words
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "will", "with", "i", "want", "need", "to", "my"
        }

        return [w for w in words if w not in stop_words and len(w) > 2]

    def filter_by_complexity(
        self, templates: List[Tuple[TemplateMetadata, float, str]], complexity: str
    ) -> List[Tuple[TemplateMetadata, float, str]]:
        """Filter matches by complexity level"""
        return [
            (t, s, r) for t, s, r in templates
            if t.complexity == complexity
        ]

    def filter_by_category(
        self, templates: List[Tuple[TemplateMetadata, float, str]], category: str
    ) -> List[Tuple[TemplateMetadata, float, str]]:
        """Filter matches by category"""
        return [
            (t, s, r) for t, s, r in templates
            if t.category == category
        ]

    def explain_match(self, query: str, template: TemplateMetadata) -> str:
        """Generate detailed explanation of why template matches"""
        score, reason = self._calculate_match_score(query, template)

        explanation = f"# Match Explanation: {template.name}\n\n"
        explanation += f"**Match Score**: {score:.0%}\n"
        explanation += f"**Reason**: {reason}\n\n"

        explanation += "## Template Intent\n"
        explanation += f"- **Purpose**: {template.intent or template.purpose or 'N/A'}\n"
        explanation += f"- **Trigger**: {template.trigger_type or 'N/A'}\n"
        explanation += f"- **Data Flow**: {template.data_flow or 'N/A'}\n\n"

        if template.external_systems:
            explanation += "## External Systems\n"
            for system in template.external_systems:
                explanation += f"- {system}\n"
            explanation += "\n"

        if template.assumptions:
            explanation += "## Assumptions\n"
            for assumption in template.assumptions[:3]:
                explanation += f"- {assumption}\n"
            explanation += "\n"

        if template.risks:
            explanation += "## Potential Risks\n"
            for risk in template.risks[:3]:
                explanation += f"- {risk}\n"
            explanation += "\n"

        return explanation
