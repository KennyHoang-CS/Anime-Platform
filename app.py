
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, TrendingAnime
from forms import LoginForm, NewUserForm
import requests
from helpers import processResponse


app = Flask(__name__)

BASE_PATH = "https://kitsu.io/api/edge"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'chicken123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


connect_db(app)

@app.route('/')
def index():
    """ The homepage that will show the trending animes! """
    res = requests.get("https://kitsu.io/api/edge/trending/anime?limit=12")
    myList = processResponse(res.json())
    return render_template('index.html', anime_trending_list = myList)

##############################################################################
#
# login routes 

@app.route('/login')
def login():
    """ Login the user. """
    form = LoginForm()

    return render_template('/users/login.html', form=form)


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
