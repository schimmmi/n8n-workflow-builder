"""
Data Flow Tracer - Tracks data movement through workflows

Analyzes:
- Data input sources (webhooks, databases, APIs, files)
- Data transformations (filter, map, aggregate, merge)
- Data output destinations (databases, APIs, notifications, files)
- Critical data paths
- Data dependencies between nodes
"""

from typing import Dict, List, Set, Tuple, Optional
import re


class DataFlowTracer:
    """Traces data flow through workflow nodes"""

    # Node types that produce data (sources)
    DATA_SOURCES = {
        "webhook": "Webhook",
        "trigger": "Event Trigger",
        "schedule": "Scheduled Trigger",
        "httprequest": "HTTP API Call",
        "postgres": "PostgreSQL Database",
        "mysql": "MySQL Database",
        "mongodb": "MongoDB Database",
        "redis": "Redis Cache",
        "spreadsheet": "Google Sheets",
        "airtable": "Airtable",
        "file": "File System",
        "s3": "AWS S3",
        "email": "Email (IMAP)",
        "slack": "Slack",
        "github": "GitHub",
    }

    # Node types that transform data
    DATA_TRANSFORMERS = {
        "function": "Custom JavaScript",
        "code": "Python/JavaScript Code",
        "set": "Set Values",
        "merge": "Merge Data",
        "split": "Split Data",
        "aggregate": "Aggregate Data",
        "filter": "Filter Items",
        "sort": "Sort Data",
        "limit": "Limit Items",
        "rename": "Rename Fields",
        "movebinary": "Move Binary Data",
        "compression": "Compress/Decompress",
        "crypto": "Encrypt/Decrypt",
        "html": "HTML Extract/Parse",
        "xml": "XML Parse",
        "json": "JSON Parse",
    }

    # Node types that output data (sinks)
    DATA_SINKS = {
        "postgres": "PostgreSQL Database",
        "mysql": "MySQL Database",
        "mongodb": "MongoDB Database",
        "redis": "Redis Cache",
        "httprequest": "HTTP API",
        "email": "Email (SMTP)",
        "slack": "Slack Message",
        "telegram": "Telegram Message",
        "discord": "Discord Message",
        "spreadsheet": "Google Sheets",
        "airtable": "Airtable",
        "file": "File System",
        "s3": "AWS S3",
        "webhook": "Webhook Response",
    }

    @staticmethod
    def trace_data_flow(workflow: Dict) -> Dict:
        """
        Trace complete data flow through workflow

        Returns:
            {
                "input_sources": List[Dict],
                "transformations": List[Dict],
                "output_destinations": List[Dict],
                "data_paths": List[Dict],
                "critical_paths": List[Dict],
                "data_lineage": Dict
            }
        """
        nodes = workflow.get("nodes", [])
        connections = workflow.get("connections", {})

        # Identify data sources
        input_sources = DataFlowTracer._identify_data_sources(nodes)

        # Identify transformations
        transformations = DataFlowTracer._identify_transformations(nodes)

        # Identify data sinks
        output_destinations = DataFlowTracer._identify_data_sinks(nodes)

        # Build data paths
        data_paths = DataFlowTracer._build_data_paths(nodes, connections)

        # Identify critical paths (paths that go from source to sink)
        critical_paths = DataFlowTracer._identify_critical_paths(
            data_paths, input_sources, output_destinations
        )

        # Build data lineage graph
        data_lineage = DataFlowTracer._build_data_lineage(nodes, connections)

        return {
            "input_sources": input_sources,
            "transformations": transformations,
            "output_destinations": output_destinations,
            "data_paths": data_paths,
            "critical_paths": critical_paths,
            "data_lineage": data_lineage,
            "summary": DataFlowTracer._generate_summary(
                input_sources, transformations, output_destinations, critical_paths
            ),
        }

    @staticmethod
    def _identify_data_sources(nodes: List[Dict]) -> List[Dict]:
        """Identify nodes that produce/input data"""
        sources = []

        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")
            node_params = node.get("parameters", {})

            # Check if node is a data source
            source_type = None
            details = {}

            for pattern, label in DataFlowTracer.DATA_SOURCES.items():
                if pattern in node_type:
                    source_type = label
                    break

            if source_type:
                # Extract source-specific details
                if "webhook" in node_type:
                    details = {
                        "path": node_params.get("path", ""),
                        "method": node_params.get("httpMethod", "POST"),
                        "type": "external_trigger",
                    }
                elif "httprequest" in node_type:
                    details = {
                        "url": node_params.get("url", ""),
                        "method": node_params.get("method", "GET"),
                        "type": "api_call",
                    }
                elif any(db in node_type for db in ["postgres", "mysql", "mongo"]):
                    operation = node_params.get("operation", "")
                    details = {
                        "operation": operation,
                        "type": "database_read" if operation in ["find", "select", "get"] else "database",
                    }
                elif "schedule" in node_type or "cron" in node_type:
                    details = {
                        "type": "scheduled_trigger",
                    }

                sources.append({
                    "node_name": node_name,
                    "node_type": node_type,
                    "source_type": source_type,
                    "details": details,
                })

        return sources

    @staticmethod
    def _identify_transformations(nodes: List[Dict]) -> List[Dict]:
        """Identify nodes that transform data"""
        transformations = []

        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")
            node_params = node.get("parameters", {})

            # Check if node is a transformer
            transformer_type = None

            for pattern, label in DataFlowTracer.DATA_TRANSFORMERS.items():
                if pattern in node_type:
                    transformer_type = label
                    break

            if transformer_type:
                # Extract transformation details
                details = {}

                if "function" in node_type or "code" in node_type:
                    details = {
                        "type": "custom_code",
                        "language": "JavaScript" if "function" in node_type else node_params.get("language", "JavaScript"),
                    }
                elif "filter" in node_type:
                    details = {
                        "type": "filtering",
                        "conditions": node_params.get("conditions", {}),
                    }
                elif "merge" in node_type:
                    details = {
                        "type": "merging",
                        "mode": node_params.get("mode", ""),
                    }
                elif "aggregate" in node_type:
                    details = {
                        "type": "aggregation",
                        "aggregate": node_params.get("aggregate", ""),
                    }
                elif "set" in node_type:
                    details = {
                        "type": "value_setting",
                        "fields": len(node_params.get("values", {})),
                    }

                transformations.append({
                    "node_name": node_name,
                    "node_type": node_type,
                    "transformation_type": transformer_type,
                    "details": details,
                })

        return transformations

    @staticmethod
    def _identify_data_sinks(nodes: List[Dict]) -> List[Dict]:
        """Identify nodes that output/store data"""
        sinks = []

        for node in nodes:
            node_type = node.get("type", "").lower()
            node_name = node.get("name", "")
            node_params = node.get("parameters", {})

            # Check if node is a data sink
            sink_type = None
            details = {}

            for pattern, label in DataFlowTracer.DATA_SINKS.items():
                if pattern in node_type:
                    sink_type = label
                    break

            if sink_type:
                # Extract sink-specific details
                if any(db in node_type for db in ["postgres", "mysql", "mongo"]):
                    operation = node_params.get("operation", "")
                    if operation in ["insert", "update", "upsert", "delete"]:
                        details = {
                            "operation": operation,
                            "type": "database_write",
                        }
                        sinks.append({
                            "node_name": node_name,
                            "node_type": node_type,
                            "sink_type": sink_type,
                            "details": details,
                        })

                elif "httprequest" in node_type:
                    method = node_params.get("method", "GET")
                    if method in ["POST", "PUT", "PATCH", "DELETE"]:
                        details = {
                            "url": node_params.get("url", ""),
                            "method": method,
                            "type": "api_write",
                        }
                        sinks.append({
                            "node_name": node_name,
                            "node_type": node_type,
                            "sink_type": sink_type,
                            "details": details,
                        })

                elif "email" in node_type:
                    details = {
                        "type": "notification",
                        "recipient": node_params.get("toEmail", ""),
                    }
                    sinks.append({
                        "node_name": node_name,
                        "node_type": node_type,
                        "sink_type": sink_type,
                        "details": details,
                    })

                elif any(msg in node_type for msg in ["slack", "telegram", "discord"]):
                    details = {
                        "type": "notification",
                    }
                    sinks.append({
                        "node_name": node_name,
                        "node_type": node_type,
                        "sink_type": sink_type,
                        "details": details,
                    })

                elif "spreadsheet" in node_type or "airtable" in node_type:
                    details = {
                        "type": "spreadsheet_write",
                    }
                    sinks.append({
                        "node_name": node_name,
                        "node_type": node_type,
                        "sink_type": sink_type,
                        "details": details,
                    })

        return sinks

    @staticmethod
    def _build_data_paths(nodes: List[Dict], connections: Dict) -> List[Dict]:
        """Build all data paths through the workflow"""
        paths = []

        # Build adjacency list
        node_map = {node["name"]: node for node in nodes}
        adjacency = {node["name"]: [] for node in nodes}

        for source_node, outputs in connections.items():
            for output_type, output_connections in outputs.items():
                # output_connections is List[List[Dict]], need to flatten
                for connection_group in output_connections:
                    if isinstance(connection_group, list):
                        for conn in connection_group:
                            target_node = conn.get("node", "")
                            if target_node in adjacency:
                                adjacency[source_node].append({
                                    "target": target_node,
                                    "output": output_type,
                                    "input": conn.get("type", ""),
                                })
                    else:
                        # Fallback for old format (if connection_group is dict directly)
                        conn = connection_group
                        target_node = conn.get("node", "")
                        if target_node in adjacency:
                            adjacency[source_node].append({
                                "target": target_node,
                                "output": output_type,
                                "input": conn.get("type", ""),
                            })

        # Find all paths using DFS
        def dfs_paths(current: str, path: List[str], visited: Set[str]):
            if len(path) >= 2:  # At least 2 nodes make a path
                paths.append({
                    "path": path.copy(),
                    "length": len(path),
                    "nodes": [node_map.get(name, {}).get("type", "") for name in path],
                })

            for neighbor in adjacency.get(current, []):
                next_node = neighbor["target"]
                if next_node not in visited:
                    visited.add(next_node)
                    dfs_paths(next_node, path + [next_node], visited)
                    visited.remove(next_node)

        # Start DFS from each node
        for node_name in adjacency:
            dfs_paths(node_name, [node_name], {node_name})

        return paths

    @staticmethod
    def _identify_critical_paths(
        data_paths: List[Dict],
        input_sources: List[Dict],
        output_destinations: List[Dict]
    ) -> List[Dict]:
        """Identify critical paths (source -> sink)"""
        source_names = {s["node_name"] for s in input_sources}
        sink_names = {s["node_name"] for s in output_destinations}

        critical_paths = []

        for path in data_paths:
            path_nodes = path["path"]
            start_node = path_nodes[0]
            end_node = path_nodes[-1]

            # Check if path goes from source to sink
            if start_node in source_names and end_node in sink_names:
                critical_paths.append({
                    "path": path_nodes,
                    "start": start_node,
                    "end": end_node,
                    "length": len(path_nodes),
                    "criticality": "high",
                })

        return critical_paths

    @staticmethod
    def _build_data_lineage(nodes: List[Dict], connections: Dict) -> Dict:
        """Build data lineage graph showing data dependencies"""
        lineage = {
            "nodes": [],
            "edges": [],
        }

        # Add all nodes
        for node in nodes:
            lineage["nodes"].append({
                "name": node.get("name", ""),
                "type": node.get("type", ""),
                "position": node.get("position", []),
            })

        # Add all edges (connections)
        for source_node, outputs in connections.items():
            for output_type, output_connections in outputs.items():
                # output_connections is List[List[Dict]], need to flatten
                for connection_group in output_connections:
                    if isinstance(connection_group, list):
                        for conn in connection_group:
                            target_node = conn.get("node", "")
                            lineage["edges"].append({
                                "from": source_node,
                                "to": target_node,
                                "output": output_type,
                                "input": conn.get("type", ""),
                            })
                    else:
                        # Fallback for old format
                        conn = connection_group
                        target_node = conn.get("node", "")
                        lineage["edges"].append({
                            "from": source_node,
                            "to": target_node,
                            "output": output_type,
                            "input": conn.get("type", ""),
                        })

        return lineage

    @staticmethod
    def _generate_summary(
        input_sources: List[Dict],
        transformations: List[Dict],
        output_destinations: List[Dict],
        critical_paths: List[Dict]
    ) -> str:
        """Generate human-readable summary of data flow"""
        parts = []

        # Input sources summary
        if input_sources:
            source_types = [s["source_type"] for s in input_sources]
            parts.append(f"Data flows from {len(input_sources)} source(s): {', '.join(set(source_types))}")
        else:
            parts.append("No clear data sources identified")

        # Transformations summary
        if transformations:
            parts.append(f"Data passes through {len(transformations)} transformation(s)")
        else:
            parts.append("No data transformations detected")

        # Output destinations summary
        if output_destinations:
            sink_types = [s["sink_type"] for s in output_destinations]
            parts.append(f"Data is written to {len(output_destinations)} destination(s): {', '.join(set(sink_types))}")
        else:
            parts.append("No data output destinations identified")

        # Critical paths summary
        if critical_paths:
            parts.append(f"{len(critical_paths)} critical data path(s) identified")
        else:
            parts.append("No complete source-to-sink paths found")

        return ". ".join(parts) + "."
