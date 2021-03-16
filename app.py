
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User, db
from forms import UserLoginForm, UserRegisterForm, SearchForm
from sqlalchemy.exc import IntegrityError
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


CURR_USER_KEY = "curr_user"
connect_db(app)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

##############################################################################
#
# user login, user register routes 

@app.route('/login', methods=["GET", "POST"])
def login():
    """ Login the user. """
    form = UserLoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
    
    return render_template('/users/login.html', form=form)

@app.route('/register', methods=["GET", "POST"]) 
def register():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserRegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
            )
            db.session.commit()
        
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('users/register.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    # Log out the user in the current session. 
    do_logout()
    flash("Logging out...", "success")

    # Redirect to the login page after the user logs out. 
    return redirect('/')

@app.route('/')
def index():
    """ The homepage that will show the trending animes! """
    response = requests.get("https://kitsu.io/api/edge/trending/anime?limit=16")
    myList = processResponse(response.json(), "trending")
    return render_template('index.html', anime_trending_list = myList)


##############################################################################
#
# Routes for user's watch-list. 

@app.route('/users/<int:user_id>')
def show_watch_list(user_id):
    """ Show the user's anime watch list. """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/watch_list.html')

##############################################################################
#
# Routes to add anime to user's watch-list. 

@app.route('/users/<int:anime_id>/add', methods=["POST"])
def add_anime():
    """ Add an anime to user's watch list. """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")



    
    return redirect('/')

##############################################################################
#
# Routes to search anime. 

@app.route('/search', methods=["GET", "POST"])
def search_anime():
    """ Search for specific anime. """
    form = SearchForm()

    if form.validate_on_submit():
        data = request.form['englishTitle']
        response =  requests.get(f'{BASE_PATH}/anime?filter[text]={data}')
        myList = processResponse(response.json(), 'search')
        return render_template('search.html', form=form, anime_search_list=myList)

    
    return render_template('search.html', form=form)




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
