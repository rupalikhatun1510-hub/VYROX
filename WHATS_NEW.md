# VYROX — onboarding steps 5 & 6

Adds the last two onboarding screens.

## New
    step5  Face photo upload + AI grooming analysis (GPT-4o vision)
    step6  Daily habits (sleep, water, routine, stress)
    done   Summary page showing everything collected

## The AI in step 5
When you upload a photo, the app:
  1. resizes it to <=1024px and STRIPS EXIF (removes GPS location)
  2. sends the front photo to GPT-4o for GROOMING analysis only
     (face shape, hair, skin - NO ratings, NO beauty scores)
  3. caches the result so it never re-runs

If OPENAI_API_KEY is empty, step 5 still works - it saves the photo and
shows a "add your key to enable AI" note instead of crashing. Put your
real key in .env to get real analysis. Cost: ~1 rupee per photo.

## IMPORTANT: table changed again
New columns were added (face_photo_path, face_analysis, sleep_hours,
water_intake, routine_type, stress_level). Drop + recreate once:

    # stop uvicorn (Ctrl+C), then:
    sudo docker exec -it vyrox_db psql -U vyrox -d vyrox -c "DROP TABLE users;"
    uv run uvicorn app.main:app --reload

## Walk it
    /  ->  step1..step6  ->  /onboarding/done  (full summary)

The photo upload works best tested on your PHONE (mkcert HTTPS) since
that's where the camera opens. On desktop it opens a file picker.

## Next
    AI plan generation (the "Building your plan" loading screen)
    Plan-ready screen
    Home dashboard
