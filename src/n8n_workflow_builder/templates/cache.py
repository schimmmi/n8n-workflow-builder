"""
Template Cache System

SQLite-based cache for template metadata to reduce API calls
and enable fast offline searches.
"""
import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("n8n-workflow-builder")


class TemplateCache:
    """
    SQLite-based template cache with automatic sync
    """

    def __init__(self, cache_path: Optional[str] = None):
        """
        Initialize template cache

        Args:
            cache_path: Path to SQLite database (defaults to ~/.n8n_workflow_builder/template_cache.db)
        """
        if cache_path is None:
            home = Path.home()
            cache_dir = home / ".n8n_workflow_builder"
            cache_dir.mkdir(exist_ok=True)
            cache_path = cache_dir / "template_cache.db"

        self.cache_path = str(cache_path)
        self.conn = sqlite3.connect(self.cache_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Main templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                author TEXT,
                author_username TEXT,
                author_verified INTEGER DEFAULT 0,
                workflow_json TEXT,
                metadata_json TEXT,
                intent_json TEXT,
                total_views INTEGER DEFAULT 0,
                source_url TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                last_synced TIMESTAMP,
                sync_enabled INTEGER DEFAULT 1
            )
        """)

        # Template tags (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_tags (
                template_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates(id),
                PRIMARY KEY (template_id, tag)
            )
        """)

        # Template nodes (which nodes used in template)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_nodes (
                template_id TEXT NOT NULL,
                node_type TEXT NOT NULL,
                node_name TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates(id),
                PRIMARY KEY (template_id, node_type, node_name)
            )
        """)

        # Sync status tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_status (
                source TEXT PRIMARY KEY,
                last_sync TIMESTAMP,
                template_count INTEGER DEFAULT 0,
                success INTEGER DEFAULT 1,
                error_message TEXT
            )
        """)

        # Search index for full-text search (independent FTS table)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS templates_fts USING fts5(
                id UNINDEXED,
                name,
                description,
                category,
                author,
                tags
            )
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_source ON templates(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_views ON templates(total_views DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_updated ON templates(updated_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_tags ON template_tags(tag)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_template_nodes ON template_nodes(node_type)")

        self.conn.commit()

    def add_template(self, template_data: Dict) -> bool:
        """
        Add or update template in cache

        Args:
            template_data: Template metadata dictionary

        Returns:
            True if successful
        """
        try:
            cursor = self.conn.cursor()

            # Extract basic fields
            template_id = template_data.get("id", template_data.get("template_id"))
            source = template_data.get("source", "unknown")
            name = template_data.get("name", "Unknown")
            description = template_data.get("description", "")
            category = template_data.get("category", "other")

            logger.info(f"Adding template to cache: {template_id} (source: {source}, name: {name})")

            # Author info
            author_info = template_data.get("user", {}) or template_data.get("author", {})
            if isinstance(author_info, str):
                author = author_info
                author_username = None
                author_verified = False
            else:
                author = author_info.get("name", "Unknown")
                author_username = author_info.get("username")
                author_verified = author_info.get("verified", False)

            # Metadata
            total_views = template_data.get("totalViews", 0) or template_data.get("total_views", 0)
            source_url = template_data.get("source_url", "")

            # JSON fields
            workflow_json = json.dumps(template_data.get("nodes", []))
            metadata_json = json.dumps(template_data.get("metadata", {}))
            intent_json = json.dumps(template_data.get("intent", {}))

            # Timestamps
            created_at = template_data.get("createdAt") or template_data.get("created_at")
            updated_at = datetime.now().isoformat()
            last_synced = datetime.now().isoformat()

            # Insert or replace template
            cursor.execute("""
                INSERT OR REPLACE INTO templates (
                    id, source, name, description, category,
                    author, author_username, author_verified,
                    workflow_json, metadata_json, intent_json,
                    total_views, source_url,
                    created_at, updated_at, last_synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_id, source, name, description, category,
                author, author_username, int(author_verified),
                workflow_json, metadata_json, intent_json,
                total_views, source_url,
                created_at, updated_at, last_synced
            ))

            # Add tags
            tags = template_data.get("tags", [])
            if tags:
                # Clear existing tags
                cursor.execute("DELETE FROM template_tags WHERE template_id = ?", (template_id,))

                # Insert new tags
                for tag in tags:
                    if isinstance(tag, dict):
                        tag = tag.get("name", "")
                    if tag:
                        cursor.execute("""
                            INSERT OR IGNORE INTO template_tags (template_id, tag)
                            VALUES (?, ?)
                        """, (template_id, tag.lower()))

            # Add nodes
            nodes = template_data.get("nodes", [])
            if nodes:
                # Clear existing nodes
                cursor.execute("DELETE FROM template_nodes WHERE template_id = ?", (template_id,))

                # Insert new nodes
                for node in nodes:
                    if isinstance(node, dict):
                        node_type = node.get("type", "")
                        node_name = node.get("name", "")
                        if node_type and node_name:
                            cursor.execute("""
                                INSERT OR IGNORE INTO template_nodes (template_id, node_type, node_name)
                                VALUES (?, ?, ?)
                            """, (template_id, node_type, node_name))

            # Update FTS index
            # Ensure tags are strings before joining
            tags_list = []
            for tag in tags:
                if isinstance(tag, dict):
                    tags_list.append(tag.get("name", ""))
                else:
                    tags_list.append(str(tag))
            tags_str = " ".join(tags_list) if tags_list else ""

            logger.info(f"🔵 [CACHE] About to INSERT into FTS5 for: {template_id}")
            logger.info(f"   FTS values: name='{name}', category='{category}', author='{author}', tags='{tags_str}'")

            # CRITICAL FIX: FTS5 doesn't properly handle INSERT OR REPLACE for duplicates
            # We must explicitly DELETE first to avoid duplicate entries
            cursor.execute("DELETE FROM templates_fts WHERE id = ?", (template_id,))

            cursor.execute("""
                INSERT INTO templates_fts (id, name, description, category, author, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (template_id, name, description, category, author, tags_str))

            logger.info(f"   FTS5 INSERT executed successfully")

            # Verify FTS5 entry was created
            cursor.execute("SELECT COUNT(*) FROM templates_fts WHERE id = ?", (template_id,))
            fts_count = cursor.fetchone()[0]
            logger.info(f"   FTS5 verification: {fts_count} entries with id={template_id}")

            self.conn.commit()
            logger.info(f"✅ Template cached successfully: {template_id} (FTS indexed: name='{name}', tags='{tags_str}')")
            return True

        except Exception as e:
            logger.error(f"Failed to add template {template_id}: {e}")
            self.conn.rollback()
            return False

    def get_template(self, template_id: str) -> Optional[Dict]:
        """
        Get template by ID

        Args:
            template_id: Template ID

        Returns:
            Template dictionary or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def search(
        self,
        query: Optional[str] = None,
        source: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        node_types: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search templates with filters

        Args:
            query: Search query (full-text)
            source: Filter by source
            category: Filter by category
            tags: Filter by tags (AND logic)
            node_types: Filter by node types used
            limit: Maximum results

        Returns:
            List of template dictionaries
        """
        cursor = self.conn.cursor()

        # Build query
        conditions = []
        params = []

        if query:
            # Use FTS for full-text search
            # Build FTS5 query with prefix matching for better results
            # Split query into words and add * for prefix matching
            query_words = query.strip().split()

            # Filter out very short words (< 3 chars) as FTS5 often ignores them
            # Use them in fallback search instead
            long_words = [w for w in query_words if len(w) >= 3]
            short_words = [w for w in query_words if len(w) < 3]

            if not long_words:
                # Only short words - use fallback search
                logger.info(f"FTS5 search - query has only short words: '{query}', using fallback")
                return self._fallback_search(query, source, limit)

            # Build FTS5 query with column prefixes for better matching
            # Search in name, description, tags, and category
            query_parts = []
            for word in long_words:
                # Search each word in multiple columns
                word_query = f"(name:{word}* OR description:{word}* OR tags:{word}* OR category:{word}*)"
                query_parts.append(word_query)

            # Combine with OR (match if ANY word matches)
            fts_query = " OR ".join(query_parts)

            logger.info(f"🔍 [SEARCH] FTS5 search - original: '{query}', FTS query: '{fts_query}', short words: {short_words}")

            # Check what's actually in FTS5
            cursor.execute("SELECT COUNT(*) FROM templates_fts")
            total_fts = cursor.fetchone()[0]
            logger.info(f"   FTS5 total entries: {total_fts}")

            # Check if source filter exists
            if source:
                cursor.execute("SELECT COUNT(*) FROM templates WHERE source = ?", (source,))
                source_count = cursor.fetchone()[0]
                logger.info(f"   Templates with source='{source}': {source_count}")

            try:
                cursor.execute("""
                    SELECT id FROM templates_fts
                    WHERE templates_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                """, (fts_query, limit))
                fts_ids = [row[0] for row in cursor.fetchall()]
                logger.info(f"   FTS5 found {len(fts_ids)} matches: {fts_ids[:5]}")

                if not fts_ids:
                    logger.warning(f"❌ [SEARCH] No FTS5 matches for query: '{query}'")
                    # Debug: Try to find out what's in FTS5 for GitHub templates
                    cursor.execute("""
                        SELECT id, name FROM templates_fts
                        WHERE id LIKE 'github_%'
                        LIMIT 3
                    """)
                    github_samples = cursor.fetchall()
                    logger.info(f"   FTS5 GitHub template samples: {github_samples}")
                    return []
            except Exception as e:
                logger.error(f"FTS5 query failed: {e}. Trying fallback...")
                # Fallback to simple LIKE query
                return self._fallback_search(query, source, limit)

            # Fetch full template data for matching IDs
            placeholders = ','.join('?' * len(fts_ids))
            cursor.execute(f"""
                SELECT * FROM templates
                WHERE id IN ({placeholders})
            """, fts_ids)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

        # Regular filters
        if source:
            conditions.append("source = ?")
            params.append(source)

        if category:
            conditions.append("category = ?")
            params.append(category)

        # Build base query
        sql = "SELECT DISTINCT t.* FROM templates t"
        joins = []

        # Join for tags filter
        if tags:
            for i, tag in enumerate(tags):
                alias = f"tt{i}"
                joins.append(f"JOIN template_tags {alias} ON t.id = {alias}.template_id")
                conditions.append(f"{alias}.tag = ?")
                params.append(tag.lower())

        # Join for node types filter
        if node_types:
            for i, node_type in enumerate(node_types):
                alias = f"tn{i}"
                joins.append(f"JOIN template_nodes {alias} ON t.id = {alias}.template_id")
                conditions.append(f"{alias}.node_type = ?")
                params.append(node_type)

        # Combine query
        if joins:
            sql += " " + " ".join(joins)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY total_views DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_popular_templates(self, limit: int = 20) -> List[Dict]:
        """Get most popular templates by views"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM templates
            ORDER BY total_views DESC
            LIMIT ?
        """, (limit,))
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_recent_templates(self, limit: int = 20) -> List[Dict]:
        """Get most recently added templates"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM templates
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def _fallback_search(self, query: str, source: Optional[str], limit: int) -> List[Dict]:
        """Fallback search using LIKE when FTS5 fails"""
        cursor = self.conn.cursor()
        query_pattern = f"%{query}%"

        conditions = ["(name LIKE ? OR description LIKE ?)"]
        params = [query_pattern, query_pattern]

        if source:
            conditions.append("source = ?")
            params.append(source)

        sql = f"SELECT * FROM templates WHERE {' AND '.join(conditions)} LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get templates by category"""
        return self.search(category=category, limit=limit)

    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[Dict]:
        """Get templates by tags (AND logic)"""
        return self.search(tags=tags, limit=limit)

    def get_by_nodes(self, node_types: List[str], limit: int = 50) -> List[Dict]:
        """Get templates using specific nodes"""
        return self.search(node_types=node_types, limit=limit)

    def update_sync_status(self, source: str, template_count: int, success: bool = True, error: Optional[str] = None):
        """Update sync status for a source"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sync_status (source, last_sync, template_count, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (source, datetime.now().isoformat(), template_count, int(success), error))
        self.conn.commit()

    def get_sync_status(self, source: Optional[str] = None) -> Dict:
        """Get sync status for source(s)"""
        cursor = self.conn.cursor()

        if source:
            cursor.execute("SELECT * FROM sync_status WHERE source = ?", (source,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}
        else:
            cursor.execute("SELECT * FROM sync_status")
            return {row["source"]: dict(row) for row in cursor.fetchall()}

    def should_sync(self, source: str, interval_hours: int = 24) -> bool:
        """
        Check if source should be synced

        Args:
            source: Source name
            interval_hours: Sync interval in hours

        Returns:
            True if sync needed
        """
        status = self.get_sync_status(source)
        if not status:
            return True

        last_sync_str = status.get("last_sync")
        if not last_sync_str:
            return True

        try:
            last_sync = datetime.fromisoformat(last_sync_str)
            now = datetime.now()
            return (now - last_sync) > timedelta(hours=interval_hours)
        except:
            return True

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Total templates
        cursor.execute("SELECT COUNT(*) as count FROM templates")
        stats["total_templates"] = cursor.fetchone()["count"]

        # By source
        cursor.execute("SELECT source, COUNT(*) as count FROM templates GROUP BY source")
        stats["by_source"] = {row["source"]: row["count"] for row in cursor.fetchall()}

        # By category
        cursor.execute("SELECT category, COUNT(*) as count FROM templates GROUP BY category ORDER BY count DESC LIMIT 10")
        stats["top_categories"] = {row["category"]: row["count"] for row in cursor.fetchall()}

        # Most popular tags
        cursor.execute("SELECT tag, COUNT(*) as count FROM template_tags GROUP BY tag ORDER BY count DESC LIMIT 20")
        stats["popular_tags"] = {row["tag"]: row["count"] for row in cursor.fetchall()}

        # Most used nodes
        cursor.execute("SELECT node_type, COUNT(*) as count FROM template_nodes GROUP BY node_type ORDER BY count DESC LIMIT 20")
        stats["popular_nodes"] = {row["node_type"]: row["count"] for row in cursor.fetchall()}

        # Sync status
        stats["sync_status"] = self.get_sync_status()

        return stats

    def clear_cache(self, source: Optional[str] = None):
        """
        Clear cache for all or specific source

        Args:
            source: Source name (clears all if None)
        """
        cursor = self.conn.cursor()

        if source:
            # Clear specific source
            cursor.execute("DELETE FROM templates WHERE source = ?", (source,))
            cursor.execute("DELETE FROM sync_status WHERE source = ?", (source,))
        else:
            # Clear all
            cursor.execute("DELETE FROM templates")
            cursor.execute("DELETE FROM template_tags")
            cursor.execute("DELETE FROM template_nodes")
            cursor.execute("DELETE FROM templates_fts")
            cursor.execute("DELETE FROM sync_status")

        self.conn.commit()
        logger.info(f"Cleared cache for {source or 'all sources'}")

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary"""
        data = dict(row)

        # Parse JSON fields
        if data.get("workflow_json"):
            try:
                data["nodes"] = json.loads(data["workflow_json"])
            except:
                data["nodes"] = []

        if data.get("metadata_json"):
            try:
                metadata = json.loads(data["metadata_json"])
                data["metadata"] = metadata
                # Expand metadata to top-level for easy access
                data["complexity"] = metadata.get("complexity", "intermediate")
                data["node_count"] = metadata.get("node_count", 0)
                data["estimated_setup_time"] = metadata.get("estimated_setup_time", "Unknown")
                data["trigger_type"] = metadata.get("trigger_type")
                data["has_error_handling"] = metadata.get("has_error_handling", False)
                data["has_documentation"] = metadata.get("has_documentation", False)
                data["uses_credentials"] = metadata.get("uses_credentials", False)
            except:
                data["metadata"] = {}
                # Set defaults if parsing fails
                data["complexity"] = "intermediate"
                data["node_count"] = 0
                data["estimated_setup_time"] = "Unknown"

        if data.get("intent_json"):
            try:
                data["intent"] = json.loads(data["intent_json"])
            except:
                data["intent"] = {}

        # Get tags
        cursor = self.conn.cursor()
        cursor.execute("SELECT tag FROM template_tags WHERE template_id = ?", (data["id"],))
        data["tags"] = [row["tag"] for row in cursor.fetchall()]

        # Convert boolean
        data["author_verified"] = bool(data.get("author_verified", 0))
        data["sync_enabled"] = bool(data.get("sync_enabled", 1))

        return data

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
