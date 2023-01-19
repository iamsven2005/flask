from website import app
from flask import render_template, request, flash, redirect, url_for
from website.models import User
from website.forms import RegisterForm, LoginForm
from website import db, bcrypt
from flask_login import login_user,logout_user, login_required

def deleteUser(id):
    userID = User.query.filter_by(id = id).first()
    db.session.delete(userID)
    db.session.commit()
    # Get ID of specific user
deleteUser(1)
