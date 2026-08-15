# VYROX — AI plan generation + dashboard

The big one. Onboarding now flows into a real AI-generated plan and the
home dashboard.

## New
    /onboarding/building   Animated "Building your plan" loading screen
    /plan/generate         (POST) the ONE GPT-4o call that builds the plan
    /plan/ready            Plan-ready screen (profile + plan cards)
    /dashboard             Home dashboard (progress ring, workout, meals)

## How the AI plan works
Step 6 now sends you to the building screen. That screen:
  1. animates the 6-item checklist (UX only)
  2. in the background POSTs to /plan/generate
  3. that makes ONE GPT-4o call with your whole profile and returns a
     structured plan: workout, meals, grooming, habits, insight
  4. the plan is saved, then you land on /plan/ready -> ENTER VYROX -> dashboard

Safety built in: for the 16-18 age bracket the prompt forbids calorie
deficits and restrictive dieting. No medical claims, no ratings.

No API key? It still works - you get a sensible DEFAULT plan built from
your own answers, so nothing breaks. Add your key for real AI plans.
Cost: one call per plan, roughly 1-2 rupees.

## IMPORTANT: new table added
This adds a "plans" table. The users table is unchanged, so you only
need to let the app create the new table - which it does on startup.
But if you hit any DB error, the clean reset is:

    # stop uvicorn (Ctrl+C), then:
    sudo docker exec -it vyrox_db psql -U vyrox -d vyrox -c "DROP TABLE IF EXISTS plans; DROP TABLE IF EXISTS users;"
    uv run uvicorn app.main:app --reload

## Walk it
    /  ->  step1..step6  ->  building (watch it generate)  ->  ready
       ->  ENTER VYROX  ->  dashboard

## Next
    Make dashboard cards tappable (workout player, food scanner, etc.)
    Skin Lab, Hair Lab, Body Lab, Progress, Profile
    Real signup/auth so accounts persist
    Subscription / paywall
