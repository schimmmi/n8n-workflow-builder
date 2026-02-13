#!/usr/bin/env python3
"""
Node Recommender
Recommends n8n nodes based on task descriptions using keyword matching
"""
import re
from typing import List, Dict, Tuple, Optional


class NodeRecommender:
    """Recommends nodes based on task description using keyword matching"""
    
    def __init__(self, node_discovery):
        """Initialize with node discovery instance
        
        Args:
            node_discovery: NodeDiscovery instance with analyzed workflows
        """
        self.node_discovery = node_discovery
        
        # Keyword mappings for common tasks
        self.keyword_mappings = {
            # Communication
            'email': ['Gmail', 'Outlook', 'SMTP', 'SendGrid', 'Mailgun', 'Email Send', 'IMAP Email'],
            'slack': ['Slack', 'Slack Send Message'],
            'discord': ['Discord'],
            'teams': ['Microsoft Teams'],
            'sms': ['Twilio', 'SMS'],
            'notification': ['Slack', 'Discord', 'Pushover', 'Telegram'],
            
            # Database
            'database': ['Postgres', 'MySQL', 'MongoDB', 'Redis', 'Supabase'],
            'postgres': ['Postgres', 'PostgreSQL'],
            'mysql': ['MySQL'],
            'mongodb': ['MongoDB', 'Mongo DB'],
            'redis': ['Redis'],
            'sql': ['Postgres', 'MySQL', 'Microsoft SQL', 'Execute Query'],
            
            # API & HTTP
            'api': ['HTTP Request', 'Webhook'],
            'http': ['HTTP Request'],
            'webhook': ['Webhook'],
            'rest': ['HTTP Request'],
            'graphql': ['GraphQL'],
            
            # Data Processing
            'transform': ['Set', 'Code', 'Function', 'Function Item'],
            'filter': ['Filter', 'If', 'Switch'],
            'merge': ['Merge'],
            'split': ['Split Out', 'Item Lists'],
            'aggregate': ['Aggregate'],
            'sort': ['Sort'],
            'code': ['Code', 'Function', 'Function Item'],
            'javascript': ['Code', 'Function'],
            'python': ['Python'],
            
            # Spreadsheets
            'spreadsheet': ['Google Sheets', 'Microsoft Excel', 'Airtable'],
            'google sheets': ['Google Sheets'],
            'excel': ['Microsoft Excel'],
            'airtable': ['Airtable'],
            
            # Cloud Storage
            'storage': ['Google Drive', 'Dropbox', 'AWS S3', 'OneDrive'],
            'google drive': ['Google Drive'],
            'dropbox': ['Dropbox'],
            's3': ['AWS S3'],
            'file': ['Read Binary Files', 'Write Binary File'],
            
            # Scheduling & Time
            'schedule': ['Schedule Trigger', 'Cron'],
            'cron': ['Cron', 'Schedule Trigger'],
            'delay': ['Wait'],
            'wait': ['Wait'],
            'interval': ['Interval'],
            
            # Forms & Data Collection
            'form': ['Webhook', 'Typeform', 'Google Forms'],
            'typeform': ['Typeform'],
            
            # CRM
            'crm': ['HubSpot', 'Salesforce', 'Pipedrive'],
            'hubspot': ['HubSpot'],
            'salesforce': ['Salesforce'],
            
            # Project Management  
            'project': ['Trello', 'Asana', 'Jira', 'Monday'],
            'trello': ['Trello'],
            'asana': ['Asana'],
            'jira': ['Jira'],
            
            # Error Handling
            'error': ['Error Trigger', 'Stop And Error'],
            'retry': ['Error Trigger'],
            'catch': ['Error Trigger'],
            
            # Logic
            'condition': ['If', 'Switch'],
            'if': ['If'],
            'switch': ['Switch'],
            'loop': ['Loop Over Items'],
            
            # AI/ML
            'ai': ['OpenAI', 'Anthropic', 'Hugging Face'],
            'openai': ['OpenAI'],
            'gpt': ['OpenAI'],
            'claude': ['Anthropic'],
        }
        
        # Node categories for filtering
        self.node_categories = {
            'trigger': ['Trigger', 'Webhook', 'Schedule', 'Cron', 'Manual'],
            'data_transformation': ['Set', 'Code', 'Function', 'Filter', 'Merge', 'Split'],
            'logic': ['If', 'Switch', 'Loop'],
            'communication': ['Slack', 'Email', 'Discord', 'Teams'],
            'database': ['Postgres', 'MySQL', 'MongoDB', 'Redis'],
            'integration': ['HTTP Request', 'Webhook'],
        }
    
    async def recommend_for_task(self, task_description: str, top_k: int = 5) -> List[Tuple[str, float, str]]:
        """Recommend nodes for a task description
        
        Args:
            task_description: Natural language description of the task
            top_k: Number of recommendations to return
            
        Returns:
            List of (node_type, score, reason) tuples
        """
        # Get all discovered nodes
        node_types = self.node_discovery.get_all_node_types()
        
        if not node_types:
            return []
        
        # Normalize task description
        task_lower = task_description.lower()
        
        # Score each node type
        scores = {}
        reasons = {}
        
        for node_type in node_types:
            score, reason = self._score_node(node_type, task_lower)
            if score > 0:
                scores[node_type] = score
                reasons[node_type] = reason
        
        # Sort by score and return top_k
        sorted_nodes = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        
        return [(node, score, reasons[node]) for node, score in sorted_nodes]
    
    def _score_node(self, node_type: str, task_description: str) -> Tuple[float, str]:
        """Score a node type against a task description
        
        Args:
            node_type: Node type to score
            task_description: Normalized task description (lowercase)
            
        Returns:
            (score, reason) tuple
        """
        score = 0.0
        reasons = []
        
        # 1. Direct node name match (highest score)
        node_name_normalized = node_type.lower().replace('n8n-nodes-base.', '')
        if node_name_normalized in task_description:
            score += 10.0
            reasons.append(f"Direct match: '{node_type}' found in description")
        
        # 2. Keyword mapping match
        for keyword, node_list in self.keyword_mappings.items():
            if keyword in task_description:
                for node_name in node_list:
                    if node_name.lower() in node_name_normalized or node_name_normalized in node_name.lower():
                        score += 5.0
                        reasons.append(f"Keyword '{keyword}' maps to this node")
                        break
        
        # 3. Partial word match
        task_words = set(re.findall(r'\b\w+\b', task_description))
        node_words = set(re.findall(r'\b\w+\b', node_name_normalized))
        
        common_words = task_words & node_words
        if common_words:
            score += len(common_words) * 2.0
            reasons.append(f"Common words: {', '.join(list(common_words)[:3])}")
        
        # 4. Usage frequency boost
        node_info = self.node_discovery.get_node_info(node_type)
        if node_info:
            usage_count = node_info.get('usage_count', 0)
            if usage_count > 0:
                # Logarithmic boost based on usage
                import math
                usage_boost = math.log(usage_count + 1) * 0.5
                score += usage_boost
                if usage_count > 5:
                    reasons.append(f"Popular choice ({usage_count} uses in your workflows)")
        
        # Combine reasons
        reason = " | ".join(reasons) if reasons else "No specific match"
        
        return score, reason
    
    def get_nodes_by_category(self, category: str) -> List[str]:
        """Get all nodes in a category
        
        Args:
            category: Category name (trigger, data_transformation, etc.)
            
        Returns:
            List of node types in that category
        """
        if category not in self.node_categories:
            return []
        
        category_keywords = self.node_categories[category]
        all_nodes = self.node_discovery.get_all_node_types()
        
        matching_nodes = []
        for node_type in all_nodes:
            node_lower = node_type.lower()
            for keyword in category_keywords:
                if keyword.lower() in node_lower:
                    matching_nodes.append(node_type)
                    break
        
        return matching_nodes
    
    def suggest_alternatives(self, node_type: str) -> List[Tuple[str, str]]:
        """Suggest alternative nodes for a given node type
        
        Args:
            node_type: Node type to find alternatives for
            
        Returns:
            List of (alternative_node, reason) tuples
        """
        alternatives = []
        
        # Get node category
        node_lower = node_type.lower()
        
        # Find similar nodes by partial match
        all_nodes = self.node_discovery.get_all_node_types()
        
        # Extract key words from node name
        node_words = set(re.findall(r'\b\w+\b', node_lower))
        
        for other_node in all_nodes:
            if other_node == node_type:
                continue
            
            other_lower = other_node.lower()
            other_words = set(re.findall(r'\b\w+\b', other_lower))
            
            # Check for word overlap
            common = node_words & other_words
            if len(common) >= 1:
                reason = f"Similar functionality ({', '.join(list(common)[:2])})"
                alternatives.append((other_node, reason))
        
        return alternatives[:5]
