# VYROX — setup

Foundation layer: config, database connection, first table (users),
and two health-check endpoints. Everything else builds on this.

## One-time setup

From inside the vyrox folder:

    # 1. Create the Python environment and install packages
    uv venv
    uv sync

    # 2. Create your real .env from the example
    cp .env.example .env

    # 3. Generate a real SECRET_KEY and paste it into .env
    python3 -c "import secrets; print(secrets.token_urlsafe(48))"
    # open .env, replace the SECRET_KEY value, and put your real
    # OPENAI_API_KEY in too. Save. NEVER commit .env.

    # 4. Start the Postgres database (Docker)
    docker compose up -d

    # 5. Confirm the database container is running
    docker ps        # you should see vyrox_db, status Up

## Run the app

    uv run uvicorn app.main:app --reload

Then open these in your browser:

    http://localhost:8000/health       -> {"status":"ok","app":"VYROX"}
    http://localhost:8000/health/db    -> {"status":"ok","database":"connected"}

If BOTH return ok, the entire stack works: FastAPI is serving,
and it can talk to Postgres. That is the milestone for this step.

## Stop the database when done

    docker compose down          # stops it, keeps your data
