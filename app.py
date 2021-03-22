from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, User, db, WatchAnime
from forms import UserLoginForm, UserRegisterForm, SearchForm
from sqlalchemy.exc import IntegrityError
import requests, random
from helpers import processResponse, getAnimeData, videoIDs, randomIntroVideo

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'chicken123'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

CURR_USER_KEY = "curr_user"
connect_db(app)

BASE_PATH = "https://kitsu.io/api/edge"     # Our base path to external API. 


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
    
    # Get our login form from forms.py
    form = UserLoginForm()
    
    if form.validate_on_submit():
        # Using bcrypt, check if the login is legitimate. 
        user = User.authenticate(form.username.data,
                                form.password.data)

        # Upon successful login, redirect to home page ('index.html').
        if user:
            do_login(user)  # Add our user to the session. 
            return redirect("/")
        else:
            # Display error message if 'login' fails and redirect to login page ('login.html').
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

    # Get our register form from forms.py
    form = UserRegisterForm()

    if form.validate_on_submit():
        
        # Did the user confirm their password upon registering?
        if form.password.data != form.password2.data:
            flash('The confirmed password is incorrect.', 'error')
            return redirect('/register')

        # There should be no duplicate usernames. 
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data or ""
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)

        # Upon successful user register, add new user to session and redirect to home page ('index.html').
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

    # Redirect to the login page after the user logs out ('index.html'). 
    return redirect('/')

@app.route('/')
def index():
    """ The homepage that will show the trending animes! """
    
    # Get our trending anime data from external API in limit of 20.
    # Limit is temporary until optimization update. 
    response = requests.get("https://kitsu.io/api/edge/trending/anime?limit=20")
    
    # To hold our user's anime IDs in their watch list. 
    animeIDs = []
    
    # If we have the user in session, get the anime IDs in the user's watch list. 
    if g.user:
        animeIDs = [id.anime_id for id in list(g.user.watchList)]
    
    # Process our trending anime external API data. 
    myList = processResponse(response.json(), "trending", animeIDs)
    
    # IMPORTANT! Need an initial youtube video embed ID for Youtube Iframe API to play
    # in our front-end, but as the client-side browser makes a get request to  
    # our flask-python backend, the data is still being "promised" / 'not-ready-yet,'
    # thus it will display a video error every time the home page ('index.html')
    # is accessed. To get around that, I will use a random youtube embed ID that is
    # already "processed" here on the backend side and will send its value in a hidden
    # button for the client side to fetch to prevent the initial video error. 
    video = randomIntroVideo(videoIDs)
    
    return render_template('index.html', anime_trending_list = myList, video=video)


##############################################################################
#
# Route to get youtube embed IDs. 
@app.route('/api/trailers')
def getVideoIDs():
    """ Returns a jsonified version of youtube embed IDs. """
    
    return jsonify(videoIDs)


##############################################################################
#
# Routes for user's watch-list. 

@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def show_watch_list(user_id):
    """ Show the user's anime watch list. """

    # Is the user logged in to access 'watch-list' feature. 
    if not g.user:
        flash("Login is required to access your watch list.", "warning")
        return redirect("/login")

    # Upon success of user validation, get the user and user's watch list. 
    user = User.query.get_or_404(user_id)
    user_list = WatchAnime.query.filter(WatchAnime.user_id == user.id)
    
    # Get anime data for every entry in user's watch list. 
    myList = getAnimeData(user_list)
    
    # Display the page of animes that the user is watching. 
    return render_template('users/watch_list.html', user=user, myList=myList)


##############################################################################
#
# Routes to get an anime's detail. 

@app.route('/animes/<int:anime_id>', methods=["GET"])
def get_anime_details(anime_id):
    """ Get the anime located by anime_id for its details from external API.  """

    # Make a get request to external API for the individual anime data. 
    response = requests.get(f'{BASE_PATH}/anime/{anime_id}')
    anime = response.json()
    
    # Get its youtube embed id. 
    video = anime['data']['attributes']['youtubeVideoId']

    # If the youtube embed id does not exist, use a default video. 
    if video is None:
        video = 'Pg7P06d2cyI'

    # Check if image source exists, otherwise use a different image. 
    try:
        image = anime['data']['attributes']['coverImage']['original']
    except TypeError:
        image = anime['data']['attributes']['posterImage']['original']

    # Determine if the user is watching this anime. 
    is_watching = list(WatchAnime.query.filter(WatchAnime.anime_id == anime_id))
    is_watching = True if len(is_watching) != 0 else False

    # Return the page ('anime_details.html') that contains the anime data with extra info. 
    return render_template('/animes/anime_details.html', anime=anime, is_watching=is_watching, video=video, image=image)


##############################################################################
#
# Routes to add anime to user's watch-list. 

@app.route('/users/<int:anime_id>/add', methods=["POST"])
def user_add_anime(anime_id):
    """ Add an anime to user's watch list. """

    # Check if the user is logged in to use the "add anime" feature. 
    if not g.user:
        flash("Login is required to add an anime.", "info")
        return redirect("/login")
    
    # Check if the 'anime to be added' is already in user's watch list. 
    animeIDs = [id.anime_id for id in list(g.user.watchList)]
    
    if anime_id in animeIDs:
        flash('This anime is already exist in your watch list.', 'info')
        return redirect(f'/users/{g.user.id}')

    # The anime does not exist in the user's watch list, so add it to their list
    # and track it in the database. 
    new_watch = WatchAnime(user_id=g.user.id, anime_id=anime_id)
    db.session.add(new_watch)
    db.session.commit()

    # Redirect back to the page ('watch_list.html') that has the user's watch list. 
    return redirect(f'/users/{g.user.id}')


##############################################################################
#
# Routes to delete anime from user's watch-list. 

@app.route('/users/<int:anime_id>/delete', methods=["POST"])
def user_delete_anime(anime_id):
    """ Delete an anime from an user's watch list. """

    # Check if the user is logged in, if not, redirect back to ('index.html').
    if not g.user:
        flash("Access unauthorized.", "error")
        return redirect("/")

    # Untrack the user's anime to watch in the database by deleting the anime.
    WatchAnime.query.filter(WatchAnime.user_id == 1, WatchAnime.anime_id == anime_id).delete()
    db.session.commit()
    
    # Redirect back to the page ('watch_list.html') that has the user's watch list.  
    return redirect(f'/users/{g.user.id}')


##############################################################################
#
# Routes to search anime. 

@app.route('/search', methods=["GET", "POST"])
def search_anime():
    """ Search for specific anime. """
    
    # Get our search form from forms.py. 
    form = SearchForm()
    
    # Handle Errors because they will not display search results.  
    try:
        if form.validate_on_submit():
            
            # Searching by category: action, adventure, ....?
            data = request.form['searchQuery']
            response =  requests.get(f'{BASE_PATH}/anime?filter[categories]={data}')
            response = response.json()
            
            # Searching by the title: Konosuba, Naruto, Ao no Exorcist, ....?
            if len(response['data']) == 0:
                response = requests.get(f'{BASE_PATH}/anime?filter[text]={data}')
                response = response.json()
                
                # If search results did not yield anything, let the user know. 
                if len(response['data']) == 0:
                    flash('Search did not find any results.', 'success')
                    return redirect('/search')

            # If no errors, get the anime data for each entry. 
            myList = processResponse(response, 'search', [])
            
            # Display anime data for each entry resulted from searching. 
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

