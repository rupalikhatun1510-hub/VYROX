"""
Onboarding routes, steps 1 through 4.

The session cookie carries user_id between steps so every screen updates
the same row. A small helper, _current_user, fetches that row (or makes
a new one) so each step handler stays short.

Flow: step1 (profile) -> step2 (goals) -> step3 (body/activity)
      -> step4 (diet) -> step5 (placeholder, built next).
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.templates_engine import templates

router = APIRouter(prefix="/onboarding")


def _current_user(request: Request, db: Session) -> User:
    """Return the session's user row, creating one if this is a fresh start."""
    uid = request.session.get("user_id")
    user = db.get(User, uid) if uid else None
    if user is None:
        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)
        request.session["user_id"] = user.id
    return user


def _csv(value: str) -> list[str]:
    """Turn 'a,b,c' from a hidden field into ['a','b','c']; '' -> []."""
    return [v for v in (value or "").split(",") if v]


# ---------- STEP 1 ----------
@router.get("/step1", response_class=HTMLResponse)
def step1_page(request: Request):
    return templates.TemplateResponse(
        request, "onboarding/step1.html",
        {"name": request.session.get("draft_name")},
    )


@router.post("/step1")
def step1_submit(
    request: Request,
    name: str = Form(...),
    age_bracket: str = Form(...),
    height_cm: int = Form(...),
    weight_kg: int = Form(...),
    db: Session = Depends(get_db),
):
    if age_bracket not in {"16-18", "19-24", "25+"}:
        age_bracket = "25+"
    user = _current_user(request, db)
    user.name = name.strip()[:80]
    user.age_bracket = age_bracket
    user.height_cm = height_cm
    user.weight_kg = weight_kg
    db.commit()
    request.session["draft_name"] = user.name
    return RedirectResponse("/onboarding/step2", status_code=303)


# ---------- STEP 2: goals ----------
@router.get("/step2", response_class=HTMLResponse)
def step2_page(request: Request):
    return templates.TemplateResponse(request, "onboarding/step2.html")


@router.post("/step2")
def step2_submit(
    request: Request,
    goals: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    user.goals = _csv(goals)
    db.commit()
    return RedirectResponse("/onboarding/step3", status_code=303)


# ---------- STEP 3: body + activity ----------
@router.get("/step3", response_class=HTMLResponse)
def step3_page(request: Request):
    return templates.TemplateResponse(request, "onboarding/step3.html")


@router.post("/step3")
def step3_submit(
    request: Request,
    body_type: str = Form(""),
    activity_level: str = Form(...),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    user.body_type = body_type or None
    user.activity_level = activity_level
    db.commit()
    return RedirectResponse("/onboarding/step4", status_code=303)


# ---------- STEP 4: diet ----------
@router.get("/step4", response_class=HTMLResponse)
def step4_page(request: Request):
    return templates.TemplateResponse(request, "onboarding/step4.html")


@router.post("/step4")
def step4_submit(
    request: Request,
    diet_type: str = Form(...),
    food_likes: str = Form(""),
    food_dislikes: str = Form(""),
    allergies: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    user.diet_type = diet_type
    user.food_likes = _csv(food_likes)
    user.food_dislikes = (food_dislikes or "").strip()[:300] or None
    user.allergies = allergies or None
    db.commit()
    return RedirectResponse("/onboarding/step5", status_code=303)


# ---------- STEP 5: placeholder (face upload, built next) ----------
@router.get("/step5", response_class=HTMLResponse)
def step5_placeholder(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    name = user.name or "there"
    goals = ", ".join(user.goals or []) or "—"
    return HTMLResponse(
        f"""
        <div style="font-family:system-ui;background:#0e0e24;color:#f5f5ff;
                    min-height:100vh;display:flex;align-items:center;
                    justify-content:center;text-align:center;padding:24px">
          <div style="max-width:360px">
            <h1 style="font-size:26px">Steps 1–4 saved, {name} ✓</h1>
            <p style="color:#b8b8d8;margin-top:14px;line-height:1.6">
              Goals: {goals}<br>
              Body: {user.body_type or '—'} · {user.activity_level or '—'}<br>
              Diet: {user.diet_type or '—'}
            </p>
            <p style="color:#7a7a9c;margin-top:16px">Next to build: step 5 (face upload).</p>
            <a href="/" style="color:#a78bfa;display:inline-block;margin-top:20px">← Back to start</a>
          </div>
        </div>
        """
    )
