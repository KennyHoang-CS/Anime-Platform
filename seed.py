from app import db
from models import User, WatchAnime

db.drop_all()
db.create_all()