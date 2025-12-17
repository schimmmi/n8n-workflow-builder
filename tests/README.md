# 🧪 Test Suite

This directory contains all test scripts for the n8n Workflow Builder MCP Server.

## 📁 Directory Structure

```
tests/
├── README.md                          # This file
├── test_final_verification.py         # Complete test suite (all features)
├── fts5/                              # FTS5 full-text search tests
│   ├── test_search_github.py          # GitHub template search tests
│   ├── test_direct_search.py          # Direct cache search tests
│   └── test_fts5_match.py             # FTS5 query matching tests
└── templates/                         # Template system tests
    ├── test_template_cache.py         # Template caching tests
    ├── test_github_templates.py       # GitHub adapter tests
    ├── test_community_import.py       # Community template import tests
    ├── test_intent_search.py          # Intent-based search tests
    └── test_github_logging.py         # GitHub import logging tests
```

## 🚀 Running Tests

### Run All Tests

```bash
# Run the comprehensive test suite
python3 tests/test_final_verification.py
```

### Run Specific Test Categories

```bash
# FTS5 search tests
python3 tests/fts5/test_search_github.py
python3 tests/fts5/test_direct_search.py
python3 tests/fts5/test_fts5_match.py

# Template system tests
python3 tests/templates/test_template_cache.py
python3 tests/templates/test_github_templates.py
python3 tests/templates/test_intent_search.py
```

## 📊 Test Categories

### 1. Final Verification Tests (`test_final_verification.py`)

Comprehensive test suite that verifies:
- ✅ No FTS5 duplicates exist
- ✅ GitHub templates are properly indexed
- ✅ Search returns correct results
- ✅ FTS5 match counts are accurate

**When to run:** After any FTS5 or template system changes

### 2. FTS5 Tests (`fts5/`)

Tests for the full-text search functionality:

- **`test_search_github.py`** - Tests GitHub template search
- **`test_direct_search.py`** - Tests direct cache API calls
- **`test_fts5_match.py`** - Tests FTS5 query patterns

**When to run:** After cache or search modifications

### 3. Template Tests (`templates/`)

Tests for the template library system:

- **`test_template_cache.py`** - Template caching and storage
- **`test_github_templates.py`** - GitHub repository imports
- **`test_community_import.py`** - Community template imports
- **`test_intent_search.py`** - Intent-based semantic search
- **`test_github_logging.py`** - Import process logging

**When to run:** After template adapter or intent matcher changes

## ✅ Test Requirements

All tests assume:
- n8n MCP server dependencies are installed
- Template cache database exists at `~/.n8n_workflow_builder/template_cache.db`
- No external API calls required (tests use local cache)

## 🐛 Debugging Failed Tests

If tests fail:

1. **Check FTS5 duplicates:**
   ```bash
   sqlite3 ~/.n8n_workflow_builder/template_cache.db \
     "SELECT id, COUNT(*) FROM templates_fts GROUP BY id HAVING COUNT(*) > 1"
   ```

2. **Rebuild FTS5 index:**
   ```bash
   python3 scripts/utils/rebuild_fts5.py
   ```

3. **Check template counts:**
   ```bash
   sqlite3 ~/.n8n_workflow_builder/template_cache.db \
     "SELECT source, COUNT(*) FROM templates GROUP BY source"
   ```

4. **Enable debug logging:**
   Set `LOG_LEVEL=DEBUG` before running tests

## 📝 Adding New Tests

When adding new tests:

1. Place in appropriate subdirectory (`fts5/` or `templates/`)
2. Follow naming convention: `test_<feature>.py`
3. Include docstring explaining what's tested
4. Add to this README under appropriate category
5. Ensure tests are idempotent (can run multiple times)

## 🔗 Related

- **Scripts:** See `scripts/` directory for utility and debug tools
- **Documentation:** See `docs/TESTING_GUIDE.md` for detailed testing guide
- **Bug Reports:** See `docs/BUG_FIX_FTS5_DUPLICATES.md` for FTS5 bug analysis
