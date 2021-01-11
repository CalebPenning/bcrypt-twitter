from models import db, User
from app import app

db.drop_all()
db.create_all()

User.query.delete()

stav = User.sign_up_user('stavrosvalhalkias', 'favabeans')

nick = User.sign_up_user('thedarkprince', 'stevenseagal')

adam = User.sign_up_user('handsomedevil', 'abugslife')

db.session.add_all([stav, nick, adam])

db.session.commit()