from fastapi import FastAPI, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import web_data
import secrets
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Set up template rendering
templates = Jinja2Templates(directory="templates")

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set a secret key for sessions and flash messages (FastAPI doesn't use 'flash' directly)
app.state.secret_key = secrets.token_hex(16)  # Secret key for any sessions or message signing

# Initialize web_data (example setup, adapt as per your existing logic)
data = web_data
data.web.create_db()
# Example data handling, adapt as necessary
# data.user.add(0, "admin", "admin")
data.user.update("admin", 1, "newpass")
#data.user_details.add(1, 'John', 'Doe', 'john.doe@example.com', '1234567890')
data.user_details.update(1, email='john.newemail@example.com')

# Pydantic model for form data validation
class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str
    confirm_password: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "About"})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Login"})

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
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
    # Validate form inputs
    if not all([first_name, last_name, email, username, password, confirm_password]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="All fields are required.")

    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")

    # Add logic to save user to the database
    data.user.add(1, username, password)
    user_id = data.user.get_by_username(username)[0]
    data.user_details.add(user_id, first_name, last_name, email)
    print(f"First Name: {first_name}, Last Name: {last_name}, Email: {email}, "
          f"Username: {username}, Password: {password}")

    # Redirect with a success message
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
