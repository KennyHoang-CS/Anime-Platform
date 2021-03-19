
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User, db, WatchAnime
from forms import UserLoginForm, UserRegisterForm, SearchForm
from sqlalchemy.exc import IntegrityError
import requests, random
from helpers import processResponse, handleResponse2, getVideo

app = Flask(__name__)

BASE_PATH = "https://kitsu.io/api/edge"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'chicken123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

app.jinja_env.globals.update(getVideo=getVideo)



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
        else:
            flash("Login credentials is invalid.", 'error')
            return redirect('/login')
        
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
        
        if form.password.data != form.password2.data:
            flash('The confirmed password is incorrect.', 'error')
            return redirect('/register')

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
    animeIDs = []
    if g.user:
        animeIDs = [id.anime_id for id in list(g.user.watchList)]
    myList = processResponse(response.json(), "trending", animeIDs)
    
    randomVideo = myList[random.randint(0,15)][7]
    
    return render_template('index.html', anime_trending_list = myList, video=randomVideo)




##############################################################################
#
# Routes for user's watch-list. 

@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def show_watch_list(user_id):
    """ Show the user's anime watch list. """

    if not g.user:
        flash("Login is required to access your watch list.", "warning")
        return redirect("/login")

    user = User.query.get_or_404(user_id)
    user_list = WatchAnime.query.filter(WatchAnime.user_id == user.id)
    myList = handleResponse2(user_list)
    return render_template('users/watch_list.html', user=user, myList=myList)

##############################################################################
#
# Routes to add anime to user's watch-list. 

@app.route('/users/<int:anime_id>/add', methods=["POST"])
def user_add_anime(anime_id):
    """ Add an anime to user's watch list. """

    if not g.user:
        flash("Login is required to add an anime.", "warning")
        return redirect("/login")
    
    # Check if the 'anime to be added' is already in user's watch list. 
    animeIDs = [id.anime_id for id in list(g.user.watchList)]
    if anime_id in animeIDs:
        flash('This anime is already exist in your watch list.')
        return redirect('/')

    new_watch = WatchAnime(user_id=g.user.id, anime_id=anime_id)
    db.session.add(new_watch)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')

@app.route('/users/<int:anime_id>/delete', methods=["POST"])
def user_delete_anime(anime_id):
    """ Delete an anime from an user's watch list. """

    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")

    WatchAnime.query.filter(WatchAnime.user_id == 1, WatchAnime.anime_id == anime_id).delete()
    db.session.commit()
    
    return redirect(f'/users/{g.user.id}')

##############################################################################
#
# Routes to search anime. 

@app.route('/search', methods=["GET", "POST"])
def search_anime():
    """ Search for specific anime. """
    form = SearchForm()
    
    try:
        if form.validate_on_submit():
            data = request.form['englishTitle']
            response =  requests.get(f'{BASE_PATH}/anime?filter[text]={data}')
            myList = processResponse(response.json(), 'search', [])
            return render_template('search.html', form=form, anime_search_list=myList)
    except (TypeError, IndexError) as e:
        return redirect('/search')
    
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
