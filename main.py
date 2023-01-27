from website import app, db
from website import admin_user
from flask_migrate import Migrate
migrate = Migrate(app, db, render_as_batch=True)

if __name__ == '__main__':

    app.run(port=5000 ,debug=True) 