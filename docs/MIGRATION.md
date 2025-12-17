# 🔄 Migration Engine Documentation

The Migration Engine automatically checks and updates workflows for node compatibility when n8n APIs change.

## 🎯 Problem It Solves

**Challenge:** n8n evolves quickly - new nodes, deprecated parameters, breaking changes. Community templates and old workflows often break.

**Solution:** Automatic compatibility checking and migration with smart upgrade rules.

---

## 🚀 Quick Start

### Check Workflow Compatibility

```
"Check workflow abc123 for compatibility issues"
"Are there any deprecated nodes in my workflow?"
```

### Automatic Migration

```
"Migrate workflow abc123 to latest versions"
"Update my workflow with deprecated parameters"
```

### Preview Changes

```
"Show me what would change if I migrate workflow abc123"
"Preview migration for 'Customer API' workflow"
```

---

## 📊 Architecture

### Components

1. **Version Checker** - Detects compatibility issues
2. **Migration Engine** - Applies transformation rules
3. **Workflow Updater** - High-level interface
4. **Migration Reporter** - Generates formatted reports
5. **Migration Rules** - Predefined node upgrade rules

### Data Flow

```
Workflow → Version Checker → Compatibility Issues
                ↓
        Migration Engine → Apply Rules
                ↓
        Workflow Updater → Updated Workflow
                ↓
        Reporter → Human-Readable Report
```

---

## 🔍 Compatibility Checking

### Compatibility Statuses

- ✅ **COMPATIBLE** - No issues, ready to use
- 🟡 **DEPRECATED** - Works but has deprecated features
- 🔴 **BREAKING** - Has breaking changes, may fail
- ❓ **UNKNOWN** - Node not in compatibility database

### Issue Types

1. **deprecated_parameter** - Parameter is outdated
2. **breaking_change** - API change that breaks workflow
3. **missing_parameter** - Required parameter missing
4. **version_mismatch** - Node version outdated
5. **deprecated_node** - Entire node is deprecated

### Issue Severities

- **critical** - Must fix before deployment
- **high** - Should fix soon
- **medium** - Fix when convenient
- **low** - Nice to fix

---

## 🔄 Migration Rules

### Built-in Rules

#### HTTP Request Node

**v2 → v3:**
- Renames `url` → `requestUrl`
- Renames `method` → `requestMethod`
- Moves authentication to credentials
- Severity: HIGH

**v3 → v4:**
- Adds new authentication options
- Updates response handling
- Severity: MEDIUM

#### Postgres Node

**v1 → v2:**
- Renames `executeQuery` → `query`
- Updates parameter structure
- Severity: HIGH

#### Slack Node

**v1 → v2:**
- Updates message formatting
- New attachment structure
- Enables markdown by default
- Severity: MEDIUM

#### Function Node

**v1 → v2:**
- API changes: `$item()` → `items[0]`
- API changes: `$items()` → `items`
- Adds migration comments to code
- Severity: CRITICAL

### Custom Rules

Add your own migration rules:

```python
from migration import MigrationRule

def my_transform(node: Dict) -> Dict:
    # Your transformation logic
    return node

custom_rule = MigrationRule(
    rule_id="my_custom_migration",
    name="My Custom Migration",
    description="Migrate my custom node",
    node_type="n8n-nodes-base.myNode",
    from_version=1,
    to_version=2,
    transform=my_transform,
    severity="high"
)
```

---

## 🛠️ MCP Tools

### check_workflow_compatibility

Check workflow for compatibility issues.

**Parameters:**
- `workflow_id` (required): Workflow to check

**Returns:** Detailed compatibility report with issues grouped by severity.

**Example:**
```
"Check workflow abc123 for compatibility"
```

---

### migrate_workflow

Automatically migrate workflow to latest versions.

**Parameters:**
- `workflow_id` (required): Workflow to migrate
- `dry_run` (optional, default: false): Preview without applying
- `target_version` (optional): Target node version

**Returns:** Migration report showing applied changes.

**Example:**
```
"Migrate workflow abc123"
"Migrate workflow xyz789 with dry_run=true"
```

---

### get_migration_preview

Preview what would change without applying.

**Parameters:**
- `workflow_id` (required): Workflow to preview

**Returns:** Detailed diff of changes.

**Example:**
```
"Preview migration for workflow abc123"
```

---

### batch_check_compatibility

Check multiple workflows at once.

