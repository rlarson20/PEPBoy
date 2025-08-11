───────────────────────────────────────  
NEW SECTION – “Wiring the Database into the FastAPI Backend”  
───────────────────────────────────────  

The steps below fill the gap between “I have SQLAlchemy models” and “my API endpoints actually read from and write to the database.”  
Follow them once, and every new route you add will have fully-working persistence with proper connection-management, migrations, and test-isolation.

1. Decide on the run-time database  
   • Local development: continue to use the SQLite file (`sqlite:///./pep_viewer.db`).  
   • CI / Automated tests: spin up an in-memory SQLite database.  
   • Production: use PostgreSQL (Render, Railway, etc.). Store its URL in an environment variable called `DATABASE_URL`.

2. Centralise configuration  
   • Create a `config.py` that subclasses Pydantic’s `BaseSettings`. Expose at least:  
     – `DATABASE_URL` (defaults to the SQLite file when not provided)  
     – `ENV` (“dev”, “test”, “prod”)  
   • Import this settings object everywhere you need the connection string (Alembic, the FastAPI app, background jobs, etc.).

3. Build the SQLAlchemy “plumbing” once  
   • Engine – instantiate it with `settings.DATABASE_URL`.  
     – Dev/Prod: enable a small connection-pool (e.g., 5–10).  
     – Tests: use `connect_args={"check_same_thread": False}` for SQLite in-memory.  
   • Session-maker – create a `SessionLocal` factory bound to that engine.  
   • Declarative Base – import your `Base` (already defined in `orm_models.py`) so SQLAlchemy knows about every table.  
   • Dependency – write a `get_db()` generator that:  
     – yields a database session,  
     – commits if no exception, rolls back on exception,  
     – always closes the session in a `finally` block.  
   • Add the dependency to every route (or to an APIRouter) via `Depends(get_db)`.

4. Connect Alembic to those models  
   • In `alembic/env.py`, import `Base` and point `target_metadata` at `Base.metadata`.  
   • Also load `settings.DATABASE_URL` so migrations run against whichever database the environment dictates.  
   • Verify with `alembic upgrade head`; tables should appear in `pep_viewer.db`.

5. CRUD / repository layer (optional but recommended)  
   • Keep your route functions thin. Create a `repositories/` package with modules like `pep.py`, `author.py`, each exposing verbs such as `get_pep_by_number()`, `list_peps()`, `create_pep()`—all of which take a SQLAlchemy Session as their first argument.  
   • This separation makes unit testing trivial (you can pass an in-memory session) and keeps business logic out of your API layer.

6. Transaction & performance considerations  
   • For read-heavy endpoints (PEP detail, search, etc.) wrap queries in `session.execute(select(...))` to avoid N+1 issues and to leverage SQLAlchemy’s query-caching.  
   • If you adopt background jobs (APScheduler) for updates, give them their own session so they never contend with web requests.  

7. Test strategy  
   • Create an in-memory SQLite engine (`sqlite:///:memory:`) at test start-up.  
   • Use `Base.metadata.create_all()` on that engine.  
   • Use a fixture that yields a Session bound to that engine, wrapped in a SAVEPOINT so every test gets a pristine DB snapshot.

8. Production hardening (Phase 3 alignment)  
   • Switch the engine to `asyncpg` + SQLAlchemy 2.X’s async APIs if you need higher concurrency. (Same architecture, new engine + async session factory.)  
   • Enable connection pooling parameters (`pool_pre_ping`, `pool_size`, `max_overflow`) suitable for your host.  
   • Run `alembic upgrade head` automatically on container start-up (e.g., via an entrypoint script) so deployments always boot with the latest schema.

9. Sanity checklist – before writing your first endpoint  
   ☐ `.env` file committed to `.gitignore` and loaded by `python-dotenv` or `Pydantic BaseSettings`.  
   ☐ `DATABASE_URL` resolves correctly for dev, test, prod.  
   ☐ `alembic upgrade head` succeeds.  
   ☐ A simple health-check route using `session.execute("SELECT 1")` succeeds.  
   ☐ All subsequent routers include `Depends(get_db)`.

Once these steps are complete, the models you already wrote in `orm_models.py` become the single source of truth for both your API layer and your migrations, and every endpoint can interact with the database through an injected SQLAlchemy Session that is fast, safe, and environment-aware.
