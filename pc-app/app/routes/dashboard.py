from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


def check_auth(request: Request):
    return request.cookies.get("session_token") is not None


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not check_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    response = templates.TemplateResponse("index.html", {"request": request})
    response.set_cookie(key="session_token", value=request.cookies.get("session_token"), httponly=True, max_age=600)
    return response


@router.get("/cards", response_class=HTMLResponse)
async def cards_page(request: Request):
    if not check_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    response = templates.TemplateResponse("cards.html", {"request": request})
    response.set_cookie(key="session_token", value=request.cookies.get("session_token"), httponly=True, max_age=600)
    return response


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, error: str = None, success: str = None):
    if not check_auth(request):
        return RedirectResponse(url="/login", status_code=302)
    response = templates.TemplateResponse("settings.html", {"request": request, "error": error, "success": success})
    response.set_cookie(key="session_token", value=request.cookies.get("session_token"), httponly=True, max_age=600)
    return response


@router.post("/settings")
async def update_settings(
    request: Request,
    old_password: str = Form(...),
    new_username: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
        
    admin = db.query(Admin).filter(Admin.username == token).first()
    if not admin or admin.password != old_password:
        return RedirectResponse(url="/settings?error=1", status_code=302)
        
    admin.username = new_username
    admin.password = new_password
    db.commit()
    
    # Logout user so they can login with new credentials
    res = RedirectResponse(url="/login?success=1", status_code=302)
    res.delete_cookie("session_token")
    return res
