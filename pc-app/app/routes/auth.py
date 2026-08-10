from fastapi import APIRouter, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Admin

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@router.post("/login")
async def login(
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == username, Admin.password == password).first()
    
    if admin:
        res = RedirectResponse(url="/", status_code=302)
        res.set_cookie(key="session_token", value=admin.username, httponly=True)
        return res
        
    return RedirectResponse(url="/login?error=1", status_code=302)

@router.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=302)
    res.delete_cookie("session_token")
    return res
