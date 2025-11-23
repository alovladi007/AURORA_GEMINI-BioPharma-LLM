# Database Migrations

This directory contains Alembic database migrations for the Pharma AI Platform.

## Quick Start

```bash
# Run all pending migrations
make db-migrate

# Create a new migration (auto-generate from models)
make db-revision message="description of changes"

# Rollback the last migration
make db-downgrade

# View current migration version
make db-current

# View migration history
make db-history
```

## Migration Workflow

### 1. Making Model Changes

When you modify SQLAlchemy models in `app/models/`:

```python
# Example: Add a new field to User model
class User(Base):
    __tablename__ = "users"
    # ... existing fields ...
    phone_number = Column(String(20), nullable=True)  # New field
```

### 2. Generate Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add phone number to users"

# Or use make command
make db-revision message="add phone number to users"
```

This creates a new migration file in `alembic/versions/` with upgrade() and downgrade() functions.

### 3. Review Migration

**IMPORTANT:** Always review auto-generated migrations before applying them!

```python
# Check the generated file in alembic/versions/
# Verify that upgrade() and downgrade() are correct
```

Common issues with auto-generated migrations:
- Doesn't detect column type changes (e.g., String(50) → String(100))
- Doesn't detect table/column renames (appears as drop + create)
- Doesn't detect changes to indexes or constraints in some cases

### 4. Apply Migration

```bash
# Apply to database
alembic upgrade head

# Or use make command
make db-migrate
```

### 5. Rollback if Needed

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Or use make command
make db-downgrade
```

## Manual Migrations

For complex schema changes, create a manual migration:

```bash
# Create empty migration
alembic revision -m "complex schema change"

# Edit the generated file manually
# Add custom SQL or SQLAlchemy operations
```

Example manual migration:

```python
def upgrade() -> None:
    # Custom SQL
    op.execute("""
        UPDATE users
        SET role = 'researcher'
        WHERE role IS NULL
    """)

    # Make column non-nullable after fixing data
    op.alter_column('users', 'role', nullable=False)

def downgrade() -> None:
    op.alter_column('users', 'role', nullable=True)
```

## Migration Best Practices

### DO:
- ✅ Review all auto-generated migrations before applying
- ✅ Test migrations on development database first
- ✅ Write both upgrade() and downgrade()
- ✅ Use transactions (they're automatic with PostgreSQL)
- ✅ Add data migrations when changing schemas
- ✅ Version control all migration files
- ✅ Run migrations as part of deployment process

### DON'T:
- ❌ Edit migrations that have been deployed to production
- ❌ Delete migration files
- ❌ Skip migration versions
- ❌ Trust autogenerate blindly
- ❌ Make breaking changes without data migration
- ❌ Run migrations manually in production (use automated deployment)

## Common Migration Operations

### Add Column

```python
def upgrade() -> None:
    op.add_column('users',
        sa.Column('phone_number', sa.String(20), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

### Modify Column

```python
def upgrade() -> None:
    # Change column type
    op.alter_column('users', 'username',
        type_=sa.String(150),  # was String(100)
        existing_type=sa.String(100)
    )

    # Make column nullable
    op.alter_column('users', 'phone_number',
        nullable=True,
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column('users', 'username',
        type_=sa.String(100),
        existing_type=sa.String(150)
    )
    op.alter_column('users', 'phone_number',
        nullable=False,
        existing_nullable=True
    )
```

### Rename Column

```python
def upgrade() -> None:
    op.alter_column('users', 'full_name', new_column_name='display_name')

def downgrade() -> None:
    op.alter_column('users', 'display_name', new_column_name='full_name')
```

### Add Index

```python
def upgrade() -> None:
    op.create_index(
        'ix_users_email_username',
        'users',
        ['email', 'username']
    )

def downgrade() -> None:
    op.drop_index('ix_users_email_username', 'users')
```

### Data Migration

```python
from sqlalchemy import table, column, Integer, String

def upgrade() -> None:
    # Define minimal table for data migration
    users = table('users',
        column('id', Integer),
        column('role', String),
    )

    # Update data
    op.execute(
        users.update()
        .where(users.c.role == None)
        .values(role='researcher')
    )

def downgrade() -> None:
    # Usually not needed for data migrations
    pass
```

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
alembic current

# Check what's pending
alembic show head

# Apply pending migrations
alembic upgrade head
```

### "Can't locate revision identified by '<revision>'"

```bash
# Verify all migration files are present
ls alembic/versions/

# Check migration history
alembic history
```

### Migration Conflicts

If working in a team and migrations conflict:

```bash
# Pull latest migrations
git pull

# Check for multiple heads
alembic heads

# If multiple heads, merge them
alembic merge heads -m "merge migrations"
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] All migrations tested on staging database
- [ ] Backup database before migration
- [ ] Review migration SQL (use `--sql` flag)
- [ ] Ensure migrations are reversible
- [ ] Monitor migration duration on staging
- [ ] Plan rollback procedure

### Deployment Commands

```bash
# 1. Backup database
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
alembic upgrade head

# 3. Verify success
alembic current

# 4. If issues, rollback
alembic downgrade -1
```

### Zero-Downtime Migrations

For large tables or production systems:

1. **Phase 1**: Add new column (nullable)
2. **Deploy code**: Write to both old and new columns
3. **Phase 2**: Backfill data in batches
4. **Phase 3**: Make new column non-nullable
5. **Deploy code**: Read from new column only
6. **Phase 4**: Drop old column

## Migration File Naming

Files are named: `YYYY_MM_DD_HHMM-<revision>_<slug>.py`

Example: `2025_01_01_0000-001_initial_schema.py`

## Useful Commands

```bash
# Show current version
alembic current

# Show migration history
alembic history --verbose

# Show SQL without executing
alembic upgrade head --sql

# Stamp database to specific version (without running migrations)
alembic stamp head

# Show pending migrations
alembic upgrade head --sql > pending_migrations.sql
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
