"""
One shared Jinja2 templates object.

Routers import `templates` from here instead of each creating their own,
so there's a single configured place pointing at app/templates.
"""

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
