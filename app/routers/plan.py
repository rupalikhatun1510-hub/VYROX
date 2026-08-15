"""
Plan routes: generate the AI plan, show the ready screen, show a basic
dashboard.

The building screen (served at /onboarding/building) POSTs to
/plan/generate in the background, then sends the user to /plan/ready.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.plan import Plan
from app.services.plan import generate_plan
from app.templates_engine import templates

router = APIRouter()

GOAL_LABELS = {
    "build_muscle": "Build Muscle", "lose_fat": "Lose Fat",
    "get_stronger": "Get Stronger", "endurance": "Endurance",
    "posture": "Posture", "mobility": "Mobility", "sleep": "Better Sleep",
    "skin": "Clear Skin", "energy": "More Energy",
}


def _user(request: Request, db: Session) -> User | None:
    uid = request.session.get("user_id")
    return db.get(User, uid) if uid else None


@router.post("/plan/generate")
def plan_generate(request: Request, db: Session = Depends(get_db)):
    """Run the AI plan generation once and save it. Called by the loading screen."""
    user = _user(request, db)
    if user is None:
        return JSONResponse({"ok": False, "error": "no user"}, status_code=400)

    data = generate_plan(user)

    # Overwrite any existing plan for this user.
    existing = db.query(Plan).filter(Plan.user_id == user.id).first()
    if existing:
        existing.data = data
    else:
        db.add(Plan(user_id=user.id, data=data))
    db.commit()
    return {"ok": True, "generated_by": data.get("generated_by")}


@router.get("/plan/ready", response_class=HTMLResponse)
def plan_ready(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if user is None:
        return RedirectResponse("/", status_code=303)

    plan_row = db.query(Plan).filter(Plan.user_id == user.id).first()
    if plan_row is None:
        # No plan yet - send back to the building screen to make one.
        return RedirectResponse("/onboarding/building", status_code=303)

    goals = user.goals or []
    goal_label = GOAL_LABELS.get(goals[0], "Wellness") if goals else "Wellness"

    return templates.TemplateResponse(
        request, "onboarding/ready.html",
        {"user": user, "plan": plan_row.data, "goal_label": goal_label},
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _user(request, db)
    if user is None:
        return RedirectResponse("/", status_code=303)
    plan_row = db.query(Plan).filter(Plan.user_id == user.id).first()
    plan = plan_row.data if plan_row else None
    return templates.TemplateResponse(
        request, "dashboard/home.html",
        {"user": user, "plan": plan},
    )
