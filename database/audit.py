# database/audit.py
import json
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from database.models import AuditLog, AuditAction

# Tables we never want to audit (avoid infinite recursion on audit_logs itself)
EXCLUDED_TABLES = {"audit_logs"}


def _serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if hasattr(value, "value"): 
        return value.value
    return value


def _row_id(obj):
    pk = inspect(obj.__class__).primary_key
    insp = inspect(obj)
    values = [getattr(obj, col.name) for col in pk]
    return "-".join(str(v) for v in values) if len(values) > 1 else str(values[0])


@event.listens_for(Session, "before_flush")
def audit_before_flush(session, flush_context, instances):
    """Capture pending audit rows on session.new/dirty/deleted and stage
    them into the same flush/transaction so logging is atomic with the
    actual change (all-or-nothing commit)."""
    pending = []

    for obj in list(session.new):
        if obj.__tablename__ in EXCLUDED_TABLES:
            continue
        new_vals = {
            c.name: _serialize(getattr(obj, c.name))
            for c in obj.__table__.columns
        }
        pending.append((obj, AuditAction.INSERT, None, new_vals))

    for obj in list(session.dirty):
        if obj.__tablename__ in EXCLUDED_TABLES:
            continue
        if not session.is_modified(obj, include_collections=False):
            continue
        state = inspect(obj)
        old_vals, new_vals = {}, {}
        for attr in state.attrs:
            hist = attr.load_history()
            if hist.has_changes():
                old_vals[attr.key] = _serialize(hist.deleted[0] if hist.deleted else None)
                new_vals[attr.key] = _serialize(hist.added[0] if hist.added else None)
        if old_vals or new_vals:
            pending.append((obj, AuditAction.UPDATE, old_vals, new_vals))

    for obj in list(session.deleted):
        if obj.__tablename__ in EXCLUDED_TABLES:
            continue
        old_vals = {
            c.name: _serialize(getattr(obj, c.name))
            for c in obj.__table__.columns
        }
        pending.append((obj, AuditAction.DELETE, old_vals, None))

    for obj, action, old_vals, new_vals in pending:
        log = AuditLog(
            table_name=obj.__tablename__,
            row_id=_row_id(obj) if action != AuditAction.INSERT else "PENDING",
            action=action,
            old_values=old_vals,
            new_values=new_vals,
            timestamp=datetime.now(timezone.utc),
        )
        session.add(log)
        # For INSERTs the PK doesn't exist yet at before_flush time;
        # patch it in after_flush once the object has an id.
        if action == AuditAction.INSERT:
            session.info.setdefault("_pending_insert_logs", []).append((log, obj))


@event.listens_for(Session, "after_flush")
def audit_after_flush(session, flush_context):
    """Backfill row_id for INSERT logs now that autoincrement PKs exist."""
    pending = session.info.pop("_pending_insert_logs", [])
    for log, obj in pending:
        log.row_id = _row_id(obj)