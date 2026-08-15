"""
Plan generation service.

ONE GPT-4o call takes everything from onboarding and returns a single
structured JSON plan: workout, meals, grooming, habits, and one insight.

Why one call, not six: it's cheaper, faster, and the sections stay
consistent with each other. The "AI is analyzing / creating / designing"
checklist on the loading screen is a UX animation, not six real calls.

Safety rules baked into the prompt (from the product spec):
  - For the 16-18 age bracket: NO aggressive calorie deficits, NO
    restrictive dieting. Focus on balanced nutrition, strength, habits.
  - No medical claims, no guaranteed outcomes.

If there's no API key or the call fails, we return a sensible default
plan built from the user's own answers, so the app always works.
"""

import json

from app.config import settings


def _default_plan(user) -> dict:
    """
    A reasonable non-AI plan built directly from the user's answers.
    Used when the AI is unavailable so onboarding always finishes.
    """
    goals = user.goals or []
    veg = user.diet_type == "veg"
    protein = "paneer, dal, tofu, eggs" if not veg else "paneer, dal, tofu, chickpeas"

    return {
        "generated_by": "default",
        "workout": {
            "title": "Full Body Starter",
            "days_per_week": 3,
            "focus": "Strength + movement",
            "exercises": [
                {"name": "Bodyweight Squats", "sets": "3 × 12"},
                {"name": "Push Ups", "sets": "3 × 10"},
                {"name": "Plank", "sets": "3 × 30s"},
                {"name": "Glute Bridge", "sets": "3 × 15"},
            ],
        },
        "meals": {
            "note": "Balanced meals with enough protein.",
            "breakfast": "Oats with fruit and milk",
            "lunch": f"Rice, vegetables and {protein}",
            "dinner": f"Roti, salad and {protein}",
        },
        "grooming": {
            "haircut": "A clean, low-maintenance cut suited to your hair.",
            "skincare": "Cleanse morning and night, moisturize, sunscreen by day.",
        },
        "habits": [
            "Drink water regularly through the day",
            "Aim for 7-8 hours of sleep",
            "Move for at least 20 minutes daily",
            "Eat protein with every meal",
        ],
        "insight": "Your plan is built from your goals: " + (", ".join(goals) or "general wellness") + ".",
    }


def generate_plan(user) -> dict:
    """
    Call GPT-4o once to build a personalized plan. Never raises - returns
    the default plan on any failure.
    """
    if not settings.OPENAI_API_KEY:
        return _default_plan(user)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Build a compact profile string from the user's answers.
        profile = {
            "name": user.name,
            "age_bracket": user.age_bracket,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "goals": user.goals,
            "body_type": user.body_type,
            "activity_level": user.activity_level,
            "diet_type": user.diet_type,
            "food_likes": user.food_likes,
            "food_dislikes": user.food_dislikes,
            "allergies": user.allergies,
            "sleep_hours": user.sleep_hours,
            "water_intake": user.water_intake,
            "routine_type": user.routine_type,
            "stress_level": user.stress_level,
            "face_analysis": user.face_analysis,
        }

        young = user.age_bracket == "16-18"
        age_rule = (
            "This user is a teenager (16-18). Do NOT suggest calorie deficits, "
            "weight-loss targets, or restrictive dieting. Focus on balanced "
            "nutrition, strength, movement, sleep and healthy habits."
            if young else
            "Adult user; standard balanced nutrition guidance is fine, but no "
            "extreme deficits."
        )

        system = (
            "You are VYROX, a wellness planning assistant. Build ONE personalized "
            "plan from the user's profile. " + age_rule + " "
            "No medical claims, no guaranteed outcomes, no appearance ratings. "
            "Respect diet type, food likes/dislikes, and allergies. "
            "Respond with ONLY a JSON object (no markdown) with this shape: "
            '{"workout":{"title":str,"days_per_week":int,"focus":str,'
            '"exercises":[{"name":str,"sets":str}]},'
            '"meals":{"note":str,"breakfast":str,"lunch":str,"dinner":str},'
            '"grooming":{"haircut":str,"skincare":str},'
            '"habits":[str,str,str,str],"insight":str}'
        )

        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=900,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Profile:\n" + json.dumps(profile)},
            ],
        )

        text = resp.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        data["generated_by"] = "ai"
        return data

    except Exception as e:
        print(f"[plan] generation failed: {e}")
        plan = _default_plan(user)
        plan["generated_by"] = "default_after_error"
        return plan
