from flask_sqlalchemy import SQLAlchemy  
#from flask_bcrypt import Bcrypt


db = SQLAlchemy()
#bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class TrendingAnime(db.Model):
    
    __tablename__ = 'trending_animes'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.Text
    )

    description = db.Column(
        db.Text
    )