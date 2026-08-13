# VYROX — onboarding steps 2-4

Adds three real onboarding screens on top of step 1.

## New screens
    step2  Goals grid (multi-select, 9 goals)
    step3  Body type + activity level
    step4  Diet type, food likes, dislikes, allergies

## IMPORTANT: the users table changed
This build adds new columns (goals, body_type, activity_level, diet_type,
food_likes, food_dislikes, allergies). Your existing table doesn't have
them, so you MUST drop and recreate it once:

    # stop uvicorn first (Ctrl+C), then:
    sudo docker exec -it vyrox_db psql -U vyrox -d vyrox -c "DROP TABLE users;"
    # then start the app again - it recreates the table with all columns:
    uv run uvicorn app.main:app --reload

(You lose any test users, which is fine - they were test data.)

## The flow now
    /  ->  step1 (name/age/body)  ->  step2 (goals)  ->  step3 (body/activity)
       ->  step4 (diet)  ->  step5 (placeholder: shows everything you saved)

Walk it in the browser. After step4 you land on a summary page listing
all the data that was saved, confirming steps 1-4 all persist.

## What's next
    step5  Face photo upload
    step6  Daily habits (sleep/water/routine/stress)
    then   AI plan generation + plan-ready screen + dashboard
