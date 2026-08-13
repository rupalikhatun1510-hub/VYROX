"""
Onboarding routes.

Step 1 collects name/age/height/weight and creates a user row.
We store the new user's id in the session cookie so later steps
(2..12) can find and update the same row.

Only step 1 is wired for now; steps 2-12 come next, one at a time.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.templates_engine import templates

router = APIRouter(prefix="/onboarding")


@router.get("/step1", response_class=HTMLResponse)
def step1_page(request: Request):
    """Show step 1. Pre-fills name if we already have it in the session."""
    return templates.TemplateResponse(
        request,
        "onboarding/step1.html",
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
    """
    Create (or update) the user row with step-1 data.

    If this browser session already started onboarding, we reuse that
    user id instead of creating a duplicate.
    """
    # Reject the removed age bracket defensively, even though the UI omits it.
    if age_bracket not in {"16-18", "19-24", "25+"}:
        age_bracket = "25+"

    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None

    if user is None:
        user = User()
        db.add(user)

    user.name = name.strip()[:80]
    user.age_bracket = age_bracket
    user.height_cm = height_cm
    user.weight_kg = weight_kg
    db.commit()
    db.refresh(user)

    # Remember this user across the next onboarding steps.
    request.session["user_id"] = user.id
    request.session["draft_name"] = user.name

    # Step 2 isn't built yet; for now go to step 3 (goals) which is next up.
    return RedirectResponse(url="/onboarding/step3", status_code=303)


@router.get("/step3", response_class=HTMLResponse)
def step3_placeholder(request: Request):
    """
    Temporary landing so the flow doesn't 404 after step 1.
    Replaced by the real goals screen in the next build.
    """
    name = request.session.get("draft_name", "there")
    return HTMLResponse(
        f"""
        <div style="font-family:system-ui;background:#0e0e24;color:#f5f5ff;
                    min-height:100vh;display:flex;align-items:center;
                    justify-content:center;text-align:center;padding:24px">
          <div>
            <h1 style="font-size:28px">Saved, {name} ✓</h1>
            <p style="color:#b8b8d8;margin-top:12px">
              Step 1 is in the database.<br>
              The goals screen (step 3) is the next thing to build.
            </p>
            <a href="/" style="color:#a78bfa;display:inline-block;margin-top:20px">← Back to start</a>
          </div>
        </div>
        """
    )
