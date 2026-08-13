from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates_engine import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def splash(request: Request):
    return templates.TemplateResponse(request, "splash.html")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.post("/login")
def login_submit(email: str = Form(...), password: str = Form(...)):
    return RedirectResponse(url="/onboarding/step1", status_code=303)
