from unittest import TestCase
from sqlalchemy import exc
from models import db, User, WatchAnime
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform_test'



class UserModelTestCase(TestCase):
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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no animes in their watch list.
        self.assertEqual(len(u.watchList), 0)
        
    # User class methods test. 
    def test_users_repr(self):
        """ Does the User __repr__ work? """
        
        self.assertEqual(User.__repr__(self.u1), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_user_create(self):
        """ Does User.create successfully create a new user given valid credentials? """
        
        self.assertIsInstance(User.signup('NewName', 'NewEmail', 'NewPassWord'), User)
        self.assertIsNot(User.signup('', 'NewEmail', 'N'), User)

    # User authenticate tests. 
    def test_user_authenticate(self):
        """ Does user authenticate work? """

        # Test valid username and valid password. 
        self.assertTrue(User.authenticate("test1", "password"))
        # Test valid username with bad password.
        self.assertFalse(User.authenticate('test1', 'badPassword'))
        # Test bad username with valid password. 
        self.assertFalse(User.authenticate('badUsername', 'password'))

    def test_user_invalid_username(self):
        """ Does it fail for an user's invalid username? """

        bad_user = User.signup(None, 'lol@gmail.com', 'password')
        bad_user.id = 123
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_user_invalid_password(self):
        """ Does it fail for an user's invalid password? """

        with self.assertRaises(ValueError):
            User.signup('bad', 'bad@gmail.com', "")