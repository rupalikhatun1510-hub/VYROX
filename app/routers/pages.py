"""
Routes that serve the public pages: splash and login.

The login POST is a placeholder for now - it doesn't check a real password
yet, because signup/auth is a later step. We keep it so the form has a target.
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates_engine import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def splash(request: Request):
    """The first screen: GET STARTED / LOG IN."""
    return templates.TemplateResponse(request, "splash.html")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Show the login form."""
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
def login_submit(email: str = Form(...), password: str = Form(...)):
    """
    Placeholder login. Real password checking comes with the auth step.
    For now any login just sends you to onboarding so the flow is walkable.
    """
    return RedirectResponse(url="/onboarding/step1", status_code=303)
