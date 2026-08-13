# VYROX — pages update

This build adds the first three real screens on top of the foundation.

## New files

    app/static/css/vyrox.css          the whole design system (colors, glass, buttons)
    app/templates/base.html           shared page shell
    app/templates/_logo.html          the V logo (inline SVG, no image needed)
    app/templates/splash.html         GET STARTED / LOG IN screen
    app/templates/login.html          email + password login
    app/templates/onboarding/step1.html  name, age, height, weight
    app/templates_engine.py           shared Jinja2 setup
    app/routers/pages.py              serves splash + login
    app/routers/onboarding.py         serves step 1, saves it to the database

## Changed files

    app/main.py        now wires the routers + session cookies
    app/models/user.py now has name / age_bracket / height_cm / weight_kg

## How to run (same as before)

    cd ~/vyrox
    docker compose up -d              # start Postgres
    uv sync                          # (only if packages changed - they didn't)
    uv run uvicorn app.main:app --reload

Then open in your browser:

    http://localhost:8000/                  splash screen
    http://localhost:8000/login             login page
    http://localhost:8000/onboarding/step1  onboarding step 1

Fill in step 1 and press NEXT. You'll land on a "Saved, <name> ✓" page.
That confirms the data went into Postgres.

## What works

- Tap a screen's buttons to move between them.
- Age pills select on tap (13-15 removed on purpose; floor is 16).
- Step 1 form saves name/age/height/weight to the users table.
- The session cookie remembers you into the next step.

## What's next

- Step 3 (goals grid) is currently a placeholder confirmation page.
- Steps 2, 4-12, the dashboard, and AI plan generation come next.

## Note on Starlette

This build uses the new TemplateResponse(request, "file.html", context)
signature required by the Starlette version installed. The old
TemplateResponse("file.html", {"request": request}) form is removed
because it errors on this version.
