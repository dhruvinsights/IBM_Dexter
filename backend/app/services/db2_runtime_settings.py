"""Runtime Db2 CLI connection string + factory helpers for vector stores."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.core.config import get_settings
from app.core.runtime_config import RuntimeConfig, get_runtime_config


def kb_table_prefix(rc: RuntimeConfig) -> str:
    """Configured stem for the KB vector table (see `kb_vector_table_name`)."""
    settings = get_settings()
    raw = (rc.get("db2_kb_table_prefix") or settings.db2_table_prefix or "DEXTER").strip()
    return raw or "DEXTER"


def kb_vector_table_name(rc: RuntimeConfig) -> str:
    """Unqualified KB table name (the part after ``SCHEMA.`` in ``QUALIFIED.TABLE``).

    If the configured prefix already ends with ``_KB`` (e.g. ``DEXTER_KB``), it is used
    as the full table name so we do not produce ``DEXTER_KB_KB``. Otherwise we append
    ``_KB`` (prefix ``DEXTER`` → table ``DEXTER_KB``).
    """
    stem = kb_table_prefix(rc)
    s = stem.strip()
    if not s:
        return "DEXTER_KB"
    if s.upper().endswith("_KB"):
        return s
    return f"{s}_KB"


def resolved_database_catalog() -> str:
    """Db2 database (catalog) name: ``DATABASE=`` in the CLI string, else ``DEXTER_DB2_DATABASE``."""
    settings = get_settings()
    rc = get_runtime_config()
    cli = (rc.get("db2_connection_string") or "").strip()
    if cli:
        for segment in cli.split(";"):
            segment = segment.strip()
            if segment.upper().startswith("DATABASE="):
                return segment.split("=", 1)[1].strip()
    return (settings.db2_database or "").strip() or "unknown"


def resolved_db2_schema(rc: RuntimeConfig) -> str:
    """Schema for KB tables (runtime ``db2_schema`` overrides ``DEXTER_DB2_SCHEMA``)."""
    settings = get_settings()
    override = (rc.get("db2_schema") or "").strip()
    if override:
        return override
    return (settings.db2_schema or "DEXTER").strip() or "DEXTER"


def db2_kb_storage_target(rc: RuntimeConfig) -> Dict[str, str]:
    """Resolved KB vector storage identifiers for status APIs and logging."""
    schema = resolved_db2_schema(rc)
    table = kb_vector_table_name(rc)
    return {
        "db2_database_catalog": resolved_database_catalog(),
        "db2_schema": schema,
        "db2_kb_table": table,
        "db2_kb_qualified_table": f"{schema}.{table}",
    }


def create_db2_vector_store(*, table_name: str, embedding_dimension: Optional[int] = None) -> Any:
    """Build Db2VectorStore from .env plus optional runtime CLI connection string."""
    from app.rag.db2_vector_store import Db2VectorStore  # noqa: WPS433

    settings = get_settings()
    rc = get_runtime_config()
    cli = (rc.get("db2_connection_string") or "").strip() or None
    emb = embedding_dimension if embedding_dimension is not None else settings.embedding_dimension
    kwargs: Dict[str, Any] = dict(
        database=resolved_database_catalog(),
        hostname=settings.db2_hostname,
        port=settings.db2_port,
        protocol=settings.db2_protocol,
        uid=settings.db2_uid,
        pwd=settings.db2_pwd,
        schema=resolved_db2_schema(rc),
        table_name=table_name,
        embedding_dimension=emb,
        security=settings.db2_security,
        authentication=settings.db2_authentication,
        ssl_server_certificate=settings.db2_ssl_server_certificate,
        connection_string_suffix=settings.db2_cli_connection_extra,
        use_langchain=settings.use_langchain_db2,
    )
    if cli:
        kwargs["cli_connection_string"] = cli
    return Db2VectorStore(**kwargs)


def test_db2_cli_connection(connection_string: str) -> Dict[str, Any]:
    """Connect with ibm_db and run SELECT 1 FROM SYSIBM.SYSDUMMY1 (no persistence)."""
    try:
        from app.rag.db2_vector_store import Db2VectorStore  # noqa: WPS433
    except ImportError as exc:
        return {"ok": False, "error": f"Db2 driver not available: {exc}"}

    raw = (connection_string or "").strip()
    if len(raw) < 8:
        return {"ok": False, "error": "Connection string is too short."}

    vs = Db2VectorStore(
        database="_",
        hostname="_",
        port=50000,
        protocol="TCPIP",
        uid="_",
        pwd="_",
        schema="DEXTER",
        table_name="_",
        embedding_dimension=384,
        use_langchain=False,
        cli_connection_string=raw,
    )
    ok, err = vs.verify_connectivity()
    try:
        vs._close()
    except Exception:
        pass
    return {"ok": ok, "error": err}


# Made with Bob
