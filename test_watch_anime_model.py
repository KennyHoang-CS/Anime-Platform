from unittest import TestCase
from sqlalchemy import exc
from models import db, User, WatchAnime
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anime_platform_test'


class WatchAnimeModelTestCase(TestCase):
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

    def test_watch_anime_model(self):
        """Does basic model work?"""

        wa = WatchAnime(
            user_id=self.u1.id,
            anime_id=1
        )

        db.session.add(wa)
        db.session.commit()

        u1 = User.query.get(self.u1.id)

        # User should have one anime in their relationship. 
        self.assertEqual(len(u1.watchList), 1)