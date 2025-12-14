# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-14

### Added
- Initial release of n8n Workflow Builder MCP Server
- AI-powered workflow node suggestions based on natural language descriptions
- Workflow template generation for common use cases (API endpoints, scheduled reports, data sync)
- Workflow analysis for identifying issues and optimization opportunities
- Node explanation system with best practices and use cases
- Workflow error debugging with common solutions
- Complete MCP server implementation with 9 tools:
  - `suggest_workflow_nodes` - Get AI-powered node suggestions
  - `generate_workflow_template` - Generate complete workflow templates
  - `analyze_workflow` - Analyze workflows for issues
  - `list_workflows` - List all workflows with filtering
  - `get_workflow_details` - Get detailed workflow information
  - `execute_workflow` - Execute workflows manually
  - `get_executions` - View workflow execution history
  - `explain_node` - Get detailed node explanations
  - `debug_workflow_error` - Debug workflow errors
- Comprehensive knowledge base for n8n nodes covering:
  - Triggers (Webhook, Schedule, Manual)
  - Logic nodes (IF, Switch, Merge, Code)
  - Data operations (HTTP Request, Set, Function)
  - Storage (Postgres, Redis)
  - Integrations (Slack, Telegram, Gmail)
- Docker support with Dockerfile and docker-compose.yml
- Complete documentation in English:
  - README.md with setup instructions
  - QUICKSTART.md for quick 5-minute setup
  - EXAMPLES.md with practical use cases
- Python package structure with proper module organization
- Test suite for connection and workflow builder functionality
- Environment configuration with .env support
- Development tools configuration (black, ruff, pytest)

### Technical Details
- Built with Python 3.11+
- Uses MCP (Model Context Protocol) for Claude integration
- Async/await architecture with httpx for n8n API communication
- Comprehensive error handling and logging
- Support for n8n API v1

### Documentation
- Quick start guide for 5-minute setup
- 5 practical scenario examples
- Best practices and common pitfalls
- Troubleshooting guide
- Power combos for advanced usage

[1.0.0]: https://github.com/yourusername/n8n-workflow-builder/releases/tag/v1.0.0
