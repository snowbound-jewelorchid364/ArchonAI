# Database Migrations Runbook

ARCHON uses Alembic for database migrations. All schema changes go through migration files — no manual SQL in production.

---

## Creating a Migration

```bash
cd apps/api

# Auto-generate migration from model changes
uv run alembic revision --autogenerate -m "add_github_app_id_to_users"

# Create empty migration (for data migrations or complex changes)
uv run alembic revision -m "backfill_subscription_plan"
```

Always review the generated file before committing:
```bash
cat apps/api/src/archon/db/migrations/versions/<timestamp>_*.py
```

Check for:
- Correct `upgrade()` and `downgrade()` functions
- No accidental table drops
- Index creation uses `CONCURRENTLY` for large tables
- Data migrations include NULL safety

---

## Running Migrations

### Local
```bash
cd apps/api
uv run alembic upgrade head
```

### Production (Railway)
Migrations run automatically on deploy via the `release_command` in `railway.toml`:
```toml
[deploy]
releaseCommand = "uv run alembic upgrade head"
```

If the migration fails, Railway automatically aborts the deployment — the previous version stays live.

---

## Safe Migration Practices

### Adding a column
```python
# SAFE — new nullable column
op.add_column('users', sa.Column('github_username', sa.Text(), nullable=True))

# SAFE — new column with server default
op.add_column('analyses', sa.Column('version', sa.Integer(), server_default='1'))

# UNSAFE — new NOT NULL column without default (blocks table)
# Don't do this on large tables
```

### Renaming a column (expand-contract pattern)
```python
# Step 1: Add new column (migration 1)
op.add_column('projects', sa.Column('repository_url', sa.Text()))

# Step 2: Backfill (migration 2)
op.execute("UPDATE projects SET repository_url = repo_url")

# Step 3: Deploy code that reads from both columns

# Step 4: Make old column nullable, drop in next release (migration 3)
op.drop_column('projects', 'repo_url')
```

### Adding an index on a large table
```python
# Use CONCURRENTLY to avoid locking the table
op.create_index(
    'idx_code_chunks_project_id',
    'code_chunks',
    ['project_id'],
    postgresql_concurrently=True
)
```

### Removing a column
```python
# Always add a downgrade path
def upgrade():
    op.drop_column('users', 'legacy_field')

def downgrade():
    op.add_column('users', sa.Column('legacy_field', sa.Text(), nullable=True))
```

---

## Rollback

### Rollback one migration
```bash
uv run alembic downgrade -1
```

### Rollback to specific revision
```bash
uv run alembic downgrade <revision_id>
```

### Check current revision
```bash
uv run alembic current
uv run alembic history --verbose
```

---

## CI Check

The CI pipeline runs this check to prevent deploying with unapplied migrations:

```bash
# scripts/check-migrations.sh
cd apps/api
uv run alembic check
# Exits non-zero if there are unapplied migration files
```

This prevents the situation where a migration file is committed but the `releaseCommand` hasn't been tested.
