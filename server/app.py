import os
from bleach import clean
import uvicorn
from fastapi import FastAPI, Request, Form
from starlette.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pymongo import MongoClient
from server.models.models import Registration
from dotenv import load_dotenv

# init
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="client")

load_dotenv()

MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI")

# the db stuff
client = MongoClient(MONGODB_CONNECTION_URI)
db = client["mediDoor"]
part_form = db["users"]
maps = db["map"]


try:
    client.admin.command("ping")
    print("Successfully connected to the database!")
except:
    print("Database connection refused. Please check status of database!")

# part_form.insert_one(
#     {
#         "username": "shourya.de12@gmail.com",
#         "fullname": "Shourya De",
#         "password": "hellohello",
#         "admin": True,
#         "phone": "",
#         "yearvalid": 2027,
#     }
# )


@app.get("/", response_class=HTMLResponse, tags=["GET Register Page"])
async def register(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, tags=["GET endpoint for register"])
async def loginPage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, tags=["GET endpoint for register"])
async def signupForm(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", tags=["POST Login Endpoint for API"])
async def signup(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: int = Form(...),
):
    user = Registration(
        fullname=clean(fullname), phone=phone, email=email, password=password
    )
    if bool((part_form.find_one({"email": email}))):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "em": "Email ID already registered. Please register with new Email ID",
            },
        )
    else:
        part_form.insert_one(user.dict())
        return templates.TemplateResponse(
            "success.html", {"request": request, "sm": "Sucessful Registration!"}
        )


@app.post(
    "/login", response_class=HTMLResponse, tags=["POST Endpoint to Register Teams"]
)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    phone: int = Form(...),
):

    if bool(part_form.find_one({"email": email, "password": password, "phone": phone})):
        data = part_form.find_one({"email": email})

        return templates.TemplateResponse(
            "user.html",
            {
                "request": request,
                "fullname": data["fullname"],
                "email": data["email"],
                "phone": data["phone"],
                "data": data,
                "getDash": False,
            },
        )
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "em": "Invalid Credentials or User doesn't exist. Please contact your admin.",
            },
        )


@app.post(
    "/dashboard",
    response_class=HTMLResponse,
    tags=["POST Endpoint to populate Dashboard"],
)
async def populate(
    request: Request,
    fips: str = Form(...),
    email: str = Form(...),
    phone: int = Form(...),
    fullname: str = Form(...),
):

    if bool(maps.find_one({"FIPS CODE": fips})):

        dashData = maps.find_one({"FIPS CODE": fips})
        prom = dashData["Prominent Disease"]
        mortality = dashData[prom + "_Average_Mortality(in %)"]
        county = dashData["County"]
        mortality = round(float(mortality), 2)

        return templates.TemplateResponse(
            "user.html",
            {
                "request": request,
                "getDash": True,
                "dashData": dashData,
                "fullname": fullname,
                "email": email,
                "phone": phone,
                "prom": prom,
                "mortality": mortality,
                "county": county,
            },
        )
    else:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "em": "Invalid FIPS code or Data not available, please try with another FIPS code",
            },
        )


# if __name__ == "__main__":
#     uvicorn.run("app:app", reload=True, host="127.0.0.1", port=5000)
