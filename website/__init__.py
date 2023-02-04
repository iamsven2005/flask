from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from os import path


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        # if database.db does not exist in this path it creates a database
        db.create_all(app=app)
        print('Created Database! ')

load_dotenv()

app = Flask(__name__)
DB_NAME = 'database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
# create location/path for database
app.config['SECRET_KEY']= os.getenv("SECRET_KEY")
UPLOAD_FOLDER = 'website/static/images/profile_pic/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# enables the database
create_database(app)
bcrypt = Bcrypt(app)
# hashes the passwords 'utf-8' is used check 'models.py'
def admin_user():
    from website.models import User
    db.create_all()
    with app.app_context():
        admin = User(admin=1, username='admin', password='admin123',email_address='admin@example.com', gender='rather not say')
        
        if not User.query.filter_by(admin = admin.id).first() and not User.query.filter_by(email_address = admin.email_address).first() and not User.query.filter_by(username = admin.username).first():
            db.session.add(admin)
            db.session.commit()
            
            #dexter the admin thing is here

login_manager = LoginManager(app)
login_manager.login_view = 'index_page'
login_manager.login_message_category = 'info'
# makes the message flashed blue when user is not authorised/logged in.


from website import routes
