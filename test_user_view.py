from unittest import TestCase
from sqlalchemy import exc
from models import db, User, WatchAnime
from app import app, do_login, CURR_USER_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform_test'
app.config['WTF_CSRF_ENABLED'] = False
app.config["TESTING"] = True


class UserViewTestCase(TestCase):
    """Test user models."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()
        WatchAnime.query.delete()

        u1 = User.signup("test1", "email1@email.com", "password")
        u1.id = 1111

        db.session.commit()

        u1 = User.query.get(u1.id)
        self.u1 = u1
        self.client = app.test_client()


    def tearDown(self):
        """ Clear any foul transactions. """
        db.session.rollback()

    def test_login_button(self):
        """ Do visiters see the login button if they are not logged in? """
        
        with self.client as c:
            resp = c.get("/")

        self.assertEqual(resp.status_code, 200)
        self.assertIn("User Login", str(resp.data))

    def test_login_form(self):
        """ Is the user able to see the login form? """

        with self.client as c:
            res = c.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Username', html)
            self.assertIn('Password', html)
            self.assertNotIn('Email', html)

    def test_login_submit(self):
        """ Is the user able to login? """

        with self.client as c:
            d = {'username': 'test1', 'password': 'password'}
            
            res = c.post('/login', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('test1, Logout', html)

    def test_login_bad_credentials(self):
        """ Is the user's login credentials validate for bad inputs? """

        with self.client as c:
            d = {'username': 'test1', 'password': 'bad-password'}
            
            res = c.post('/login', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Login credentials is invalid.', html)


    def test_register_form(self):
        """ Is the user able to see the register form? """

        with self.client as c:
            res = c.get('/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Email', html)
            self.assertIn('Confirm Password', html)

    def test_register_submit(self):
        """ Is a new user able to register? """

        with self.client as c:
            d = {'username': 'newUser', 'password': 'password', 'password2':  'password'}
            
            res = c.post('/register', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('newUser, Logout', html)

    def test_register_password_confirm(self):
        """ Does it redirect back to register page if confirmed password is incorrect? """

        with self.client as c:
            d = {'username': 'newUser', 'password': 'password', 
            'password2': 'not-password'}
            
            res = c.post('/register', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('The confirmed password is incorrect.', html)

    def test_register_duplicate_username(self):
        """ Should not allow duplicate usernames. """

        with self.client as c:
            d = {'username': 'test1', 'password': 'password', 
            'password2': 'password'}
            
            res = c.post('/register', data=d, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Username already taken", html)


    def test_home_page(self):
        """ Is the user able to see trending animes on home page? """

        with self.client as c:
            res = c.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Avg. Rating', html)
            self.assertIn('Add to watch list', html)

    def test_user_watch_list(self):
        """ Is the logged-in user able to view their watch list? """            

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id
            
            res = c.get(f'/users/{self.u1.id}')
            
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn("test1's Watch List", html)

    def test_user_watch_list_without_login(self):
        """ Does the user get redirected if attempting to view watch list? """

        with self.client as c:
            res = c.get(f'/users/{self.u1.id}')
            
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 302)
    
    def test_guest_add_anime(self):
        """ Is the guest redirected to login page after attempting to 

            add an anime to watch list, since login is required?
        """

        with self.client as c:
            
            res = c.post(f'/users/10941/add', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Login is required to add an anime.', html)
            self.assertIn('Username', html)
            self.assertIn('Password', html)
            self.assertNotIn('Email', html)
        
    def test_user_add_anime(self):
        """ After login, can the user add an anime to watch list? """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id
            
            res = c.post(f'/users/10941/add', follow_redirects=True)
            
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn(f"{self.u1.username}'s Watch List", html)
            # 10941 is an anime ID that contains the anime series
            # which 'Kono Subrashii ... is the anime title. 
            self.assertIn("Kono Subarashii Sekai ni Shukufuku wo!", html)

    def test_user_add_anime_duplicates(self):
        """ After user login and adding an anime, did the 'add to watch' button 
        
            get replaced with 'Remove from watch' button?
        """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1.id
            
            res = c.post(f'/users/10941/add', follow_redirects=True)
            
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Remove from watch list', html)
            self.assertNotIn('Add to watch', html)
    
    def test_guest_delete_anime(self):
        """ Does the guest get redirected to home page if they attempt to
            delete an anime without logging in? 
        """

        with self.client as c:
            # 10941 is an anime entry. 
            res = c.post(f'/users/10941/delete', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('User Login', html)
            self.assertIn('Trending Animes', html)
            
    
    def test_anime_details_page(self):
        """ Does the anime details page show information? """

        with self.client as c:
            # 5940 is an anime entry. 
            res = c.get('/animes/5940') 
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Ao no Exorcist', html)
            self.assertIn('TV', html)
            self.assertIn('Teens 13 or older', html)
            self.assertIn('Humans and demons are two sides of the same coin, ', html)
            
    def test_search(self):
        """ Does our search work? """
        with self.client as c:
            
            res = c.post('/search', data={'searchQuery': 'burn the witch'}) 
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('BURN THE WITCH', html)
            self.assertIn("all the deaths in London are related to dragons, fantastical beings", html)

    def test_redirection_followed(self):
        with self.client as c:
            res = c.get('/', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
