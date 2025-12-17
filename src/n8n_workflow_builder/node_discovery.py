"""
Workflow-Based Node Discovery

Since n8n API doesn't expose node-types endpoints in all versions,
we learn about nodes by analyzing existing workflows.

This gives us:
- Which nodes are available (used in workflows)
- Which operations/parameters each node supports
- Common parameter patterns
- Credential requirements
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict
import json
import sqlite3
from pathlib import Path
import os


class NodeDiscovery:
    """Discovers node types and schemas from existing workflows"""

    # Category mappings for node classification
    NODE_CATEGORIES = {
        'trigger': ['trigger', 'webhook', 'schedule', 'cron', 'manual'],
        'data_source': ['sheets', 'airtable', 'database', 'postgres', 'mysql', 'mongodb', 'drive', 'dropbox', 's3'],
        'transform': ['code', 'function', 'set', 'merge', 'split', 'aggregate', 'filter', 'sort'],
        'notification': ['telegram', 'slack', 'discord', 'email', 'gmail', 'sms', 'twilio', 'matrix'],
        'http': ['http', 'webhook', 'request', 'api'],
        'logic': ['if', 'switch', 'router', 'compare', 'condition'],
        'utility': ['wait', 'sticky', 'note', 'error', 'stop'],
    }

    def __init__(self, db_path: Optional[str] = None):
        self.discovered_nodes = {}  # node_type -> NodeSchema
        self.node_usage_count = defaultdict(int)  # Track popularity
        self.node_categories = {}  # node_type -> category

        # Database for persistence
        if db_path is None:
            # Default to ~/.n8n-mcp/node_discovery.db
            home = Path.home()
            db_dir = home / ".n8n-mcp"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "node_discovery.db")

        self.db_path = db_path
        self._init_db()
        self._load_from_db()

    def analyze_workflows(self, workflows: List[Dict]) -> Dict:
        """
        Analyze multiple workflows to discover node types and patterns

        Args:
            workflows: List of workflow objects from n8n API

        Returns:
            Summary of discovered nodes
        """
        for workflow in workflows:
            self._analyze_workflow(workflow)

        # Save to database after analysis
        self._save_to_db()

        return self.get_summary()

    def _analyze_workflow(self, workflow: Dict):
        """Analyze a single workflow"""
        nodes = workflow.get('nodes', [])

        for node in nodes:
            node_type = node.get('type')
            if not node_type:
                continue

            # Track usage
            self.node_usage_count[node_type] += 1

            # Categorize node
            if node_type not in self.node_categories:
                self.node_categories[node_type] = self._categorize_node(node_type)

            # Extract schema if first time seeing this node
            if node_type not in self.discovered_nodes:
                self.discovered_nodes[node_type] = self._extract_node_schema(node)
            else:
                # Merge with existing schema (learn more parameters)
                self._merge_node_schema(node_type, node)

    def _categorize_node(self, node_type: str) -> str:
        """Categorize a node based on its type name"""
        node_type_lower = node_type.lower()

        # Check against category keywords
        for category, keywords in self.NODE_CATEGORIES.items():
            for keyword in keywords:
                if keyword in node_type_lower:
                    return category

        return 'other'

    def _extract_node_schema(self, node: Dict) -> Dict:
        """Extract schema from a node instance"""
        return {
            'type': node.get('type'),
            'name': node.get('name'),
            'typeVersion': node.get('typeVersion', 1),
            'parameters': self._extract_parameters(node),
            'credentials': self._extract_credentials(node),
            'position': node.get('position'),
            # Track all parameter keys we've seen
            'seen_parameters': set(node.get('parameters', {}).keys()),
            # Track parameter value types
            'parameter_types': self._infer_parameter_types(node.get('parameters', {})),
        }

    def _merge_node_schema(self, node_type: str, node: Dict):
        """Merge new node instance with existing schema"""
        existing = self.discovered_nodes[node_type]

        # Add new parameters we haven't seen before
        new_params = set(node.get('parameters', {}).keys())
        existing['seen_parameters'].update(new_params)

        # Update parameter types
        param_types = self._infer_parameter_types(node.get('parameters', {}))
        for key, value_type in param_types.items():
            if key not in existing['parameter_types']:
                existing['parameter_types'][key] = value_type

    def _extract_parameters(self, node: Dict) -> Dict:
        """Extract parameters from node"""
        return node.get('parameters', {})

    def _extract_credentials(self, node: Dict) -> Optional[Dict]:
        """Extract credentials info from node"""
        return node.get('credentials')

    def _infer_parameter_types(self, parameters: Dict) -> Dict:
        """Infer types of parameter values"""
        types = {}
        for key, value in parameters.items():
            if isinstance(value, bool):
                types[key] = 'boolean'
            elif isinstance(value, int):
                types[key] = 'number'
            elif isinstance(value, str):
                types[key] = 'string'
            elif isinstance(value, list):
                types[key] = 'array'
            elif isinstance(value, dict):
                types[key] = 'object'
            else:
                types[key] = 'unknown'
        return types

    def get_summary(self) -> Dict:
        """Get summary of discovered nodes"""
        return {
            'total_node_types': len(self.discovered_nodes),
            'total_usage': sum(self.node_usage_count.values()),
            'node_types': list(self.discovered_nodes.keys()),
            'most_used': sorted(
                self.node_usage_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def get_node_schema(self, node_type: str) -> Optional[Dict]:
        """Get schema for a specific node type"""
        schema = self.discovered_nodes.get(node_type)
        if not schema:
            return None

        # Convert sets to lists for JSON serialization
        result = schema.copy()
        result['seen_parameters'] = list(result['seen_parameters'])
        result['usage_count'] = self.node_usage_count[node_type]

        return result

    def search_nodes(self, query: str) -> List[Dict]:
        """Search for nodes by keyword"""
        query_lower = query.lower()
        matches = []

        for node_type, schema in self.discovered_nodes.items():
            if (query_lower in node_type.lower() or
                query_lower in schema.get('name', '').lower()):
                matches.append({
                    'type': node_type,
                    'name': schema.get('name'),
                    'usage_count': self.node_usage_count[node_type],
                    'parameters': len(schema.get('seen_parameters', [])),
                    'typeVersion': schema.get('typeVersion', 1),
                    'category': self.node_categories.get(node_type, 'other')
                })

        # Sort by usage count
        matches.sort(key=lambda x: x['usage_count'], reverse=True)

        return matches

    def get_node_examples(self, node_type: str, workflows: List[Dict]) -> List[Dict]:
        """Get example usages of a node type from workflows"""
        examples = []

        for workflow in workflows:
            for node in workflow.get('nodes', []):
                if node.get('type') == node_type:
                    examples.append({
                        'workflow_name': workflow.get('name', 'Unknown'),
                        'workflow_id': workflow.get('id'),
                        'node_name': node.get('name'),
                        'parameters': node.get('parameters', {}),
                        'credentials': node.get('credentials')
                    })

                    # Limit to 5 examples
                    if len(examples) >= 5:
                        return examples

        return examples

    def get_parameter_insights(self, node_type: str) -> Dict:
        """Get insights about parameters for a node type"""
        schema = self.discovered_nodes.get(node_type)
        if not schema:
            return {}

        return {
            'all_parameters': list(schema.get('seen_parameters', [])),
            'parameter_types': schema.get('parameter_types', {}),
            'total_variations': len(schema.get('seen_parameters', [])),
            'usage_count': self.node_usage_count[node_type]
        }

    def get_popular_nodes(self, limit: int = 20) -> List[Dict]:
        """Get most commonly used nodes"""
        popular = []

        for node_type, count in sorted(
            self.node_usage_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]:
            schema = self.discovered_nodes.get(node_type, {})
            popular.append({
                'type': node_type,
                'name': schema.get('name', node_type),
                'usage_count': count,
                'parameters': len(schema.get('seen_parameters', [])),
            })

        return popular

    def export_knowledge(self) -> Dict:
        """Export all discovered knowledge as JSON"""
        export = {
            'summary': self.get_summary(),
            'nodes': {}
        }

        for node_type, schema in self.discovered_nodes.items():
            export['nodes'][node_type] = {
                'name': schema.get('name'),
                'typeVersion': schema.get('typeVersion'),
                'usage_count': self.node_usage_count[node_type],
                'parameters': list(schema.get('seen_parameters', [])),
                'parameter_types': schema.get('parameter_types', {}),
                'credentials': schema.get('credentials')
            }

        return export

    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Discovered nodes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS discovered_nodes (
                node_type TEXT PRIMARY KEY,
                name TEXT,
                type_version INTEGER,
                usage_count INTEGER DEFAULT 0,
                parameters TEXT,
                parameter_types TEXT,
                credentials TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _load_from_db(self):
        """Load discovered nodes from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM discovered_nodes')
        rows = cursor.fetchall()

        for row in rows:
            node_type = row[0]
            self.discovered_nodes[node_type] = {
                'type': node_type,
                'name': row[1],
                'typeVersion': row[2],
                'seen_parameters': set(json.loads(row[4])) if row[4] else set(),
                'parameter_types': json.loads(row[5]) if row[5] else {},
                'credentials': json.loads(row[6]) if row[6] else None,
            }
            self.node_usage_count[node_type] = row[3]

        conn.close()

    def _save_to_db(self):
        """Save discovered nodes to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for node_type, schema in self.discovered_nodes.items():
            cursor.execute('''
                INSERT OR REPLACE INTO discovered_nodes
                (node_type, name, type_version, usage_count, parameters, parameter_types, credentials, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                node_type,
                schema.get('name'),
                schema.get('typeVersion', 1),
                self.node_usage_count[node_type],
                json.dumps(list(schema.get('seen_parameters', []))),
                json.dumps(schema.get('parameter_types', {})),
                json.dumps(schema.get('credentials'))
            ))

        conn.commit()
        conn.close()

    def save(self):
        """Manually save to database"""
        self._save_to_db()


class NodeRecommender:
    """Recommends nodes based on discovered usage patterns"""

    # Common stopwords to ignore in matching
    STOPWORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
        'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with'
    }

    # Synonym mappings for common terms
    SYNONYMS = {
        # Messaging platforms
        'slack': ['telegram', 'discord', 'mattermost', 'matrix', 'chat', 'message'],
        'telegram': ['slack', 'discord', 'chat', 'message'],
        'discord': ['slack', 'telegram', 'chat', 'message'],
        'email': ['gmail', 'mail', 'smtp', 'imap'],
        'gmail': ['email', 'mail'],

        # Data sources
        'spreadsheet': ['sheets', 'excel', 'airtable', 'table'],
        'sheets': ['spreadsheet', 'excel', 'googlesheets'],
        'excel': ['spreadsheet', 'sheets'],
        'airtable': ['spreadsheet', 'table', 'database'],
        'database': ['postgres', 'mysql', 'mongodb', 'sql', 'db'],
        'postgres': ['postgresql', 'database', 'sql', 'db'],
        'mysql': ['database', 'sql', 'db'],
        'mongodb': ['mongo', 'database', 'nosql', 'db'],

        # Actions
        'send': ['post', 'push', 'publish', 'transmit'],
        'receive': ['get', 'fetch', 'pull', 'retrieve'],
        'read': ['get', 'fetch', 'retrieve', 'load'],
        'write': ['save', 'store', 'update', 'create'],
        'update': ['modify', 'change', 'edit', 'write'],
        'delete': ['remove', 'drop', 'destroy'],

        # File storage
        'drive': ['googledrive', 'storage', 'cloud'],
        'dropbox': ['storage', 'cloud', 'files'],
        's3': ['aws', 'storage', 'cloud', 'bucket'],

        # Triggers
        'webhook': ['http', 'api', 'trigger'],
        'schedule': ['cron', 'timer', 'interval'],
        'trigger': ['webhook', 'event', 'start'],
    }

    def __init__(self, discovery: NodeDiscovery):
        self.discovery = discovery
        # Build reverse synonym map for faster lookup
        self.expanded_synonyms = self._build_synonym_map()

    def _build_synonym_map(self) -> Dict[str, List[str]]:
        """Build expanded synonym map for efficient lookup"""
        synonym_map = {}
        for word, synonyms in self.SYNONYMS.items():
            synonym_map[word] = synonyms
        return synonym_map

    def _get_expanded_keywords(self, keywords: List[str]) -> List[tuple]:
        """
        Expand keywords with synonyms
        Returns: List of (keyword, weight) tuples where weight=1.0 for original, 0.5 for synonym
        """
        expanded = []
        for keyword in keywords:
            # Original keyword gets full weight
            expanded.append((keyword, 1.0))
            # Synonyms get half weight
            if keyword in self.expanded_synonyms:
                for synonym in self.expanded_synonyms[keyword]:
                    expanded.append((synonym, 0.5))
        return expanded

    def recommend_for_task(self, task_description: str, top_k: int = 5) -> List[Dict]:
        """
        Recommend nodes for a task based on keywords

        Args:
            task_description: Natural language description of task
            top_k: Number of recommendations

        Returns:
            List of recommended nodes with scores
        """
        # Filter out stopwords and short words
        keywords = [
            word for word in task_description.lower().split()
            if word not in self.STOPWORDS and len(word) > 2
        ]

        # Expand with synonyms
        expanded_keywords = self._get_expanded_keywords(keywords)

        recommendations = []

        for node_type, schema in self.discovery.discovered_nodes.items():
            score = 0
            keyword_matches = []
            synonym_matches = []

            node_type_lower = node_type.lower()
            node_name = schema.get('name', '').lower()
            seen_parameters = schema.get('seen_parameters', [])

            # Match keywords and synonyms in node type
            for keyword, weight in expanded_keywords:
                if keyword in node_type_lower:
                    # Exact word boundary match gets more points
                    if f".{keyword}" in node_type_lower or node_type_lower.endswith(keyword):
                        match_score = 5 * weight  # Strong match with weight
                        score += match_score
                        if weight == 1.0:
                            keyword_matches.append(keyword)
                        else:
                            synonym_matches.append(keyword)
                    else:
                        match_score = 2 * weight  # Partial match with weight
                        score += match_score
                        if weight == 1.0:
                            keyword_matches.append(keyword)
                        else:
                            synonym_matches.append(keyword)

            # Match keywords in node name
            for keyword, weight in expanded_keywords:
                if keyword in node_name and keyword not in keyword_matches:
                    score += 3 * weight
                    if weight == 1.0:
                        keyword_matches.append(keyword)
                    else:
                        synonym_matches.append(keyword)

            # Match keywords in parameters (bonus for nodes with relevant parameters)
            for keyword, weight in expanded_keywords:
                for param in seen_parameters:
                    if keyword in param.lower():
                        score += 1 * weight  # Smaller boost for parameter match
                        break

            # Popularity boost (reduced - max 3 points instead of 5)
            usage = self.discovery.node_usage_count[node_type]
            popularity_score = min(usage / 50, 3.0)  # Cap at +3, slower growth

            # Only add popularity if there's at least some keyword match
            if keyword_matches or synonym_matches:
                score += popularity_score

            if score > 0:
                recommendations.append({
                    'type': node_type,
                    'name': schema.get('name'),
                    'score': score,
                    'usage_count': usage,
                    'keyword_matches': keyword_matches,
                    'synonym_matches': synonym_matches,
                    'reason': self._generate_reason(keyword_matches, synonym_matches, node_type, schema, popularity_score)
                })

        # Sort by score, then by usage count as tiebreaker
        recommendations.sort(key=lambda x: (x['score'], x['usage_count']), reverse=True)

        return recommendations[:top_k]

    def _generate_reason(self, keyword_matches: List[str], synonym_matches: List[str], node_type: str, schema: Dict, popularity_score: float) -> str:
        """Generate reason for recommendation"""
        reasons = []

        if keyword_matches:
            reasons.append(f"Matches: {', '.join(set(keyword_matches))}")

        if synonym_matches:
            reasons.append(f"Similar: {', '.join(set(synonym_matches))}")

        if popularity_score > 2.0:
            reasons.append("highly popular")
        elif popularity_score > 1.0:
            reasons.append("commonly used")

        if reasons:
            return " • ".join(reasons)

        return "Potential match"
