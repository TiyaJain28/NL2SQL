import pathlib

from sqlalchemy import text

from app.database import admin_engine

SEED_FILE = pathlib.Path(__file__).resolve().parent.parent / "db" / "seed.sql"
ROLES_FILE = pathlib.Path(__file__).resolve().parent.parent / "db" / "roles.sql"


def _tables_exist(conn) -> bool:
    result = conn.execute(
        text(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables "
            "  WHERE table_schema = 'public' AND table_name = 'orders'"
            ")"
        )
    )
    return bool(result.scalar())


def run_seed(force: bool = False) -> dict:
    """
    Load the sample schema + data into the admin database if it isn't
    already present. Returns a status dict — never raises past this point,
    so callers (startup hook or the manual endpoint) always get a clear
    yes/no instead of a silent failure.
    """
    print(f"[seed] starting seed check (force={force})", flush=True)

    if not SEED_FILE.exists():
        msg = f"seed file not found at {SEED_FILE}"
        print(f"[seed] ERROR: {msg}", flush=True)
        return {"ran": False, "error": msg}

    try:
        with admin_engine.connect() as conn:
            already_seeded = _tables_exist(conn)

            if already_seeded and not force:
                print("[seed] tables already exist, skipping (pass force=true to re-run)", flush=True)
                return {"ran": False, "already_seeded": True}

            if already_seeded and force:
                print("[seed] force=true, dropping existing tables first", flush=True)
                conn.execute(text(
                    "DROP TABLE IF EXISTS order_items, orders, customers, products, regions CASCADE"
                ))
                conn.commit()

            print(f"[seed] loading {SEED_FILE.name}", flush=True)
            sql_text = SEED_FILE.read_text()

            with conn.begin():
                conn.exec_driver_sql(sql_text)

            print("[seed] schema + data loaded successfully", flush=True)

    except Exception as e:
        print(f"[seed] ERROR: seeding failed: {e}", flush=True)
        return {"ran": False, "error": str(e)}

    roles_result = {"attempted": False}
    if ROLES_FILE.exists():
        try:
            with admin_engine.connect() as conn:
                with conn.begin():
                    conn.exec_driver_sql(ROLES_FILE.read_text())
            print("[seed] read-only role created/verified", flush=True)
            roles_result = {"attempted": True, "ok": True}
        except Exception as e:
            print(f"[seed] WARNING: could not set up read-only role ({e}). "
                  f"This is non-fatal — point DATABASE_URL at the same user "
                  f"as ADMIN_DATABASE_URL if you don't need row-level isolation.",
                  flush=True)
            roles_result = {"attempted": True, "ok": False, "error": str(e)}

    print("[seed] completed", flush=True)
    return {"ran": True, "already_seeded": False, "readonly_role": roles_result}