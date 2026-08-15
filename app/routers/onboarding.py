"""
Onboarding routes, steps 1 through 6.

Step 5 is the only one that does real work beyond saving form fields:
it takes an uploaded photo, cleans it, runs the AI grooming analysis,
and caches the result on the user row so it's never recomputed.
"""

from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.templates_engine import templates
from app.services.vision import save_clean_photo, analyze_face

router = APIRouter(prefix="/onboarding")


def _current_user(request: Request, db: Session) -> User:
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
def step2_submit(request: Request, goals: str = Form(""), db: Session = Depends(get_db)):
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


# ---------- STEP 5: face upload + AI ----------
@router.get("/step5", response_class=HTMLResponse)
def step5_page(request: Request):
    return templates.TemplateResponse(request, "onboarding/step5.html")


@router.post("/step5")
async def step5_submit(
    request: Request,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)

    # Read the upload, clean it (resize + strip EXIF), save to disk.
    raw = await photo.read()
    path = save_clean_photo(raw, user.id)
    user.face_photo_path = path

    # Run the AI grooming analysis ONCE and cache the result.
    user.face_analysis = analyze_face(path)

    db.commit()
    return RedirectResponse("/onboarding/step6", status_code=303)


# ---------- STEP 6: daily habits ----------
@router.get("/step6", response_class=HTMLResponse)
def step6_page(request: Request):
    return templates.TemplateResponse(request, "onboarding/step6.html")


@router.post("/step6")
def step6_submit(
    request: Request,
    sleep_hours: str = Form(...),
    water_intake: str = Form(...),
    routine_type: str = Form(""),
    stress_level: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    user.sleep_hours = sleep_hours
    user.water_intake = water_intake
    user.routine_type = routine_type or None
    user.stress_level = stress_level or None
    db.commit()
    return RedirectResponse("/onboarding/building", status_code=303)



# ---------- BUILDING: loading screen that triggers plan generation ----------
@router.get("/building", response_class=HTMLResponse)
def building(request: Request):
    return templates.TemplateResponse(request, "onboarding/building.html")


# ---------- DONE: summary (plan generation + dashboard come next) ----------
@router.get("/done", response_class=HTMLResponse)
def done(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    fa = user.face_analysis or {}
    face_line = (
        f"Face: {fa.get('face_shape','—')} · Hair: {fa.get('hair','—')} · Skin: {fa.get('skin','—')}"
        if fa.get("available")
        else "Face analysis: not run (add OpenAI key to enable)"
    )
    return HTMLResponse(
        f"""
        <div style="font-family:system-ui;background:#0e0e24;color:#f5f5ff;
                    min-height:100vh;display:flex;align-items:center;
                    justify-content:center;text-align:center;padding:24px">
          <div style="max-width:380px">
            <h1 style="font-size:26px">All 6 steps done, {user.name or 'there'} ✓</h1>
            <p style="color:#b8b8d8;margin-top:14px;line-height:1.7">
              Goals: {", ".join(user.goals or []) or "—"}<br>
              Body: {user.body_type or "—"} · {user.activity_level or "—"}<br>
              Diet: {user.diet_type or "—"}<br>
              Sleep: {user.sleep_hours or "—"} · Water: {user.water_intake or "—"}<br>
              Routine: {user.routine_type or "—"} · Stress: {user.stress_level or "—"}<br>
              <span style="color:#a78bfa">{face_line}</span>
            </p>
            <p style="color:#7a7a9c;margin-top:16px">
              Next to build: AI plan generation + the home dashboard.
            </p>
            <a href="/" style="color:#a78bfa;display:inline-block;margin-top:20px">← Back to start</a>
          </div>
        </div>
        """
    )
