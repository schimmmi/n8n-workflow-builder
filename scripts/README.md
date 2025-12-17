# 🛠️ Utility Scripts

This directory contains utility and debug scripts for the n8n Workflow Builder MCP Server.

## 📁 Directory Structure

```
scripts/
├── README.md              # This file
├── debug/                 # Debug and diagnostic tools
│   ├── debug_fts5.py      # FTS5 index inspector
│   └── inspect_fts5_tokens.py  # FTS5 tokenization debugger
└── utils/                 # Utility scripts
    ├── rebuild_fts5.py    # FTS5 index rebuild utility
    ├── add_intent_tools.py  # Add intent metadata tools
    └── intent_tools.py    # Intent system utilities
```

## 🔍 Debug Scripts

### `debug/debug_fts5.py`

Inspects the FTS5 full-text search index state.

**Usage:**
```bash
python3 scripts/debug/debug_fts5.py
```

**What it does:**
- Shows template counts in main table vs FTS5
- Detects duplicate FTS5 entries
- Displays sample templates from each source
- Identifies discrepancies between tables

**When to use:**
- After template imports to verify indexing
- When searches return unexpected results
- To diagnose FTS5 issues

### `debug/inspect_fts5_tokens.py`

Tests FTS5 tokenization and query patterns.

**Usage:**
```bash
python3 scripts/debug/inspect_fts5_tokens.py
```

**What it does:**
- Tests various FTS5 query patterns
- Shows which queries match which templates
- Demonstrates column-specific vs global queries
- Helps understand FTS5 tokenization behavior

**When to use:**
- To understand why certain searches fail
- To test new FTS5 query patterns
- To debug tokenization issues

## 🔧 Utility Scripts

### `utils/rebuild_fts5.py`

Rebuilds the FTS5 full-text search index from scratch.

**Usage:**
```bash
python3 scripts/utils/rebuild_fts5.py
```

**What it does:**
1. Clears the existing FTS5 index
2. Fetches all templates from main table
3. Rebuilds FTS5 entries one by one
4. Verifies the rebuild succeeded

**When to use:**
- ✅ **After upgrading to v1.16.1** (removes FTS5 duplicates)
- After FTS5 schema changes
- When FTS5 index becomes corrupted
- To fix search issues

**Important:** This is a **safe operation** - it only rebuilds the FTS5 index, the main template data is never touched.

### `utils/add_intent_tools.py`

Adds intent metadata tools to workflows.

**Usage:**
```bash
python3 scripts/utils/add_intent_tools.py <workflow_id>
```

**What it does:**
- Analyzes workflow nodes
- Suggests intent metadata for undocumented nodes
- Adds AI-generated intent descriptions

**When to use:**
- To document existing workflows
- To improve AI context continuity
- For workflow explainability

### `utils/intent_tools.py`

General intent system utilities.

**Usage:**
```bash
python3 scripts/utils/intent_tools.py [command]
```

**What it does:**
- Manage intent metadata
- Analyze intent coverage
- Generate intent suggestions

**When to use:**
- For batch intent operations
- To analyze intent coverage across workflows

## 🚀 Quick Reference

### Common Tasks

**Fix search issues:**
```bash
# 1. Check FTS5 state
python3 scripts/debug/debug_fts5.py

# 2. If duplicates found, rebuild
python3 scripts/utils/rebuild_fts5.py

# 3. Verify fix
python3 tests/test_final_verification.py
```

**Debug failed searches:**
```bash
# 1. Inspect query patterns
python3 scripts/debug/inspect_fts5_tokens.py

# 2. Check template indexing
python3 scripts/debug/debug_fts5.py

# 3. Test search directly
python3 tests/fts5/test_direct_search.py
```

**Migrate to v1.16.1:**
```bash
# Remove FTS5 duplicates (REQUIRED after upgrading)
python3 scripts/utils/rebuild_fts5.py
```

## 📝 Adding New Scripts

When adding new scripts:

1. **Debug scripts** → `debug/` directory
   - Diagnostic tools
   - Inspection utilities
   - Debugging helpers

2. **Utility scripts** → `utils/` directory
   - Maintenance tools
   - Data migration scripts
   - Batch operations

3. **Include:**
   - Docstring explaining purpose
   - Usage examples in `--help`
   - Entry in this README

## ⚠️ Important Notes

### Safety

All scripts in this directory are **safe to run** and will:
- ✅ Never delete template data
- ✅ Never modify workflows in n8n
- ✅ Only operate on local cache database
- ✅ Provide clear output of what they're doing

### Permissions

Scripts that modify data will:
- Show what will be changed
- Ask for confirmation (where appropriate)
- Provide rollback instructions if needed

## 🔗 Related

- **Tests:** See `tests/` directory for test scripts
- **Documentation:** See `docs/` for detailed guides
- **Bug Reports:** See `docs/BUG_FIX_FTS5_DUPLICATES.md` for FTS5 issue details