**Parameters:**
- `workflow_ids` (optional): Specific IDs (all if omitted)

**Returns:** Batch report with summary statistics.

**Example:**
```
"Check all workflows for compatibility"
"Check workflows abc123, def456, ghi789"
```

---

### get_available_migrations

List available migration rules for a node type.

**Parameters:**
- `node_type` (required): Node type to query

**Returns:** List of available rules with versions.

**Example:**
```
"What migrations are available for HTTP Request node?"
"Show me postgres node migrations"
```

---

## 📋 Usage Examples

### Example 1: Check Before Deployment

```
1. "Check workflow 'Production API' for compatibility"
2. Review issues
3. "Migrate workflow if safe"
4. "Preview migration first"
5. "Apply migration"
```

### Example 2: After n8n Upgrade

```
1. "Batch check all workflows for compatibility"
2. Review report - identify critical issues
3. "Migrate workflow abc123" (for each problematic workflow)
4. Test migrated workflows
```

### Example 3: Community Template

```
1. Import template from community
2. "Check workflow for compatibility"
3. See deprecated parameters
4. "Migrate workflow" (auto-fix)
5. Deploy updated template
```

### Example 4: Audit Existing Workflows

```
1. "Batch check all workflows"
2. Get summary: X compatible, Y deprecated, Z breaking
3. Prioritize by severity
4. Migrate high-priority workflows first
```

---

## ⚠️ Important Notes

### Safe Migration

- ✅ **Always preview** before migrating production workflows
- ✅ **Test migrations** in staging first
- ✅ **Backup workflows** before batch operations
- ✅ **Review changes** in migration reports

### What Gets Preserved

- ✅ Workflow structure (nodes, connections)
- ✅ Node names and IDs
- ✅ Workflow settings
- ✅ Credentials (references only)

### What May Change

- ⚠️ Node type versions
- ⚠️ Parameter names (renamed per rules)
- ⚠️ Parameter structure (updated per rules)
- ⚠️ Default values (if schema changed)

### Limitations

- ❌ **Cannot migrate** if no rule exists
- ❌ **Cannot fix** custom code logic
- ❌ **Cannot update** external integrations
- ❌ **Cannot guarantee** 100% compatibility

---

## 🔧 Technical Details

### Version Checker Algorithm

1. Load workflow JSON
2. Extract nodes and their versions
3. Check each node against compatibility database
4. Identify deprecated parameters
5. Calculate overall status
6. Generate issue list with severities

### Migration Engine Algorithm

1. Find applicable rules for node type/version
2. Build migration path (may be multi-step)
3. Apply transformations in order
4. Update node version
5. Validate result
6. Generate migration log

### Validation

After migration, validates:
- Node count unchanged
- Connections preserved
- Node names intact
- No data loss

---

## 📊 Reports

### Compatibility Report

```markdown
# Compatibility Report: My Workflow

**Status:** 🟡 DEPRECATED
**Issues Found:** 3

## 🔴 Critical Issues
- HTTP Request: Parameter 'url' deprecated since v3

## 🟡 Medium Priority Issues
- Slack: Node version 1 is outdated

## 💡 Recommendations
✅ Auto-migration available
Run: migrate_workflow(workflow_id)
```

### Migration Report

```markdown
# Migration Report: My Workflow

**Timestamp:** 2025-12-17 10:00:00
**Migrations Applied:** 2

## Status Comparison
| Metric | Before | After |
|--------|--------|-------|
| Status | deprecated | compatible |
| Issues | 3 | 0 |

## Applied Migrations
### HTTP Request
- HTTP Request v2 → v3
- Parameters renamed: url → requestUrl

✅ Success: All issues resolved!
```

---

## 🚀 Best Practices

1. **Regular Audits:** Check compatibility monthly
2. **Before Upgrades:** Test migrations before n8n upgrades
3. **Preview First:** Always preview production migrations
4. **Test Thoroughly:** Test migrated workflows in staging
5. **Document Changes:** Keep migration logs for audit
6. **Monitor Performance:** Watch for issues after migration

---

## 🔗 Related Documentation

- **[Tools Reference](TOOLS.md)** - Complete MCP tools list
- **[Examples](../examples/PROMPTS.md)** - Migration prompt examples
- **[Validation](VALIDATION.md)** - Pre-deployment checks

---

**Questions?** Ask Claude for help with migrations! 🎉
