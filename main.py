from fastapi import FastAPI, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr
import web_data
import secrets
from itsdangerous import URLSafeTimedSerializer

app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Secret key for sessions
app.state.secret_key = secrets.token_hex(16)

SECRET_KEY = app.state.secret_key  # Use the secret key from app state
SESSION_COOKIE_NAME = "session"

def create_session_cookie(user_id: int):
    """Create a session cookie for the user."""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps({"user_id": user_id})

def get_user_from_session(cookie: str):
    """Retrieve the user ID from the session cookie."""
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        session_data = serializer.loads(cookie, max_age=3600)  # 1-hour session expiry
        return session_data.get("user_id")
    except Exception:
        return None

@app.middleware("http")
async def set_login_status(request: Request, call_next):
    """Middleware to set user login status based on session cookie."""
    session_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    request.state.user_id = get_user_from_session(session_cookie)
    response = await call_next(request)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page - accessible only if logged in."""
    if not request.state.user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - shows whether user is logged in."""
    is_logged_in = request.state.user_id is not None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Home", "is_logged_in": is_logged_in}
    )

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page - shows whether user is logged in."""
    is_logged_in = request.state.user_id is not None
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "About", "is_logged_in": is_logged_in}
    )

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Login page."""
    return templates.TemplateResponse("index.html", {"request": request, "title": "Login"})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Handle user login."""
    try:
        user_id = web_data.login_user(username, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    session_cookie = create_session_cookie(user_id)
    response.set_cookie(key=SESSION_COOKIE_NAME, value=session_cookie, httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Registration page."""
    return templates.TemplateResponse("index.html", {"request": request, "title": "Register"})

@app.post("/register")
async def register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Handle user registration."""
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")

    try:
        web_data.add_user(
            level=1,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    """Logout user and delete session cookie."""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
