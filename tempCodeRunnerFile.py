from website import app, db
from website import admin_user
from flask_migrate import Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':

    app.run(debug=False)