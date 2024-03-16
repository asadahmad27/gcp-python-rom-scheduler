from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status

app = FastAPI()
EV1 = {
    'year': 2000,
    'cost': 4000.0,
    'power': 12.0,
    'manufacturer': 'Suzuki',
    'battery_size': 65.0,
    'wltp_range': 400,
    'name': 'Mehran New',
    'reviews': [
        {'rating': 8, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet', 'submission_date': '2021-01-02'},
        {'rating': 5, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet', 'submission_date': '2021-01-05'},
        {'rating': 3, 'text': 'Lorem ipsum dolor sit amet,Lorem ipsum dolor sit amet', 'submission_date': '2021-01-09'},
    ]
}

EV2 = {'year': 2007, 'cost': 1000, 'power': 400, 'manufacturer': 'Suzuki', 'battery_size': 65, 'wltp_range': 100,
       'name': 'Mehran'}
firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

print(type(EV1), type(EV2))
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


def getUser(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])
    print(user, "user")
    if not user.get().exists:
        user = {
            'name': "N/A",
            'age': 0
        }
        user = firestore_db.collection('users').document(user_token['user_id']).set(user)

    return user


def validateFirebaseToken(id_token):
    if not id_token:
        return None

    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except ValueError as err:
        print(str(err))

    return user_token


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Fetch all EVs from Firestore
    evs_query = firestore_db.collection('ev').stream()
    evs = [doc.to_dict() for doc in evs_query]
    print(evs, "Evs", evs_query)
    # Pass the EVs to the template
    return templates.TemplateResponse('home.html', {
        'request': request,
        # 'user_info': user_info,
        'evs_query': evs_query,
        'evs': evs
    })

@app.post("/", response_class=HTMLResponse)
async def root(request: Request):
    # Fetch all EVs from Firestore

    id_token = request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')
    user = getUser(user_token)
    form = await request.form()
    name = form['name']
    # Logic to add room in db

    return templates.TemplateResponse('home.html', {
        'request': request,
        # 'user_info': user_info,
        'evs_query': evs_query,
        'evs': evs
    })


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    id_token = request.cookies.get("token")
    error_message = "no error"
    user_token = None
    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    return templates.TemplateResponse('login.html', {'request': request, 'name': 'asad', 'user_token': user_token})