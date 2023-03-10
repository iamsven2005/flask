import os
import re
from dotenv import load_dotenv
from website import app, bcrypt
from flask import render_template, request, flash, redirect, url_for, jsonify, Response
from website.models import *
from website.forms import *
from website import db
from flask_login import login_user, logout_user, login_required, current_user
from website import admin_user
import shelve
from datetime import datetime
from uuid import uuid4  # Unique key generator
import pandas as pd
from flask_mail import Mail, Message
import qrcode
import io, base64, PIL
from werkzeug.utils import secure_filename
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from uuid import uuid1
from sqlalchemy import func
# To ensure file name is parsed

# Note that for otp expiry, need to fiddle with js

load_dotenv()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Background Tasks

db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
db_tempemail['email'] = None
db_tempemail.close()

from flask_uploads import UploadSet, configure_uploads, IMAGES

photos = UploadSet('photos', IMAGES)

def configure_app(app):
    configure_uploads(app, photos)


@app.route('/photos')
def photo_gallery():
    all_photos = Photo.query.all()
    return render_template('photos.html', photos=all_photos)

@app.route('/photo/<int:photo_id>')
def photo1(photo_id):
    photo = Photo.query.get(photo_id)
    return render_template('photo.html', photo=photo)







@app.route('/test')
def index():
    # Open the shelve database and retrieve the list of stored images
    db = shelve.open('images_db')
    images = db.get('images', [])
    db.close()
    
    # Render the HTML template with the list of images
    return render_template('test.html', images=images)

@app.route('/testupload', methods=['POST'])
def upload():
    # Retrieve the uploaded image from the request
    image = request.files.get('image')
    
    # Save the image to the shelve database
    db = shelve.open('images_db')
    images = db.get('images', [])
    images.append(image)
    db['images'] = images
    db.close()
    
    # Redirect the user back to the main page
    return redirect('/test')

if __name__ == '__main__':
    app.run(debug="True")



# For Error Handling when user enters invalid url address
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404

#password strength checker



@app.context_processor
def cart_database():
    Cart_Dict = {}
    Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'c')
    try:
        print(current_user)
        # Shopping Cart Database
        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            print(Shopping_Cart_Database[str(current_user.id)])

        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

    except AttributeError:
        if "default" in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database["default"]
        else:
            Shopping_Cart_Database['default'] = Cart_Dict

    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    Cart_Dict = list(Cart_Dict.values())

    return dict(cart=Cart_Dict)


@app.context_processor
def inbox_database():
    tickets_response_dict = {}
    ticket_database = shelve.open('website/databases/Messages/messages.db', 'c')
    try:
        # Ticket Response Database
        if str(current_user.id) in ticket_database:
            tickets_response_dict = ticket_database[f'{current_user.id}']

        else:
            ticket_database[str(current_user.id)] = tickets_response_dict

    except AttributeError:
        if "default" in ticket_database:
            tickets_response_dict = ticket_database["default"]
        else:
            ticket_database['default'] = tickets_response_dict

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")

    except TypeError:
        print("Type Error User Is not logged in yet")

    except Exception as e:

        if "default" in ticket_database:
            tickets_response_dict = ticket_database["default"]
        else:
            inbox_database['default'] = tickets_response_dict

        print(f"An Unknown Error has occurred, {e}")

    else:
        tickets_response_dict = list(tickets_response_dict.values())

    return dict(current_user_inbox=tickets_response_dict)

from flask import render_template, request

@app.route('/photos')
def photos():
    all_photos = Photo.query.all()
    return render_template('photos.html', photos=all_photos)

@app.route('/photo/<int:photo_id>')
def photo(photo_id):
    photo = Photo.query.get(photo_id)
    return render_template('photo.html', photo=photo)



# Sven
# the '/' route is default route

@app.route('/moneymanagement')
@login_required
def money_management():
    return render_template('trans_or_dep.html')


@app.route('/home')
@login_required
def home_page():
    userID = User.query.filter_by(id=current_user.id).first()
    admin_user()
    return render_template('home.html', user=userID)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    userID = User.query.filter_by(id=current_user.id).first()
    Owned_Items_Dict = {}
    Wish_Dict = {}
    Items_Dict = {}
    Products = {}
    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'r')
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'r')

        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
            Wish_Database.close()
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict
            Wish_Database.close()
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
            Item_Database.close()
        else:
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    try:
        products_database = shelve.open('website/databases/products/products.db', 'r')
        if str(current_user.id) in products_database:
            Products = products_database[str(current_user.id)]
            products_database.close()

        else:
            products_database[str(current_user.id)] = Products
            products_database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    try:
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'r')
        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            Owned_Items_Database.close()
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
            Owned_Items_Database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    Selling_Items = []
    print(Items_Dict)
    for i in Items_Dict:
        Item = Items_Dict.get(i)
        if Item.get_owner_id() == current_user.id:
            print('hello')
            Selling_Items.append(Item)

    print(Wish_Dict)
    print(Selling_Items)
    update_username_form = Update_Username()
    update_email_form = Update_Email()
    update_gender_form = Update_Gender()
    update_password_form = Update_Password()
    update_profile_pic_form = Update_Profile_Pic()
    if update_username_form.validate_on_submit:
        pass
    if update_username_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_username_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')

    return render_template('profile.html', username_form=update_username_form, email_form=update_email_form, profilepic_form = update_profile_pic_form,
                           gender_form=update_gender_form, password_form=update_password_form,
                           owned_items=Owned_Items_Dict, wished_items=Wish_Dict, selling_items=len(Selling_Items), products=Products, user=userID)


@app.route('/deleteProfile')
@login_required
def delete_profile():
    db.create_all()
    userID = User.query.filter_by(id=current_user.id).first()
    db.session.delete(userID)
    db.session.commit()
    logout_user()
    flash("Account Deleted Successfully", category="success")
    return redirect(url_for("home_page"))

@app.route('/sudo_deleteProfile/<int:id>')
@login_required
def sudo_delete_profile(id):
    db.create_all()
    userID = User.query.filter_by(id=id).first()
    db.session.delete(userID)
    db.session.commit()
    logout_user()
    flash("Account Deleted Successfully", category="success")
    return redirect(url_for("home_page"))



@app.route("/updateUser", methods=['GET', 'POST'])
def update_user():
    update_user_form = Update_User()
    userID = User.query.filter_by(id=current_user.username).first()
    if request.method == 'POST' and update_user_form.validate_on_submit():
        attempted_user = User.query.filter_by(username=current_user.username).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=update_user_form.password1.data):
            userID.password = bcrypt.generate_password_hash('update_user_form.password1').decode('utf-8')
            userID.username = update_user_form.username.data
            userID.email_address = update_user_form.email_address.data
            #userID.gender = update_user_form.gender.data
            #userID.profile_pic = request.files['profile_pic']
            # Change it to a string to save to db
            #userID.profile_pic = pic_name
            db.session.commit()
            flash("User Particulars changed successfully", category="success")
            return redirect(url_for("profile_page"))

        else:  # If there are not errors from the validations
            flash("Password is Incorrect Try again.", category='danger')
    if update_user_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_user_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')
    return render_template("UpdateUser.html", form=update_user_form, user=userID)

@app.route("/updateDescription", methods=["GET", "POST"])
def update_description():
    form = Update_User_Description()
    userID = User.query.filter_by(id=current_user.id).first()
    if request.method == "POST" and form.validate_on_submit():
        print("form: ", form.description.data)
        userID.description = form.description.data
        db.session.commit()
        flash("Description updated", category='success')
        return redirect(url_for('profile_page'))
    return render_template("UpdateDescription.html", form=form, user=current_user.id)

@app.route("/updateProfilePic", methods=['GET', 'POST'])
def update_profile_pic():
    update_profile_pic_form = Update_Profile_Pic()
    if request.method == 'POST':
        userID = User.query.filter_by(id=current_user.id).first()
        # Check for profile pic
        if request.files['profile_pic']:
            userID.profile_pic = request.files['profile_pic']

            # Grab Image Name
            pic_filename = secure_filename(userID.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid1()) + "_" + pic_filename
            # Save That Image
            saver = request.files['profile_pic']


            # Change it to a string to save to db
            userID.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("Profile pic Updated Successfully!", category='success')
                return redirect(url_for("profile_page"))
                
            except:
               if update_profile_pic_form.errors != {}:  # If there are not errors from the validations
                    errors = []
                    for err_msg in update_profile_pic_form.errors.values():
                        errors.append(err_msg)
                    err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
                    flash(f'{err_message}', category='danger')
            return redirect(url_for('profile_page'))
				


@app.route("/updateUsername", methods=['GET', 'POST'])
def update_username():
    update_username_form = Update_Username()
    if request.method == 'POST' and update_username_form.validate_on_submit():
        userID = User.query.filter_by(id=current_user.id).first()
        userID.username = update_username_form.username.data
        db.session.commit()
        flash("Username changed successfully", category="success")
        return redirect(url_for("profile_page"))
    if update_username_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_username_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')
    return redirect(url_for('profile_page'))


@app.route("/updateEmail", methods=['GET', 'POST'])
def update_email():
    update_email_form = Update_Email()
    if request.method == 'POST' and update_email_form.validate_on_submit():
        userID = User.query.filter_by(id=current_user.id).first()
        userID.email_address = update_email_form.email_address.data
        db.session.commit()
        flash("Email changed successfully", category="success")
        return redirect(url_for("profile_page"))
    if update_email_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_email_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')
    return redirect(url_for('profile_page'))


@app.route("/updateGender", methods=['GET', 'POST'])
def update_gender():
    update_gender_form = Update_Gender()
    if request.method == 'POST' and update_gender_form.validate_on_submit():
        userID = User.query.filter_by(id=current_user.id).first()
        userID.gender = update_gender_form.gender.data
        db.session.commit()
        flash("Gender changed successfully", category="success")
        return redirect(url_for("profile_page"))
    if update_gender_form.errors != {}:  # If there are no errors from the validations
        errors = []
        for err_msg in update_gender_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')
    return redirect(url_for('profile_page'))


@app.route("/updatePassword", methods=['GET', 'POST'])
def update_password():
    update_password_form = Update_Password()
    userID = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST' and update_password_form.validate_on_submit():
        password = request.form.get('new_password')

        attempted_user = User.query.filter_by(username=current_user.username).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=update_password_form.current_password.data):
            
            
            userID.password_hash = bcrypt.generate_password_hash(update_password_form.new_password.data).decode('utf-8')
            db.session.commit()
            flash("Password Changed Successfully", category="success")
        else:
            flash("Current Password is Incorrect.", category='danger')

        return redirect(url_for("profile_page"))
    if update_password_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_password_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')
    return redirect(url_for('profile_page'))


@app.route('/PastOrders')
@login_required
def past_orders():
    Owned_Items_Dict = {}
    try:
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'r')

        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            Owned_Items_Database.close()
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
            Owned_Items_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")
    print(Owned_Items_Dict)

    return render_template('PastOrders.html', items=Owned_Items_Dict)


@app.route('/data/pastorders')
def past_orders_data():
    Owned_Items_Dict = {}
    dates = []
    qty_purchased = []
    past_orders_dict = {}

    try:
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'c')
        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            Owned_Items_Database.close()
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
            Owned_Items_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    for i in Owned_Items_Dict:
        dates.append(Owned_Items_Dict[i].get_date_purchase())
        qty_purchased.append((Owned_Items_Dict[i].get_qty_purchased()))

    df = pd.DataFrame(list(zip(dates, qty_purchased)), columns=["dates", "qty"])
    df = df.groupby("dates")["qty"].sum().reset_index()
    dates = df["dates"].tolist()
    qty_purchased = df["qty"].tolist()
    print("Head")

    past_orders_dict['Dates'] = dates
    past_orders_dict['Qty'] = qty_purchased
    return jsonify(past_orders_dict)


@app.route('/data/sales')
@login_required
def sales_data():
    dates = []
    transactions = []
    sales_dict = {}
    new_sales_dict = {}
    sales_log_count = 0
    try:

        SalesLogDatabase = shelve.open('website/databases/SalesLogs/sales.db', 'c')
        SalesCounter = shelve.open('website/databases/SalesLogs/salescount.db', 'c')

        if str(current_user.id) in SalesLogDatabase:
            sales_dict = SalesLogDatabase[str(current_user.id)]
            SalesLogDatabase.close()
        else:
            SalesLogDatabase[str(current_user.id)] = sales_dict
            SalesLogDatabase.close()
        if str(current_user.id) in SalesCounter:
            sales_log_count = SalesCounter[str(current_user.id)]
            SalesCounter.close()
        else:
            SalesCounter[str(current_user.id)] = sales_log_count
            SalesCounter.close()
    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    for i in sales_dict:
        dates.append(sales_dict[i].get_date_recorded())
        transactions.append(sales_dict[i].get_transaction())

    df = pd.DataFrame(list(zip(dates, transactions)), columns=["dates", "trans"])
    df = df.groupby("dates")["trans"].sum().reset_index()
    dates = df["dates"].tolist()
    transactions = df["trans"].tolist()
    print("Head")

    new_sales_dict['Dates'] = dates
    new_sales_dict['Trans'] = transactions
    return jsonify(new_sales_dict)


@app.route('/data/transactions')
@login_required
def transaction_data():
    dates = []
    transactions = []
    logs_dict = {}
    new_transactions_dict = {}

    try:

        TransactionLogsDatabase = shelve.open('website/databases/TransactionLogs/transactionlogs.db', 'c')
        # TransactionCounter = shelve.open('website/databases/TransactionLogs/transactionlogscount.db', 'c')

        if str(current_user.id) in TransactionLogsDatabase:
            logs_dict = TransactionLogsDatabase[str(current_user.id)]
        else:
            TransactionLogsDatabase[str(current_user.id)] = logs_dict

        # if str(current_user.id) in TransactionCounter:
        #     log_count = TransactionCounter[str(current_user.id)]
        # else:
        #     TransactionCounter[str(current_user.id)] = transaction_logs_count



    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    for i in logs_dict:
        dates.append(logs_dict[i].get_date_recorded())
        transactions.append(logs_dict[i].get_transaction())

    df = pd.DataFrame(list(zip(dates, transactions)), columns=["dates", "log"])
    df = df.groupby("dates")["log"].sum().reset_index()
    dates = df["dates"].tolist()
    transactions = df["log"].tolist()
    print("Head")

    new_transactions_dict['Dates'] = dates
    new_transactions_dict['Logs'] = transactions
    return jsonify(new_transactions_dict)


@app.route('/Appointment')
@login_required
def appointment():
    bookings_dict = {}
    count = 0
    try:
        booking_database = shelve.open('website/databases/Bookings/Booking.db', 'c')
        booking_database_uniqueID = shelve.open('website/databases/Bookings/Booking_uniqueID.db', 'c')
        if str(current_user.id) in booking_database:
            bookings_dict = booking_database[str(current_user.id)]
        else:
            booking_database[str(current_user.id)] = bookings_dict

        if str(current_user.id) in booking_database_uniqueID:
            count = booking_database_uniqueID[str(current_user.id)]
        else:
            booking_database_uniqueID[str(current_user.id)] = count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    return render_template('appointment.html', bookings=bookings_dict)


@app.route('/Delete_Appointment/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    bookings_dict = {}
    count = 0
    try:
        booking_database = shelve.open('website/databases/Bookings/Booking.db', 'w')
        booking_database_uniqueID = shelve.open('website/databases/Bookings/Booking_uniqueID.db', 'w')
        if str(current_user.id) in booking_database:
            bookings_dict = booking_database[str(current_user.id)]
        else:
            booking_database[str(current_user.id)] = bookings_dict

        if str(current_user.id) in booking_database_uniqueID:
            count = booking_database_uniqueID[str(current_user.id)]
        else:
            booking_database_uniqueID[str(current_user.id)] = count

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            del bookings_dict[id]
            booking_database[str(current_user.id)] = bookings_dict
            flash('Booking cancelled successfully!', category='success')

    return redirect(url_for('appointment'))


@app.route('/markets', methods=['POST', "GET"])
@login_required
def market_page():
    purchase_form = Purchase_Form()
    Items_Dict = {}
    Wish_Dict = {}
    event_dict = {}
    DisabledProducts_Dict = {}
    search = request.args.get('search')
    try:
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'r')
        event_database = shelve.open('website/databases/Events/event.db', 'c')


        if "EventInfo" not in event_database:
            event_database["EventInfo"] = event_dict
            return redirect(url_for('appointment'))
        else:
            event_dict = event_database["EventInfo"]

        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict



    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'r')
        products_database = shelve.open('website/databases/products/products.db', 'c')
        DisableProducts_Database = shelve.open('website/databases/disabled_products/disable_products.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
            Item_Database.close()
        else:
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()

        if "DisableProducts" in DisableProducts_Database:
            DisabledProducts_Dict = DisableProducts_Database["DisableProducts"]
            DisableProducts_Database.close()

        else:
            DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict
            DisableProducts_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    print("Market Database")
    print(Items_Dict)
    print("Disabled Products")
    print(DisabledProducts_Dict)


    return render_template('market.html', items=Items_Dict, wish_items=Wish_Dict, purchase_form=purchase_form,
                           event_items=event_dict, search=search, DisabledProducts=DisabledProducts_Dict)


@app.route('/image/<int:id>')
def get_img(id):
    
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)
    '''
    img = Item_Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404
    '''

@app.route('/shopping_cart', methods=['GET', 'POST'])
@login_required
def Shopping_Cart():
    purchase_form = Purchase_Form()
    Cart_Dict = {}
    try:
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'r')

        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            Shopping_Cart_Database.close()
        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
            Shopping_Cart_Database.close()


    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        total = 0
        for i in Cart_Dict:
            total += Cart_Dict[i].get_total_cost()
        print('Cart Dictionary')
        print(Cart_Dict)
    return render_template('ShoppingCart.html', cart_items=Cart_Dict, total=total)


@app.route('/edit_shopping_cart', methods=['GET', 'POST'])
@login_required
def Edit_Shopping_Cart():
    # uuid is Cart_Dict Key
    # uuid2 is Shopping Cart Item ID
    # uuid3 is Owner ID(Seller ID) of Shopping Cart Item
    Edit_Cart_Form = Edit_Cart()
    Cart_Dict = {}
    Products = {}
    Items_Dict = {}
    total = 0
    try:
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'r')

        # Current User Shopping cart database
        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            print(Shopping_Cart_Database[str(current_user.id)])
            Shopping_Cart_Database.close()
        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
            Shopping_Cart_Database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        for i in Cart_Dict:
            total += Cart_Dict[i].get_total_cost()

    return render_template('EditCart.html', cart_items=Cart_Dict, total=total, edit_cart_form=Edit_Cart_Form)


@app.route('/edit_shopping_cart_item', methods=['GET', 'POST'])
@login_required
def Edit_Shopping_Cart_Item():
    # uuid is Cart_Dict Key
    # uuid2 is Shopping Cart Item ID
    # uuid3 is Owner ID(Seller ID) of Shopping Cart Item
    Edit_Cart_Form = Edit_Cart()
    Cart_Dict = {}
    Products_dict = {}
    Items_Dict = {}
    # Logs Dictionary & Counters
    logs_dict = {}
    log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    try:
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'w')
        Item_Database = shelve.open('website/databases/items/items.db', 'w')
        products_database = shelve.open('website/databases/products/products.db', 'w')

        # Current Market Database
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']

        else:
            Item_Database['ItemInfo'] = Items_Dict

        # Current User Shopping cart database
        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            print(Shopping_Cart_Database[str(current_user.id)])

        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

        # Seller Items Database
        if str(request.form.get('uuid3')) in products_database:
            Products_dict = products_database[str(request.form.get('uuid3'))]
        else:
            products_database[str(request.form.get('uuid3'))] = Products_dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        UserID = User.query.filter_by(id=current_user.id).first()

        print(UserID)
        if request.method == 'POST':
            print("Hello")
            cart_item = Cart_Dict[str(request.form.get('uuid'))]
            print(cart_item.get_qty_purchased())
            print(Edit_Cart_Form.quantity.data)
            print(cart_item)
            if Edit_Cart_Form.quantity.data != None:
                if cart_item.get_quantity() > 0:
                    if Edit_Cart_Form.quantity.data <= cart_item.get_quantity():
                        total = cart_item.get_price() * Edit_Cart_Form.quantity.data
                        item_quantity = Items_Dict[str(request.form.get('uuid2'))].get_quantity()
                        cart_item_quantity = Cart_Dict[str(request.form.get('uuid'))].get_qty_purchased()
                        print(cart_item_quantity)
                        if cart_item_quantity < Edit_Cart_Form.quantity.data:
                            # Minus Quantity of Item
                            new_item_quantity = item_quantity - (Edit_Cart_Form.quantity.data - cart_item_quantity)
                            print('minus')
                            print(new_item_quantity)
                        else:
                            # Adds Quantity of Item
                            new_item_quantity = item_quantity + (cart_item_quantity - Edit_Cart_Form.quantity.data)
                            print('add')
                            print(new_item_quantity)
                        print(new_item_quantity)
                        Items_Dict[str(request.form.get('uuid2'))].set_quantity(new_item_quantity)
                        Products_dict[str(request.form.get('uuid2'))].set_quantity(new_item_quantity)
                        Item_Database['ItemInfo'] = Items_Dict
                        products_database[str(request.form.get('uuid3'))] = Products_dict
                        # Set New Quantity Purchased Of Item Added to Cart
                        cart_item.set_qty_purchased(Edit_Cart_Form.quantity.data)
                        cart_item.set_total_cost(total)
                        print("Cart items")
                        print(Cart_Dict)
                        print(Shopping_Cart_Database[str(current_user.id)])
                        Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
                        flash(f"{cart_item.get_name()} Quantity Changed Successfully", category='success')
                        Item_Database.close()
                        Shopping_Cart_Database.close()

                        # Tracking Log Section
                        log_count += 1
                        log = Logs(
                            id=str(log_count),
                            log_description=f'{cart_item.get_name()} Quantity was changed to {Edit_Cart_Form.quantity.data}',
                            date_recorded=datetime.now().strftime("%d/%m/%y"),
                            time_recorded=datetime.now().strftime("%I:%M:%S %p")
                        )

                        logs_dict[str(log_count)] = log
                        # Logs Database
                        LogsDatabase[str(current_user.id)] = logs_dict
                        # Counters
                        LogsCounter[str(current_user.id)] = log_count
                        LogsDatabase.close()
                        LogsCounter.close()

                    else:
                        flash(f"{cart_item.get_name()} does not have enough in stock", category='danger')
                else:
                    if Edit_Cart_Form.quantity.data < cart_item.get_qty_purchased():
                        total = cart_item.get_price() * Edit_Cart_Form.quantity.data
                        item_quantity = Items_Dict[str(request.form.get('uuid2'))].get_quantity()
                        cart_item_quantity = Cart_Dict[str(request.form.get('uuid'))].get_qty_purchased()
                        print(cart_item_quantity)
                        if cart_item_quantity < Edit_Cart_Form.quantity.data:
                            # Minus Quantity of Item
                            new_item_quantity = item_quantity - (Edit_Cart_Form.quantity.data - cart_item_quantity)
                            print('minus')
                            print(new_item_quantity)
                        else:
                            # Adds Quantity of Item
                            new_item_quantity = item_quantity + (cart_item_quantity - Edit_Cart_Form.quantity.data)
                            print('add')
                            print(new_item_quantity)
                        print(new_item_quantity)
                        Items_Dict[str(request.form.get('uuid2'))].set_quantity(new_item_quantity)
                        Products_dict[str(request.form.get('uuid2'))].set_quantity(new_item_quantity)
                        Item_Database['ItemInfo'] = Items_Dict
                        products_database[str(request.form.get('uuid3'))] = Products_dict
                        # Set New Quantity Purchased Of Item Added to Cart
                        cart_item.set_qty_purchased(Edit_Cart_Form.quantity.data)
                        cart_item.set_total_cost(total)
                        print("Cart items")
                        print(Cart_Dict)
                        print(Shopping_Cart_Database[str(current_user.id)])
                        Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
                        flash(f"{cart_item.get_name()} Quantity Changed Successfully", category='success')
                        Item_Database.close()
                        Shopping_Cart_Database.close()

                        # Tracking Log Section
                        log_count += 1
                        log = Logs(
                            id=str(log_count),
                            log_description=f'{cart_item.get_name()} Quantity was changed to {Edit_Cart_Form.quantity.data}',
                            date_recorded=datetime.now().strftime("%d/%m/%y"),
                            time_recorded=datetime.now().strftime("%I:%M:%S %p")
                        )

                        logs_dict[str(log_count)] = log
                        # Logs Database
                        LogsDatabase[str(current_user.id)] = logs_dict
                        # Counters
                        LogsCounter[str(current_user.id)] = log_count
                        LogsDatabase.close()
                        LogsCounter.close()
                    else:
                        print(Edit_Cart_Form.quantity.data)
                        flash(f"{cart_item.get_name()} is out of stock", category='danger')
            else:
                flash(f"Please Enter a Valid Quantity", category='danger')
    return redirect(url_for('Edit_Shopping_Cart'))


@app.route('/removefromcart', methods=['GET', 'POST'])
@login_required
def remove_from_cart():
    purchase_form = Purchase_Form()
    Cart_Dict = {}
    Items_Dict = {}
    Products = {}

    # Logs Dictionary & Counters
    logs_dict = {}
    log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    try:
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'w')
        Item_Database = shelve.open('website/databases/items/items.db', 'w')
        products_database = shelve.open('website/databases/products/products.db', 'w')

        if str(request.form.get('uuid3')) in products_database:
            Products = products_database[str(request.form.get('uuid3'))]
        else:
            products_database[str(request.form.get('uuid3'))] = Products

        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            print(Shopping_Cart_Database[str(current_user.id)])

        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        UserID = User.query.filter_by(id=current_user.id).first()
        name = Cart_Dict[str(request.form.get('uuid'))].get_name()
        cart_qty = Cart_Dict[str(request.form.get('uuid'))].get_qty_purchased()
        new_qty = Items_Dict[str(request.form.get('uuid2'))].get_quantity() + cart_qty
        # remove item from cart
        del Cart_Dict[str(request.form.get('uuid'))]
        Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

        # Update Market base new Quantity
        Items_Dict[str(request.form.get('uuid2'))].set_quantity(new_qty)
        Item_Database['ItemInfo'] = Items_Dict

        # Update Owner of Item new Quantity after removing from cart
        Products[str(request.form.get('uuid2'))].set_quantity(new_qty)
        products_database[str(request.form.get('uuid3'))] = Products

        # update cart counter
        UserID.shoppingCartCount -= 1
        db.session.commit()

        Shopping_Cart_Database.close()
        Item_Database.close()
        products_database.close()
        flash(f"{name} removed from cart", category='success')
        # Tracking Log Section
        log_count += 1
        log = Logs(
            id=str(log_count),
            log_description=f'{cart_qty}x {name} was removed from your cart',
            date_recorded=datetime.now().strftime("%d/%m/%y"),
            time_recorded=datetime.now().strftime("%I:%M:%S %p")
        )

        logs_dict[str(log_count)] = log
        # Logs Database
        LogsDatabase[str(current_user.id)] = logs_dict
        # Counters
        LogsCounter[str(current_user.id)] = log_count
        LogsDatabase.close()
        LogsCounter.close()
    return redirect(url_for('Shopping_Cart'))



@app.route('/receipt', methods=['POST', 'GET'])
@login_required
def Receipt():
    def createQR(*args: Item):
        return qrcode.make('Receipt:\n{}\nTotal price:${}'.format('\n'.join(
            [i.get_name() + ',Qty: ' + str(i.get_qty_purchased()) + ',Cost: $' + str(i.get_total_cost()) + ',OrderDate: Jan 8 2023, warranty for 1 year, End-Date: Jan 8 2024' for i in
             args]),
            sum([i.get_total_cost() for i in args])))

    # args are items objects ,the * means accept all args yes, you can put as many arguments as you want.
    # Also creates a QR code

    def toB64String(image: PIL):
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        b = base64.b64encode(buffered.getvalue())  # bytes
        return b.decode('utf-8')  # string

    # Accepts a PIl object(accepts QR code object) and converts the image to base64
    # the converts it to a base 64 string.

    Cart_Dict = {}
    try:
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'r')

        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
            print(Shopping_Cart_Database[str(current_user.id)])
            Shopping_Cart_Database.close()
        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
            Shopping_Cart_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")
    else:
        total = 0
        for i in Cart_Dict:
            total += Cart_Dict[i].get_total_cost()
    print("Checkout Cart")
    print(Cart_Dict)
    order_date = datetime.now().strftime("%d/%m/%Y")
    expiration_date = datetime.now() + timedelta(days=365)
    current_day = datetime.now().strftime("%d")
    expected_delivery_date = datetime.now().strftime(f"{int(current_day) + 2}/%m/%Y")

    return render_template('Receipt.html', cart_items=Cart_Dict, total=total, order_date=order_date, expiration_date=expiration_date,
                           expected_delivery_date=expected_delivery_date,
                           qr_code=toB64String((createQR(*Cart_Dict.values()))))


@app.route('/InventoryManagement', methods=['GET', 'POST'])
@login_required
def Inventory_Management():
    Restock_Form = Restock_Item_Form()
    Products = {}
    DisabledProducts_Dict = {}
    try:
        DisableProducts_Database = shelve.open('website/databases/disabled_products/disable_products.db', 'c')
        products_database = shelve.open('website/databases/products/products.db', 'c')
        if str(current_user.id) in products_database:
            Products = products_database[str(current_user.id)]
        else:
            products_database[str(current_user.id)] = Products

        if "DisableProducts" in DisableProducts_Database:
            DisabledProducts_Dict = DisableProducts_Database["DisableProducts"]
        else:
            DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    return render_template('InventoryManagement.html', products=Products, restock_form=Restock_Form,
                           DisabledProducts=DisabledProducts_Dict)


@app.route('/RestockItem', methods=['GET', 'POST'])
@login_required
def Restock_Item():
    Restock_Form = Restock_Item_Form()
    Products = {}
    Items_Dict = {}
    try:
        products_database = shelve.open('website/databases/products/products.db', 'c')
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        if str(current_user.id) in products_database:
            Products = products_database[str(current_user.id)]
        else:
            products_database[str(current_user.id)] = Products

        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']

        else:
            Item_Database['ItemInfo'] = Items_Dict


    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            restocked = Products[str(request.form.get('uuid'))].get_quantity() + Restock_Form.quantity.data
            Products[str(request.form.get('uuid'))].set_quantity(restocked)
            products_database[str(current_user.id)] = Products
            Items_Dict[str(request.form.get('uuid'))].set_quantity(restocked)
            Item_Database['ItemInfo'] = Items_Dict
            flash(f"{Products[str(request.form.get('uuid'))].get_name()} Restocked Successfully!", category='success')

            Item_Database.close()
            products_database.close()
    return redirect(url_for('Inventory_Management'))


@app.route('/DisableProduct', methods=['GET', 'POST'])
@login_required
def Disable_Product():
    DisabledProducts_Dict = {}
    Items_Dict = {}

    try:
        DisableProducts_Database = shelve.open('website/databases/disabled_products/disable_products.db', 'c')
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        if "DisableProducts" in DisableProducts_Database:
            DisabledProducts_Dict = DisableProducts_Database["DisableProducts"]
        else:
            DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict

        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']

        else:
            Item_Database['ItemInfo'] = Items_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            if str(request.form.get('uuid')) not in DisabledProducts_Dict:
                disabled_item = Items_Dict[str(request.form.get('uuid'))]
                DisabledProducts_Dict[disabled_item.get_id()] = disabled_item
                DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict
                flash(f"{disabled_item.get_name()} has been disabled!", category='danger')
                DisableProducts_Database.close()
                Item_Database.close()

    return redirect(url_for('Inventory_Management'))


@app.route('/EnableProduct', methods=['GET', 'POST'])
@login_required
def Enable_Product():
    DisabledProducts_Dict = {}
    Items_Dict = {}

    try:
        DisableProducts_Database = shelve.open('website/databases/disabled_products/disable_products.db', 'c')
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        if "DisableProducts" in DisableProducts_Database:
            DisabledProducts_Dict = DisableProducts_Database["DisableProducts"]
        else:
            DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict

        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']

        else:
            Item_Database['ItemInfo'] = Items_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            disabled_item = Items_Dict[str(request.form.get('uuid'))]
            del DisabledProducts_Dict[disabled_item.get_id()]
            DisableProducts_Database["DisableProducts"] = DisabledProducts_Dict
            flash(f'{disabled_item.get_name()} has been enabled!', category='success')
            DisableProducts_Database.close()

    return redirect(url_for('Inventory_Management'))


@app.route('/Wish', methods=['GET', 'POST'])
@login_required
def wish():
    wish_form = Wish_Form()
    Items_Dict = {}
    Wish_Dict = {}
    # Logs Dictionary & Counters
    logs_dict = {}
    log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'w')
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']

        else:
            Item_Database['ItemInfo'] = Items_Dict

        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            wish_item = Items_Dict[str(request.form.get('uuid'))]
            if str(request.form.get('uuid')) not in Wish_Dict:
                print(Items_Dict)
                print(request.form.get('uuid'))
                print(Wish_Dict)
                Wish_Dict[wish_item.get_id()] = wish_item
                Wish_Database[str(current_user.id)] = Wish_Dict
                flash(f"{wish_item.get_name()} Added to Wishlist", category='success')
                Item_Database['ItemInfo'] = Items_Dict
                Wish_Database.close()
                Item_Database.close()
                # Tracking Log & Transaction Section
                log_count += 1
                log = Logs(
                    id=str(log_count),
                    log_description=f'{wish_item.get_name()} added to your wishlist',
                    date_recorded=datetime.now().strftime("%d/%m/%y"),
                    time_recorded=datetime.now().strftime("%I:%M:%S %p")
                )

                logs_dict[str(log_count)] = log
                # Logs Database
                LogsDatabase[str(current_user.id)] = logs_dict
                # Counters
                LogsCounter[str(current_user.id)] = log_count
                LogsDatabase.close()
                LogsCounter.close()
            else:
                print(Wish_Dict)
                wish_item = Items_Dict[str(request.form.get('uuid'))]
                flash(f"{wish_item.get_name()} is already in your wishlist", category='success')

    return redirect(url_for('market_page'))


@app.route('/DeleteWish', methods=['GET', 'POST'])
@login_required
def delete_wish():
    wish_form = Wish_Form()
    Wish_Dict = {}
    # Logs Dictionary & Counters
    logs_dict = {}
    log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    try:
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'c')
        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST':
            wish = Wish_Dict[str(request.form.get('uuid'))]
            del Wish_Dict[str(request.form.get('uuid'))]
            Wish_Database[str(current_user.id)] = Wish_Dict
            flash(f'{wish.get_name()} removed from wishlist', category='success')
            # Tracking Log & Transaction Section
            log_count += 1
            log = Logs(
                id=str(log_count),
                log_description=f'{wish.get_name()} removed from wishlist',
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )

            logs_dict[str(log_count)] = log
            # Logs Database
            LogsDatabase[str(current_user.id)] = logs_dict
            # Counters
            LogsCounter[str(current_user.id)] = log_count
            LogsDatabase.close()
            LogsCounter.close()
    return redirect(url_for('market_page'))


@app.route('/WishList')
@login_required
def wish_list():
    Items_Dict = {}
    Wish_Dict = {}
    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'r')
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
            Item_Database.close()
        else:
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()

        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
            Wish_Database.close()
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict
            Wish_Database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")
    print(Wish_Dict)

    return render_template('WishList.html', items=Wish_Dict)


@app.route('/AddItemForm', methods=['POST', 'GET'])
@login_required
def Add_Item():
    add_item_form = Add_Item_Form()
    your_products_dict = {}
    Items_Dict = {}
    unique_id = uuid4()

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        Your_Products_Database = shelve.open('website/databases/products/products.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict
        if str(current_user.id) in Your_Products_Database:
            your_products_dict = Your_Products_Database[str(current_user.id)]
        else:
            Your_Products_Database[str(current_user.id)] = your_products_dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if add_item_form.validate_on_submit() and request.method == 'POST':
            pic = request.files['pic']
            
            if not pic:
                flash("Please Insert an Image before adding a product.", category='danger')
                return redirect(url_for('Add_Item'))

            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype
            '''
            if request.files['item_pic']:
                item.item_pic = request.files['item_pic']

                # Grab Image Name
                pic_filename = secure_filename(item.item_pic.filename)
                # Set UUID
                pic_name = str(uuid1()) + "_" + pic_filename
                # Save That Image
                saver = request.files['item_pic']

                item.item_pic = pic_name
            '''
            while True:
                unique_id = uuid4()
                if str(unique_id) not in Items_Dict:
                    img = Img(img=pic.read(), mimetype=mimetype, name=filename)
                    db.session.add(img)
                    db.session.commit()
                    #img = Item_Img(img=pic_name)
                    #db.session.add(img)
                    #saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                    #db.session.commit()
                    item = Item(id=str(unique_id),
                                name=add_item_form.name.data,
                                quantity=add_item_form.quantity.data,
                                description=add_item_form.description.data,
                                price=add_item_form.price.data,
                                owner=current_user.username,
                                owner_id=current_user.id,
                                image=img.id
                                )

                    Items_Dict[str(unique_id)] = item
                    your_products_dict[str(unique_id)] = item
                    Item_Database['ItemInfo'] = Items_Dict
                    Your_Products_Database[str(current_user.id)] = your_products_dict
                    flash('Item Added Successfully', category='success')
                    print('Item added')
                    Item_Database.close()
                    Your_Products_Database.close()
                    return redirect(url_for('retrieve_items'))
                else:
                    continue

    return render_template('AddItem.html', add_item_form=add_item_form), 200

@app.route("/retrieveItems")
def retrieve_items():
    Items_Dict = {}
    Item_Database = shelve.open('website/databases/items/items.db', 'r')
    Items_Dict = Item_Database['ItemInfo']
    print(Items_Dict)

    Item_Database.close()

    items_list = []
    for key in Items_Dict:
        item = Items_Dict.get(key)
        items_list.append(item)

    return render_template('retrieveItems.html', count=len(items_list), items_list=items_list)

@app.route('/updateItem/<id>', methods=['GET', 'POST'])
def update_item(id):
    update_item_form = Add_Item_Form()
    Items_Dict = {}

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'w')
        #Your_Products_Database = shelve.open('website/databases/products/products.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict
        
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST' and update_item_form.validate():
            item = Items_Dict.get(id)
            item.set_name(update_item_form.name.data)
            item.set_quantity(update_item_form.quantity.data)
            item.set_description(update_item_form.description.data)
            item.set_price(update_item_form.price.data)
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()
     
            return redirect(url_for('retrieve_items'))
        else:
            Item_Database = shelve.open('website/databases/items/items.db', 'r')
            Items_dict = Item_Database['ItemInfo']
            Item_Database.close()

            item = Items_dict.get(id)
            update_item_form.name.data = item.get_name()
            update_item_form.quantity.data = item.get_quantity()
            update_item_form.description.data = item.get_description()
            update_item_form.price.data = item.get_price()*0.8

        return render_template('UpdateItem.html', update_item_form=update_item_form), 200

@app.route("/discounts/<id>", methods=["POST", "GET"])
def discounted_item(id):
    update_item_form = Add_Item_Form()
    Items_Dict = {}

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'w')
        #Your_Products_Database = shelve.open('website/databases/products/products.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict
        
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        if request.method == 'POST' and update_item_form.validate():
            item = Items_Dict.get(id)
            item.set_price(update_item_form.price.data)
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()
     
            return redirect(url_for('retrieve_items'))
        else:
            Item_Database = shelve.open('website/databases/items/items.db', 'r')
            Items_dict = Item_Database['ItemInfo']
            Item_Database.close()

            item = Items_dict.get(id)
            update_item_form.price.data = item.get_price()

        return render_template('discounts.html', update_item_form=update_item_form), 200

@app.route('/deleteItem/<id>', methods=['POST'])
def delete_item(id):
    Item_dict = {}
    Item_Database = shelve.open('website/databases/items/items.db', 'w')
    Items_Dict = Item_Database['ItemInfo']

    Items_Dict.pop(id)

    Item_Database["ItemInfo"] = Items_Dict
    Item_Database.close()

    return redirect(url_for('retrieve_items'))



@app.route('/PurchaseItem', methods=['POST', 'GET'])
@login_required
def Purchase_Item():
    purchase_item_form = Purchase_Form()
    Items_Dict = {}
    Owned_Items_Dict = {}
    Cart_Dict = {}
    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'c')
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict

        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            print(Owned_Items_Database[str(current_user.id)])
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict

        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    # Logs
    logs_dict = {}
    transaction_logs_dict = {}
    log_count = 0
    transaction_log_count = 0

    # Sales Dict
    sales_dict = {}
    sales_log_count = 0

    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        TransactionLogsDatabase = shelve.open('website/databases/TransactionLogs/transactionlogs.db', 'c')
        TransactionCounter = shelve.open('website/databases/TransactionLogs/transactionlogscount.db', 'c')
        SalesLogDatabase = shelve.open('website/databases/SalesLogs/sales.db', 'c')
        SalesCounter = shelve.open('website/databases/SalesLogs/salescount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

        if str(current_user.id) in TransactionLogsDatabase:
            transaction_logs_dict = TransactionLogsDatabase[str(current_user.id)]
        else:
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict

        if str(current_user.id) in TransactionCounter:
            transaction_log_count = TransactionCounter[str(current_user.id)]
        else:
            TransactionCounter[str(current_user.id)] = transaction_log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")


    else:
        UserID = User.query.filter_by(id=current_user.id).first()
        print("Cart Items")
        print(Cart_Dict)
        total = 0
        for i in Cart_Dict:
            print(Cart_Dict[i])
            total += Cart_Dict[i].get_total_cost()

        #UserID_Owner = User.query.filter_by(id=Items_Dict[str(request.form.get('uuid'))].get_owner_id()).first()
        if request.method == 'POST':
            if total <= current_user.budget:
                # Minus Balance of User
                current_user.budget -= total
                # Increase Current User Spending
                current_user.spending += total
                for i in Cart_Dict:
                    UserID_Owner = User.query.filter_by(id=Cart_Dict[i].get_owner_id()).first()
                    # Adds Balance of Item Owner
                    UserID_Owner.budget += Cart_Dict[i].get_total_cost()
                    # Adds Profit to Item Owner
                    UserID_Owner.profits += Cart_Dict[i].get_total_cost()

                UserID.shoppingCartCount = 0
                db.session.commit()
                Item_Database['ItemInfo'] = Items_Dict
                # Set Extra Purchased Item Attributes
                for i in Cart_Dict:
                    Cart_Dict[i].set_date_purchase(datetime.now().strftime("%d/%m/%Y"))
                    Cart_Item = Cart_Dict[i]
                    print(Cart_Item)
                    Owned_Items_Dict[str(uuid4())] = Cart_Item
                Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
                print("Owned items")
                print(Owned_Items_Dict)
                print(Owned_Items_Database[str(current_user.id)])
                flash(f"Purchased Made Successfully", category='success')

                Item_Database.close()
                Owned_Items_Database.close()

                sales_log_count += 1
                transaction_log_count += 1
                log_count += 1
                # Tracking Log & Transaction Section
                log = Logs(
                    id=str(log_count),
                    log_description=f'You Purchased ${total:.2f} worth of items',
                    date_recorded=datetime.now().strftime("%d/%m/%y"),
                    time_recorded=datetime.now().strftime("%I:%M:%S %p")
                )
                transaction_log = TransactionLogs(
                    id=str(transaction_log_count),
                    log_description=f'You Purchased ${total:.2f} worth of items',
                    transaction=(total) * -1,
                    date_recorded=datetime.now().strftime("%d/%m/%y"),
                    time_recorded=datetime.now().strftime("%I:%M:%S %p")
                )
                logs_dict[str(log_count)] = log
                transaction_logs_dict[str(transaction_log_count)] = transaction_log
                LogsDatabase[str(current_user.id)] = logs_dict
                LogsCounter[str(current_user.id)] = log_count
                TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict
                TransactionCounter[str(current_user.id)] = transaction_log_count
                # Seller Logs Section
                for i in Cart_Dict:
                    owner_id = Cart_Dict[i].get_owner_id()
                    # Seller Dict
                    seller_logs_dict = {}
                    seller_transactions_logs_dict = {}
                    seller_sales_logs_dict = {}

                    seller_logs_count = 0
                    seller_transaction_logs_count = 0
                    seller_sales_logs_count = 0
                    try:
                        if str(owner_id) in LogsDatabase:
                            seller_logs_dict = LogsDatabase[str(owner_id)]
                        else:
                            LogsDatabase[str(owner_id)] = seller_logs_dict

                        if str(owner_id) in LogsCounter:
                            seller_logs_count = LogsCounter[str(owner_id)]
                        else:
                            LogsCounter[str(owner_id)] = seller_logs_count

                        if str(owner_id) in TransactionLogsDatabase:
                            seller_transactions_logs_dict = TransactionLogsDatabase[str(owner_id)]
                        else:
                            TransactionLogsDatabase[str(owner_id)] = seller_transactions_logs_dict

                        if str(owner_id) in TransactionCounter:
                            seller_transaction_logs_count = TransactionCounter[str(owner_id)]
                        else:
                            TransactionCounter[str(owner_id)] = seller_transaction_logs_count

                        if str(owner_id) in SalesLogDatabase:
                            seller_sales_logs_dict = SalesLogDatabase[str(owner_id)]
                        else:
                            SalesLogDatabase[str(owner_id)] = seller_sales_logs_dict

                        if str(owner_id) in SalesCounter:
                            seller_sales_logs_count = SalesCounter[str(owner_id)]
                        else:
                            SalesCounter[str(owner_id)] = seller_sales_logs_count

                    except IOError:
                        print("An Error Has Occurred Trying to Read The Database")

                    except Exception as e:
                        print(f"An Unknown Error has occurred, {e}")
                    print('error')
                    print(seller_transaction_logs_count)
                    seller_logs_count += 1
                    seller_transaction_logs_count += 1
                    seller_sales_logs_count += 1

                    seller_log = Logs(
                        id=str(seller_logs_count),
                        log_description=f'You received ${Cart_Dict[i].get_total_cost():.2f} from your sales',
                        date_recorded=datetime.now().strftime("%d/%m/%y"),
                        time_recorded=datetime.now().strftime("%I:%M:%S %p")
                    )
                    transaction_log_seller = TransactionLogs(
                        id=str(seller_transaction_logs_count),
                        log_description=f'You received ${Cart_Dict[i].get_total_cost():.2f} from your sales',
                        transaction=Cart_Dict[i].get_total_cost(),
                        date_recorded=datetime.now().strftime("%d/%m/%y"),
                        time_recorded=datetime.now().strftime("%I:%M:%S %p")
                    )
                    sale_log_seller = SalesLogs(
                        id=str(seller_sales_logs_count),
                        log_description=f'You received ${Cart_Dict[i].get_total_cost():.2f} from your sales',
                        transaction=Cart_Dict[i].get_total_cost(),
                        date_recorded=datetime.now().strftime("%d/%m/%y"),
                        time_recorded=datetime.now().strftime("%I:%M:%S %p")
                    )
                    # Update Seller Logs Dict
                    seller_logs_dict[str(seller_logs_count)] = seller_log
                    LogsCounter[str(owner_id)] = seller_logs_count

                    seller_transactions_logs_dict[str(seller_transaction_logs_count)] = transaction_log_seller
                    TransactionCounter[str(owner_id)] = seller_transaction_logs_count

                    seller_sales_logs_dict[str(seller_sales_logs_count)] = sale_log_seller
                    SalesCounter[str(owner_id)] = seller_sales_logs_count

                    # Update Seller Logs Database
                    LogsDatabase[str(owner_id)] = seller_logs_dict
                    TransactionLogsDatabase[str(owner_id)] = seller_transactions_logs_dict
                    SalesLogDatabase[str(owner_id)] = seller_sales_logs_dict

                Cart_Dict.clear()
                Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
                Shopping_Cart_Database.close()
                LogsDatabase.close()
                TransactionLogsDatabase.close()
                SalesLogDatabase.close()

                LogsCounter.close()
                TransactionCounter.close()
                SalesCounter.close()
            else:
                flash(f"Insufficient funds to purchase Items", category='danger')
                return redirect(url_for('Shopping_Cart'))

    return redirect(url_for('payment_page'))


@app.route('/AddToCart', methods=['POST', 'GET'])
@login_required
def Add_To_Cart():
    # uuid is Item ID
    # uuid2 is Seller ID
    add_to_cart_form = Add_To_Cart_Form()
    Items_Dict = {}
    Cart_Dict = {}
    Seller_Items_Dict = {}

    # Logs Dictionary & Counters
    logs_dict = {}
    log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'c')
        Shopping_Cart_Database = shelve.open('website/databases/shoppingcart/cart.db', 'c')
        Seller_Products_Database = shelve.open('website/databases/products/products.db', 'c')
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
        else:
            Item_Database['ItemInfo'] = Items_Dict

        if str(current_user.id) in Shopping_Cart_Database:
            Cart_Dict = Shopping_Cart_Database[str(current_user.id)]
        else:
            Shopping_Cart_Database[str(current_user.id)] = Cart_Dict

        if str(request.form.get('uuid2')) in Seller_Products_Database:
            Seller_Items_Dict = Seller_Products_Database[str(request.form.get('uuid2'))]
        else:
            Seller_Products_Database[str(request.form.get('uuid2'))] = Seller_Items_Dict


    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    else:
        print("Hello")
        print(str(request.form.get('uuid2')))
        print(str(request.form.get('uuid')))
        print(str(current_user.id))
        UserID = User.query.filter_by(id=current_user.id).first()
        print(UserID)
        if request.method == 'POST':
            cart_item = Items_Dict[str(request.form.get('uuid'))]
            print(cart_item.get_quantity())
            print(add_to_cart_form.quantity.data)
            print(cart_item)
            print("Seller dictionary")
            print(Seller_Items_Dict)
            if add_to_cart_form.quantity.data != None:
                if cart_item.get_quantity() > 0:
                    if add_to_cart_form.quantity.data <= cart_item.get_quantity():
                        total = cart_item.get_price() * add_to_cart_form.quantity.data
                        item_quantity = Items_Dict[str(request.form.get('uuid'))].get_quantity()
                        # seller_item_quantity = Seller_Items_Dict[str(request.form.get('uuid'))].get_quantity()
                        # Minus Quantity of Item
                        item_quantity -= add_to_cart_form.quantity.data
                        Items_Dict[str(request.form.get('uuid'))].set_quantity(item_quantity)
                        # Minus Quantity of Seller Item Database
                        Seller_Items_Dict[str(request.form.get('uuid'))].set_quantity(item_quantity)
                        Item_Database['ItemInfo'] = Items_Dict
                        Seller_Products_Database[str(request.form.get('uuid2'))] = Seller_Items_Dict
                        # Set Quantity Purchased Of Item Added to Cart
                        cart_item.set_qty_purchased(add_to_cart_form.quantity.data)
                        cart_item.set_total_cost(total)
                        Cart_Dict[str(uuid4())] = cart_item
                        print("Cart items")
                        print(Cart_Dict)
                        print(Shopping_Cart_Database[str(current_user.id)])
                        Shopping_Cart_Database[str(current_user.id)] = Cart_Dict
                        flash(f"{cart_item.get_name()} Added to Cart", category='success')
                        Item_Database.close()
                        Shopping_Cart_Database.close()
                        UserID.shoppingCartCount += 1
                        db.session.commit()
                        # Tracking Log & Section
                        log_count += 1
                        log = Logs(
                            id=str(log_count),
                            log_description=f'{add_to_cart_form.quantity.data}x {cart_item.get_name()} was added to your cart',
                            date_recorded=datetime.now().strftime("%d/%m/%y"),
                            time_recorded=datetime.now().strftime("%I:%M:%S %p")
                        )

                        logs_dict[str(log_count)] = log
                        # Logs Database
                        LogsDatabase[str(current_user.id)] = logs_dict
                        # Counters
                        LogsCounter[str(current_user.id)] = log_count
                        LogsDatabase.close()
                        LogsCounter.close()


                    else:
                        flash(f"{cart_item.get_name()} does not have enough in stock", category='danger')
                else:
                    flash(f"{cart_item.get_name()} is out of stock", category='danger')
            else:
                flash(f"Please Enter a Valid Quantity", category='danger')
    return redirect(url_for('market_page'))


#staff profile storage
@app.route('/staff')
@login_required
def staff_page():
    staff_dict = {}
    try:
        #db_shelve = shelve.open('website/databases/partners/partner.db', 'r')
        db_shelve = shelve.open('website/databases/staff/staff.db', 'r')
        staff_dict = db_shelve['Staff']
        db_shelve.close()
    except IOError:
        print("Error trying to read file")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    staff_list = []
    for key in staff_dict:
        staff = staff_dict.get(key)
        staff_list.append(staff)

    staffid_list = []
    users = User.query.all()
    for user in users:
        staffid_list.append(user.staff_id)
    print("staffid_list: ",staffid_list)

    return render_template('staff.html', count=len(staff_list), staffid_list=staffid_list, staff_list=staff_list, users=users)


@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff_page():
    form = CreateStaffForm()
    db_shelve = shelve.open('website/databases/staff/staff.db', 'c')
    db_shelve_uniqueID = shelve.open('website/databases/staff/staff_uniqueID.db', 'c')
    staff_dict = {}
    ids = 0
    try:
        if 'Staff' in db_shelve:
            staff_dict = db_shelve['Staff']
        else:
            db_shelve['Staff'] = staff_dict
        if 'ID' in db_shelve_uniqueID:
            ids = db_shelve_uniqueID['ID']
        else:
            db_shelve_uniqueID['ID'] = ids
    except:
        print("Error in retrieving Staff from database")

    if request.method == 'POST':
        if form.validate_on_submit():
            staff = Staff(name=form.name.data,
                               location=form.location.data,
                               email=form.email.data)
            ids += 1
            staff.set_id(ids)
            staff.set_staff_count(ids)
            staff_dict[ids] = staff
            db_shelve['Staff'] = staff_dict
            db_shelve_uniqueID['ID'] = ids
            flash("Record submitted Successfully", category='success')
            db_shelve.close()
            db_shelve_uniqueID.close()
            return redirect(url_for('landing_page'))
        else:
            if form.errors != {}:  # If there are not errors from the validations
                errors = []
                for err_msg in form.errors.values():
                    errors.append(err_msg)
                err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
                flash(f'{err_message}', category='danger')
            flash("An Error Occurred trying to submit Form", category='danger')
            return redirect(url_for('add_staff_page'))
   


    return render_template('RegisterStaff.html', form=form)


@app.route('/deleteStaff/<int:id>', methods=['POST'])
def delete_staff(id):
    staff_dict = {}
    db_shelve = shelve.open('website/databases/staff/staff.db', 'w')
    staff_dict = db_shelve['Staff']
    staff_dict.pop(id)
    db_shelve['Staff'] = staff_dict
    db_shelve.close()

    return redirect(url_for('staff_page'))


@app.route('/updateStaff/<int:id>', methods=['POST'])
def update_staff(id):
    form = UpdateStaffForm()
    if request.method == 'POST' and form.validate_on_submit():
        staff_dict = {}
        db_shelve = shelve.open('website/databases/staff/staff.db', 'w')
        staff_dict = db_shelve['Staff']
        staff = staff_dict.get(id)
        staff.set_name(form.name.data)
        staff.set_location(form.location.data)
        staff.set_email(form.email.data)
        staff.set_staff_id(form.staff_id.data)
        staff.set_date(datetime.now().strftime("%d/%m/%Y"))

        db_shelve['Staff'] = staff_dict
        db_shelve.close()
        return redirect(url_for('staff_page'))
    else:
        staff_dict = {}
        db_shelve = shelve.open('website/databases/staff/staff.db', 'r')
        staff_dict = db_shelve['Staff']
        db_shelve.close()
        staff = staff_dict.get(id)
        form.name.data = staff.get_name()
        form.location.data = staff.get_location()
        form.email.data = staff.get_email()
        form.staff_id.data = staff.get_staff_id()

        return render_template('updateStaff.html', form=form)


#staff account management
@app.route('/staff/staff_management')
@login_required
def staff_management():
    staff_dict = {}
    try:
        #db_shelve = shelve.open('website/databases/partners/partner.db', 'r')
        db_shelve = shelve.open('website/databases/staff/staff.db', 'r')
        staff_dict = db_shelve['Staff']
        db_shelve.close()
    except IOError:
        print("Error trying to read file")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    staff_list = []
    for key in staff_dict:
        staff = staff_dict.get(key)
        staff_list.append(staff)
    users = User.query.all()
    print("Staff: ", users)
    return render_template('StaffAccount_Management.html', count=len(staff_list), staff_list=staff_list, users=users)


@app.route('/registerStaffAccount/<int:id>', methods=['GET', 'POST'])
@login_required
def register_staff_account(id):
    db.create_all()
    form = Register_Staff_Account()
    staff = ''
    staff_dict = {}
    staff_db = shelve.open('website/databases/staff/staff.db', 'w')
    staff_dict = staff_db["Staff"]

    id=id
    staff = staff_dict.get(id)
    current_id = staff.get_id()
    print(current_id)

    staff_id = form.staff_id.data
    staff.set_staff_id(staff_id)

    
    if request.method == 'POST' and form.validate_on_submit():
        password = form.password1.data
        print("password is: ", password)
        user_to_create = User(username=form.username.data,
                            staff_id = staff.get_staff_count(),
                            email_address=form.work_email.data,
                            password=form.password1.data,
                            usertype="staff")
        db.session.add(user_to_create)
        db.session.commit()
    
        user_email = {}
        user_email = staff.get_email()
        print(user_email)

        if form.errors != {}:  # If there are not errors from the validations
            errors = []
            for err_msg in form.errors.values():
                errors.append(err_msg)
            err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
            flash(f'{err_message}', category='danger')

        db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
        try:
            db_tempemail['email'] = user_email
            db_tempemail.close()
        except Exception as e:
            print(f'{e} error has occurred! Database will close!')
            db_tempemail.close()
            return redirect(url_for('register_staff_account', id=current_id))

        msg = Message('Login credentials for staff account creation', sender='agegracefullybothelper@gmail.com',
                        recipients=[staff.get_email()])
        msg.body = f"Dear valued staff, \n\n We have received a request to create a staff account for you. Your login credentials are: \nUsername: {form.username.data} \nPassword: {form.password1.data} \nYour work email: {form.work_email.data} \nPlease do not respond back to this message as this is just a bot account."
        mail.send(msg)
        
        flash(f"Success! Account {user_to_create.username} created!", category='success')

        return redirect(url_for('landing_page'))

    return render_template('registerStaffAccount.html', form=form, staff=staff)

@app.route('/staff/staff_management/update/<int:id>', methods=['POST', 'GET'])
@login_required
def staff_management_update(id):
    form = Update_Staff_Account()
    userID = User.query.filter_by(id=id).first()

    if request.method == 'POST' and form.validate_on_submit():
        # NOTE THAT FORM DOES NOT VALIDATE ON SUBMIT!
        # Also note that below does not work
        userID.username = form.username.data
        userID.email_address = form.email_address.data
        db.session.commit()
        flash("User's Particulars updated to database successfully!", category="success")
    else:
        flash("Some error occurred!", category="danger")

    if request.method == 'GET':
        return render_template('update_staff_management.html', form=form, user=userID)

    flash(form.errors, category="danger")
    return redirect(url_for("staff_management"))

@app.route('/staff/staff_management/enable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def staff_management_enable(id):
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Enabled'
    flash(f"{userID.username} account has been enabled", category='success')
    db.session.commit()
    return redirect(url_for('staff_management'))


@app.route('/staff/staff_management/disable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def staff_management_disable(id):
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Disabled'
    flash(f'{userID.username} account has been disabled', category='danger')
    db.session.commit()
    return redirect(url_for('staff_management'))


@app.route('/staff/staff_management/staff_info/<int:id>', methods=['GET'])
@login_required
def staff_information(id):
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/staff/staff.db', 'w')
    retailer_dict = retailer_db["Retailers"]

    current_retail = retailer_dict.get(id-7)
    print(current_retail)
    retailer_db.close()

    return render_template("staff_information.html", current_retail=current_retail, retail_id=id)

  


@app.route('/transfer_funds')
@login_required
def transfer_funds_page():
    users = User.query.all()
    return render_template('TransferFunds.html', users=users)


@app.route('/transfer_funds_user/<int:id>', methods=['POST'])
@login_required
def transfer_funds_user_page(id):
    userID = User.query.filter_by(id=id).first()
    username = userID.username
    form = TransferFunds()
    # Logs and counters
    logs_dict = {}
    transaction_logs_dict = {}
    log_count = 0
    transaction_log_count = 0
    # Recepient Logs
    recepient_logs_dict = {}
    recepient_transaction_logs_dict = {}
    recepient_log_count = 0
    recepient_transaction_log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        TransactionLogsDatabase = shelve.open('website/databases/TransactionLogs/transactionlogs.db', 'c')
        TransactionCounter = shelve.open('website/databases/TransactionLogs/transactionlogscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

        if str(current_user.id) in TransactionLogsDatabase:
            transaction_logs_dict = TransactionLogsDatabase[str(current_user.id)]
        else:
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict

        if str(current_user.id) in TransactionCounter:
            transaction_log_count = TransactionCounter[str(current_user.id)]
        else:
            TransactionCounter[str(current_user.id)] = transaction_log_count

        if str(id) in LogsDatabase:
            recepient_logs_dict = LogsDatabase[str(id)]
        else:
            LogsDatabase[str(id)] = recepient_logs_dict

        if str(id) in LogsCounter:
            recepient_log_count = LogsCounter[str(id)]
        else:
            LogsCounter[str(id)] = recepient_log_count

        if str(id) in TransactionLogsDatabase:
            recepient_transaction_logs_dict = TransactionLogsDatabase[str(id)]
        else:
            TransactionLogsDatabase[str(id)] = recepient_transaction_logs_dict

        if str(id) in TransactionCounter:
            recepient_transaction_log_count = TransactionCounter[str(id)]
        else:
            TransactionCounter[str(id)] = recepient_transaction_log_count
    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    if request.method == 'POST':
        if form.validate_on_submit():
            currentuserID = User.query.filter_by(id=current_user.id).first()
            userID.budget += form.transfer.data
            currentuserID.budget -= form.transfer.data
            db.session.commit()
            flash("Amount transferred successfully", category='success')
            log_count += 1
            transaction_log_count += 1
            recepient_log_count += 1
            recepient_transaction_log_count += 1
            log = Logs(
                id=str(log_count),
                log_description=f'${form.transfer.data} was transferred to {userID.username}',
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            transaction_log = TransactionLogs(
                id=str(transaction_log_count),
                log_description=f'${form.transfer.data} was transferred to {userID.username}',
                transaction=(form.transfer.data) * -1,
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            recepient_log = Logs(
                id=str(recepient_log_count),
                log_description=f'{current_user.username} transferred ${form.transfer.data} to your account',
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            recepient_transaction_log = TransactionLogs(
                id=str(recepient_transaction_log_count),
                log_description=f'{current_user.username} transferred ${form.transfer.data} to your account',
                transaction=form.transfer.data,
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            # upate current user dict and counter
            logs_dict[str(log_count)] = log
            transaction_logs_dict[str(transaction_log_count)] = transaction_log
            # update recepient dict and counter
            recepient_logs_dict[str(recepient_log_count)] = recepient_log
            recepient_transaction_logs_dict[str(recepient_transaction_log_count)] = recepient_transaction_log

            # Logs Database
            LogsDatabase[str(current_user.id)] = logs_dict
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict
            LogsDatabase[str(id)] = recepient_logs_dict
            TransactionLogsDatabase[str(id)] = recepient_transaction_logs_dict
            # Counters
            LogsCounter[str(current_user.id)] = log_count
            TransactionCounter[str(current_user.id)] = transaction_log_count
            LogsCounter[str(id)] = recepient_log_count
            TransactionCounter[str(id)] = recepient_transaction_log_count
            LogsDatabase.close()
            TransactionLogsDatabase.close()
            LogsCounter.close()
            TransactionCounter.close()
        return render_template('transferUserFunds.html', form=form, username=username)

    if request.method == 'GET':
        return render_template('transferUserFunds.html', form=form, username=username)


@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    db.create_all()
    form = DepositForm()
    logs_dict = {}
    transaction_logs_dict = {}
    log_count = 0
    transaction_log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        TransactionLogsDatabase = shelve.open('website/databases/TransactionLogs/transactionlogs.db', 'c')
        TransactionCounter = shelve.open('website/databases/TransactionLogs/transactionlogscount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
        else:
            LogsDatabase[str(current_user.id)] = logs_dict

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
        else:
            LogsCounter[str(current_user.id)] = log_count

        if str(current_user.id) in TransactionLogsDatabase:
            transaction_logs_dict = TransactionLogsDatabase[str(current_user.id)]
        else:
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict

        if str(current_user.id) in TransactionCounter:
            transaction_log_count = TransactionCounter[str(current_user.id)]
        else:
            TransactionCounter[str(current_user.id)] = transaction_log_count
    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    if request.method == 'POST':
        if form.validate_on_submit() and current_user.can_deposit(form.budget.data):
            userID = User.query.filter_by(id=current_user.id).first()
            userID.budget += form.budget.data
            db.session.commit()
            flash("Amount added successfully", category='success')
            # Tracking Log & Transaction Section
            log_count += 1
            transaction_log_count += 1
            log = Logs(
                id=str(log_count),
                log_description=f'${form.budget.data} was deposited into your account',
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            transaction_log = TransactionLogs(
                id=str(transaction_log_count),
                log_description=f'${form.budget.data} was deposited into your account',
                transaction=form.budget.data,
                date_recorded=datetime.now().strftime("%d/%m/%y"),
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
            )
            logs_dict[str(log_count)] = log
            transaction_logs_dict[str(transaction_log_count)] = transaction_log
            # Logs Database
            LogsDatabase[str(current_user.id)] = logs_dict
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict
            # Counters
            LogsCounter[str(current_user.id)] = log_count
            TransactionCounter[str(current_user.id)] = transaction_log_count
            LogsDatabase.close()
            TransactionLogsDatabase.close()
            LogsCounter.close()
            TransactionCounter.close()
        else:
            flash("Cannot deposit an amount less or equal to 0!", category='danger')
        return redirect(url_for('deposit'))
    if request.method == 'GET':
        return render_template('Deposit.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    db.create_all()
    form = RegisterForm()
    if request.method == 'POST':
        password = request.form.get('password1')
        print('password: ', password)
        if form.validate_on_submit():    
                user_to_create = User(username=form.username.data,
                                        email_address=form.email_address.data,
                                        password=form.password1.data,
                                        usertype="customers")
                # 'password' = form.password1.data this is entering the hashed
                # version of the password. Check models.py,
                # @password.setter hashes the passwords
                db.session.add(user_to_create)
                db.session.commit()
                login_user(user_to_create)
                flash(f"Success! You are logged in as: {user_to_create.username}", category='success')

                return redirect(url_for('home_page'))
        if form.errors != {}:  # If there are not errors from the validations
            errors = []
            for err_msg in form.errors.values():
                errors.append(err_msg)
            err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
            flash(f'{err_message}', category='danger')

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    # to log out the current logged in user
    # the category for flash will decide the color of the flashed message
    # for instance 'info' is blue, 'danger' is red, 'success' is green.
    return redirect(url_for("landing_page"))
    # flash("You have been logged out!", category='info')
    # redirects user to login page after they are logged out.


@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    add_notes_form = Add_Notes()
    notes_database = shelve.open('website/databases/Notes/note.db', 'c')
    user_notes = {}

    try:
        if str(current_user.id) not in notes_database:
            notes_database[str(current_user.id)] = user_notes
        else:
            user_notes = notes_database[str(current_user.id)]
    except IOError:
        flash("An Error Has Occurred Trying to Read The Database", category="error")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}")
    else:
        if request.method == "POST":
            new_note = Notes(id=str(uuid4()),
                             title=add_notes_form.title.data,
                             description=add_notes_form.description.data,
                             time_added=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
                             time_updated=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"))
            user_notes[new_note.get_id()] = new_note
            notes_database[str(current_user.id)] = user_notes
            notes_database.close()
            flash("New Note Added", category='success')
            print(user_notes)
            # for i in user_notes:
            #     print(f"{user_notes[i].get_id()}")
            # return redirect(url_for("notes"))
    return render_template("notes.html", form=add_notes_form, user_notes=user_notes)


@app.route("/deleteNotes", methods=["GET", "POST"])
@login_required
def deleteNotes():
    if request.method == "POST":
        notes_database = shelve.open('website/databases/Notes/note.db', 'w')
        user_notes = {}
        try:
            if str(current_user.id) not in notes_database:
                notes_database[str(current_user.id)] = user_notes
            else:
                user_notes = notes_database[str(current_user.id)]
        except KeyError:
            flash("No such note.", category="error")
        except Exception as e:
            flash(f"An Unknown Error has occurred, {e}")
        else:
            del user_notes[str(request.form.get('uuid'))]
            notes_database[str(current_user.id)] = user_notes
            notes_database.close()
            flash("Note Deleted", category='success')
    return redirect(url_for("notes"))


@app.route('/updateNotes', methods=["GET", "POST"])
@login_required
def updateNotes():
    if request.method == 'POST':
        update_notes_form = Update_Notes()
        notes_database = shelve.open('website/databases/Notes/note.db', 'w')
        user_notes = {}
        try:
            if str(current_user.id) not in notes_database:
                notes_database[str(current_user.id)] = user_notes
            else:
                user_notes = notes_database[str(current_user.id)]
        except KeyError:
            flash("No such note.", category="danger")
        except Exception as e:
            flash(f"An Unknown Error has occurred, {e}", category="danger")
        else:
            current_note = user_notes[str(request.form.get('uuid'))]
            current_note.set_title(request.form.get('title'))
            current_note.set_description(request.form.get('description'))
            current_note.set_time_updated(datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"))
            notes_database[str(current_user.id)] = user_notes
            flash('Note Updated', category='success')
            notes_database.close()
        return redirect(url_for("notes"))


# mervyn
@app.route('/landing', methods=["GET", "POST"])
def landing_page():
    admin_user()

    db.create_all()
    # warning very funny error when logging in if passwords are not hashed(check SQlite) it will crash
    # giving an error of Invalid salt Value error
    form = LoginForm()
    if form.validate_on_submit():
        # if user exist and if password is correct
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            if attempted_user.account_availability(attempted_user.status) == "sven":
                return redirect(url_for('home_page'))
            elif attempted_user.account_availability(attempted_user.status) != 0:
                # checks username for valid user and checks if password is correct
                login_user(attempted_user)
                # 'login_user' is a built-in function for flask_login
                flash(f"Success! You are logged in as: {attempted_user.username}", category='success')
                if current_user.usertype == "retailers":
                    return redirect(url_for('retail_homepage'))
                else:
                    return redirect(url_for('home_page'))
            else:
                flash(f"{attempted_user.username} account has been disabled!"
                      f" Please contact Customer Support for more information.", category='danger')
        else:
            flash("Username or Password are not matched! Please try again.", category='danger')

    return render_template('Landingbase.html', form=form)


@app.route('/about_us', methods=['GET', 'POST'])
def about_us_page():
    return render_template('aboutUs.html')


@app.route('/dashboard')
@login_required
def dashboard_page():
    Owned_Items_Dict = {}
    logs_dict = {}
    transaction_logs_dict = {}
    log_count = 0
    transaction_log_count = 0
    sales_dict = {}
    sales_log_count = 0
    try:
        LogsDatabase = shelve.open('website/databases/Logs/logs.db', 'c')
        LogsCounter = shelve.open('website/databases/Logs/logscount.db', 'c')
        TransactionLogsDatabase = shelve.open('website/databases/TransactionLogs/transactionlogs.db', 'c')
        TransactionCounter = shelve.open('website/databases/TransactionLogs/transactionlogscount.db', 'c')
        SalesLogDatabase = shelve.open('website/databases/SalesLogs/sales.db', 'c')
        SalesCounter = shelve.open('website/databases/SalesLogs/salescount.db', 'c')
        if str(current_user.id) in LogsDatabase:
            logs_dict = LogsDatabase[str(current_user.id)]
            LogsDatabase.close()
        else:
            LogsDatabase[str(current_user.id)] = logs_dict
            LogsDatabase.close()

        if str(current_user.id) in LogsCounter:
            log_count = LogsCounter[str(current_user.id)]
            LogsCounter.close()
        else:
            LogsCounter[str(current_user.id)] = log_count
            LogsCounter.close()

        if str(current_user.id) in TransactionLogsDatabase:
            transaction_logs_dict = TransactionLogsDatabase[str(current_user.id)]
            TransactionLogsDatabase.close()
        else:
            TransactionLogsDatabase[str(current_user.id)] = transaction_logs_dict
            TransactionLogsDatabase.close()

        if str(current_user.id) in TransactionCounter:
            transaction_log_count = TransactionCounter[str(current_user.id)]
            TransactionCounter.close()

        else:
            TransactionCounter[str(current_user.id)] = transaction_log_count
            TransactionCounter.close()

        if str(current_user.id) in SalesLogDatabase:
            sales_dict = SalesLogDatabase[str(current_user.id)]
            SalesLogDatabase.close()
        else:
            SalesLogDatabase[str(current_user.id)] = sales_dict
            SalesLogDatabase.close()
        if str(current_user.id) in SalesCounter:
            sales_log_count = SalesCounter[str(current_user.id)]
            SalesCounter.close()
        else:
            SalesCounter[str(current_user.id)] = sales_log_count
            SalesCounter.close()
        if str(current_user.id) in SalesCounter:
            sales_log_count = SalesCounter[str(current_user.id)]
            SalesCounter.close()
        else:
            SalesCounter[str(current_user.id)] = sales_log_count
            SalesCounter.close()
    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    try:
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'r')
        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            Owned_Items_Database.close()
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
            Owned_Items_Database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")
    with shelve.open('visitor_count') as db:
        if 'visitors' not in db:
            db['visitors'] = 0
        db['visitors'] += 1
    with shelve.open('visitor_count') as db:
        visitor_count = db['visitors']
    return render_template('dashboard.html', owned_items=Owned_Items_Dict, logs=logs_dict,
                           transaction_logs=transaction_logs_dict, sales_logs=sales_dict, visitor_count=visitor_count)


@app.route('/data/spending-profit-balance')
def budget_data():
    balance = '{0:.2f}'.format(current_user.budget)
    spending = '{0:.2f}'.format(current_user.spending)
    profit = '{0:.2f}'.format(current_user.profits)
    budget_data = {"Balance": balance, "Spending": spending, "Profit": profit}
    return jsonify(budget_data)


# @app.route('/charts')
# @login_required
# def charts_page():
#     return render_template('charts.html')


@app.route('/forgot_password', methods=["GET", 'POST'])
def forgot_password_page():
    if request.method == "GET":
        form = password_reset()
        return render_template('forgot_password.html', form=form)

    form = password_reset()
    if request.method == 'POST':
        if User.query.filter_by(email_address=form.email_address.data).first():
            user_to_reset = User.query.filter_by(email_address=form.email_address.data).first()
            otp = {}
            otp = user_to_reset.password_otp()

            db_otp = shelve.open('website/databases/otp/otp.db', 'c')
            try:
                db_otp['otp'] = otp
                db_otp.close()
            except Exception as e:
                print(f'{e} error has occurred! Database will close!')
                db_otp.close()
                return redirect(url_for('forgot_password_page'))

            user_email = {}
            user_email = form.email_address.data

            db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
            try:
                db_tempemail['email'] = user_email
                db_tempemail.close()
            except Exception as e:
                print(f'{e} error has occurred! Database will close!')
                db_tempemail.close()
                return redirect(url_for('forgot_password_page'))

            msg = Message('agegracefully Password Reset', sender='agegracefullybothelper@gmail.com',
                        recipients=[form.email_address.data])
            msg.body = f"Dear valued customer, \n\n We have received a request to reset the password for your account. In order to reset your password, please enter the following one-time password (OTP) when prompted: \n\n OTP:  {otp} \n\n Please note that this OTP will only be valid for the next 15 minutes. If you did not request a password reset, you can safely ignore this email. \n\n Thank you for choosing our service. \n\n Sincerely, \n\n Agegracefully"
            mail.send(msg)
            flash('Successfully sent! Please check your inbox for a one time password.', category='success')

            return redirect(url_for('forgot_password_page_otp'))
        else:
            flash('Email does not exist!', category='danger')
            return render_template('forgot_password.html', form=form)
    else:
        return render_template('forgot_password.html', form=form)


# Do need to add in routing validation where you cannot directly access the route
@app.route('/forgot_password/otp', methods=['GET', 'POST'])
def forgot_password_page_otp():
    form = password_reset()

    if request.method == 'POST':
        db_otp = shelve.open('website/databases/otp/otp.db', 'c')
        while True:
            try:
                check_otp = db_otp['otp']
                if check_otp == form.otp.data:

                    db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
                    user_email = db_tempemail['email']
                    db_tempemail.close()

                    user_to_reset = User.query.filter_by(email_address=user_email).first()
                    otp = {}
                    otp = user_to_reset.scramble_otp()
                    db_otp['otp'] = otp
                    db_otp.close()
                    print(f'OTP Scrambled! OTP now is, {otp}')

                    flash('Otp Successful! Please enter your new password.', category="success")
                    return redirect(url_for('password_reset_page'))
                else:
                    flash('Incorrect OTP!', category='danger')
                    return render_template('forgot_password_otp.html', form=form)
            except Exception as e:
                print(f'{e} error has occurred! Database will now close.')
                db_otp.close()
                return redirect(url_for('forgot_password_page'))
    else:
        return render_template('forgot_password_otp.html', form=form)


@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset_page():
    form = password_reset()

    if request.method == "POST":
        password = request.form.get('new_password')
        db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
        if db_tempemail['email'] is not None:
            try:
                email_variable = db_tempemail['email']

                user_to_reset = User.query.filter_by(email_address=email_variable).first()
                user_to_reset.password_hash = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                db.session.commit()
                flash("Password Changed Successfully!", category="success")

                db_tempemail['email'] = None
                db_tempemail.close()

                return redirect(url_for('landing_page'))

            except Exception as e:
                print(f'{e} error has occurred! Database will now close.')
                db_tempemail.close()
                return redirect(url_for('forgot_password_page'))
            else:
                flash('NYP{cr4zy_nyp_H4xx0r!1}', category='danger')
                db_tempemail.close()
                return redirect(url_for('forgot_password_page'))
    else:
        return render_template('reset_password.html', form=form)


@app.route('/warranty/create', methods=['GET', 'POST'])
@login_required
def create_warranty():
    from website.models import warranty
    from website.forms import CreatewarrantyForm

    form = CreatewarrantyForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            create_warranty_form = CreatewarrantyForm()

            warranty_dict = {}
            warranty_db = shelve.open('website/databases/warranty/warranty.db', 'c')
            warranty_id_db = shelve.open('website/databases/warranty/warranty_id_db', 'c')
            id = 0

            try:
                try:
                    # if company data in database,
                    warranty_dict = warranty_db['warranty']
                except Exception as e:
                    print(f"An unknown error, \"{e}\" has occured!")

                if "ID" in warranty_id_db:
                    id = warranty_id_db["ID"]

                else:
                    warranty_id_db['ID'] = id
                time_recorded=datetime.now().strftime("%I:%M:%S %p")
                warranty_recorded=datetime.now()
                
                currentyear= warranty_recorded.year + 1
                currentmonth = warranty_recorded.month
                currentday = warranty_recorded.day
                date_recorded=f"{currentday}/{currentmonth}/{currentyear}"
                warranty = warranty(id, create_warranty_form.company.data, create_warranty_form.remarks.data,
                                      create_warranty_form.email.data, create_warranty_form.phone.data, create_warranty_form.UUID.data, create_warranty_form.Address.data,create_warranty_form.PostalCode.data, date_recorded, time_recorded, warranty_recorded)

                id += 1
                warranty.set_warranty_id(id)
                warranty_dict[warranty.get_warranty_id()] = warranty
                warranty_db['warranty'] = warranty_dict
                warranty_id_db['ID'] = id
                warranty_db.close()

            except Exception as e:
                flash(f"{e} error occurred!", category='danger')
                warranty_db.close()

        return redirect(url_for('warranty_view'))
    return render_template("Createwarranty.html", form=form)


@app.route('/warrantyedit/<int:id>', methods=['GET', 'POST'])
@login_required
def update_warranty(id):
    form = UpdatewarrantyForm()

    if request.method == "POST" and form.validate_on_submit():

        warranty_dict = {}
        warranty_db = shelve.open('website/databases/warranty/warranty.db', 'c')
        warranty_dict = warranty_db["warranty"]

        for key in warranty_dict:
            print(warranty_dict[key])

        warranty = warranty_dict.get(id)
        warranty.set_warranty_name(form.company.data)
        warranty.set_warranty_remarks(form.remarks.data)
        warranty.set_email(form.email.data)
        warranty.set_phone_number(form.phone.data)

        warranty_db['warranty'] = warranty_dict
        warranty_db.close()

        return redirect(url_for('warranty_page'))
    else:
        warranty_dict = {}
        warranty_db = shelve.open('website/databases/warranty/warranty.db', 'c')
        warranty_dict = warranty_db['warranty']
        warranty_db.close()

        warranty = warranty_dict.get(id)
        form.company.data = warranty.get_warranty_name()
        form.remarks.data = warranty.get_warranty_remarks()
        form.email.data = warranty.get_email()
        form.phone.data = warranty.get_phone_number()
        
    if form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])


    return render_template('updatewarranty.html', form=form)

@app.route('/delivery', methods=['GET', 'POST'])
@login_required
def delivery():

    return render_template('delivery.html')
@app.route('/progress/<int:id>', methods=['GET', 'POST'])

@login_required
def progress():

    return render_template('progress.html')
#stuff for progress in warranty
status_db = shelve.open("website/databases/warranty/status.db", writeback=True)
if not "status" in status_db:
    status_db["status"] = {"btn1": True, "btn2": False, "btn3": False, "result": "Pending..."}

@app.route("/get_status", methods=["GET"])
def get_status():
    return status_db["status"]

@app.route("/update_status", methods=["POST"])
def update_status():
    status = status_db["status"]
    id = request.json["id"]
    if id == "btn1":
        status["btn1"] = False
        status["btn2"] = True
        status["result"] = "Your Item has been packed"
    elif id == "btn2":
        status["btn2"] = False
        status["btn3"] = True
        status["result"] = "Your Item is on the way"
    elif id == "btn3":
        status["btn1"] = False
        status["btn2"] = False
        status["btn3"] = False
        status["result"] = "You have accepted the delivery"
    status_db.sync()
    return "OK"


@app.route("/reset_status", methods=["POST"])
def reset_status():
    status = status_db["status"]
    status["btn1"] = True
    status["btn2"] = False
    status["btn3"] = False
    status["result"] = ""
    status_db.sync()
    return "OK"
#end stuff for progress in warranty
@app.route('/warranty/delete/<int:id>', methods=['POST'])
@login_required
def warranty_delete(id):
    try:
        warranty_dict = {}
        warranty_db = shelve.open('website/databases/warranty/warranty.db', 'w')
        warranty_dict = warranty_db['warranty']

        current_id = warranty_dict.get(id)
        warranty_dict.pop(id)
        warranty_db['warranty'] = warranty_dict

        if current_id not in warranty_db['warranty']:
            flash("Deletion Successful!", category="success")
        else:
            flash("Deletion unsuccessful!", category='danger')

        warranty_db.close()

    except IOError:
        flash("Something went wrong with the database!", category='danger')

    return redirect(url_for('warranty_page'))


@app.route('/warranty')
@login_required
def warranty_page():
    warranty_dict = {}
    try:
        warranty_db = shelve.open('website/databases/warranty/warranty.db', 'r')
        warranty_dict = warranty_db['warranty']
        warranty_db.close()
    except IOError:
        print("Failed to read file")
    except Exception as e:
        print(f"An unknown error has occurred, {e}")

    warranty_list = []
    users = User.query.all()
    for key in warranty_dict:
        
        warranty = warranty_dict.get(key)
        warranty_list.append(warranty)
        
        print("Warranty: ", users)

    return render_template('warranty.html', count=len(warranty_list), warranty_list=warranty_list, users=users)


@app.route('/user_management')
@login_required
def user_management():
    users = User.query.all()
    return render_template('User_Management.html', users=users)


@app.route('/user_management/update/<int:id>', methods=['POST', 'GET'])
@login_required
def user_management_update(id):
    userID = User.query.filter_by(id=id).first()
    form = Update_User_Admin()

    if request.method == 'POST' and form.validate_on_submit:
        # NOTE THAT FORM DOES NOT VALIDATE ON SUBMIT!
        # Also note that below does not work
        userID.username = form.username.data
        userID.email_address = form.email_address.data
        db.session.commit()
        flash("User's Particulars updated to database successfully!", category="success")
    else:
        flash("Some error occurred!", category="danger")

    if request.method == 'GET':
        return render_template('Update_User_Management.html', form=form, user=userID)

    flash(form.errors, category="danger")
    return redirect(url_for('user_management'))


@app.route('/user_management/enable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def user_management_enable(id):
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Enabled'
    flash(f"{userID.username} account has been enabled", category='success')
    db.session.commit()
    return redirect(url_for('user_management'))


@app.route('/user_management/disable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def user_management_disable(id):
    # The problem is this, where I cannot find the ID.
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Disabled'
    flash(f'{userID.username} account has been disabled', category='danger')
    db.session.commit()
    return redirect(url_for('user_management'))


# Sven
@app.route('/Events', methods=['GET', 'POST'])
@login_required
def Events_Page():
    Event_Form = Add_Event()
    event_database = shelve.open('website/databases/Events/event.db', 'c')
    event_dict = {}

    try:
        if "EventInfo" not in event_database:
            event_database["EventInfo"] = event_dict
        else:
            event_dict = event_database["EventInfo"]
    except IOError:
        flash("An Error Has Occurred Trying to Read The Database", category="error")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}")
    else:
        if request.method == "POST":
            new_event = Events(
                id=str(uuid4()),
                description=Event_Form.description.data,
                title=Event_Form.title.data,
                date_added=datetime.now().strftime("%d/%m/%y"),
                time_added=datetime.now().strftime("%I:%M:%S:%p"),
                updated_date=datetime.now().strftime("%d/%m/%y"),
                updated_time=datetime.now().strftime("%I:%M:%S:%p")
            )
            event_dict[new_event.get_id()] = new_event
            event_database["EventInfo"] = event_dict
            event_database.close()
            flash("New Event Added", category='success')

    return render_template('events.html', form=Event_Form, events=event_dict)


@app.route("/deleteEvents", methods=["GET", "POST"])
@login_required
def deleteEvents():
    event_database = shelve.open('website/databases/Events/event.db', 'w')
    event_dict = {}
    try:
        if "EventInfo" not in event_database:
            event_database["EventInfo"] = event_dict
        else:
            event_dict = event_database["EventInfo"]
    except KeyError:
        flash("No such note.", category="error")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}")
    else:
        print("event dictionary")
        print(event_dict)
        del event_dict[str(request.form.get('uuid'))]
        event_database["EventInfo"] = event_dict
        event_database.close()
        flash("Event Deleted", category="success")
    return redirect(url_for("Events_Page"))


@app.route('/updateEvents', methods=["GET", "POST"])
@login_required
def updateEvents():
    # update_events_form = Update_Events()
    event_database = shelve.open('website/databases/Events/event.db', 'w')
    event_dict = {}
    try:
        if "EventInfo" not in event_database:
            event_database["EventInfo"] = event_dict
        else:
            event_dict = event_database["EventInfo"]
    except KeyError:
        flash("No such note.", category="danger")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}", category="danger")
    else:
        current_event = event_dict[str(request.form.get('uuid'))]
        current_event.set_title(request.form.get('title'))
        current_event.set_description(request.form.get('description'))
        current_event.set_updated_date(datetime.now().strftime("%d/%m/%y "))
        current_event.set_updated_time(datetime.now().strftime("%I:%M:%S:%p"))
        event_database["EventInfo"] = event_dict
        flash('Event Updated', category='success')
        event_database.close()
    return redirect(url_for("Events_Page"))


@app.route('/Current_Events', methods=['GET', 'POST'])
@login_required
def Current_Events_Page():
    event_database = shelve.open('website/databases/Events/event.db', 'c')
    event_dict = {}

    try:
        if "EventInfo" not in event_database:
            event_database["EventInfo"] = event_dict
        else:
            event_dict = event_database["EventInfo"]
    except IOError:
        flash("An Error Has Occurred Trying to Read The Database", category="error")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}")

    return render_template('currentevents.html', events=event_dict)


# Sven
@app.route('/tickets', methods=['GET', 'POST'])
@login_required
def ticket_page():
    ticket_form = Ticket_Form()
    tickets = {}
    count = 0
    ticket_history = {}
    # ticket_history_count = 0
    try:
        ticket_database = shelve.open('website/databases/Ticket/ticket.db', 'c')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'c')
        ticket_history_database = shelve.open('website/databases/Ticket_History/ticket_history.db', 'c')
        # ticket_history_database_uniqueID = shelve.open('website/databases/Ticket_History/ticket_history_uniqueID.db',
        #                                                'c')
        if 'TicketInfo' in ticket_database:
            tickets = ticket_database['TicketInfo']
        else:
            ticket_database['TicketInfo'] = tickets

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

        if str(current_user.id) in ticket_history_database:
            ticket_history = ticket_history_database[str(current_user.id)]
        else:
            ticket_history_database[str(current_user.id)] = ticket_history

        # if str(current_user.id) in ticket_history_database_uniqueID:
        #     ticket_history_count = ticket_history_database_uniqueID[str(current_user.id)]
        # else:
        #     ticket_history_database_uniqueID[str(current_user.id)] = ticket_history_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    if request.method == 'POST':
        count += 1
        # ticket_history_count+=1
        ticket = Tickets(
            id=str(count),
            description=ticket_form.description.data,
            title=ticket_form.title.data,
            urgency=ticket_form.urgency.data,
            time_added=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
            owner=current_user.username,
            owner_id=current_user.id,
            pending='Pending'
        )
        # Main Ticket Database section(for admins)
        tickets[str(count)] = ticket
        ticket_database['TicketInfo'] = tickets
        ticket_database_uniqueID['ID'] = count
        ticket_database.close()
        ticket_database_uniqueID.close()
        # Ticket History Portion
        ticket_history[str(count)] = ticket
        ticket_history_database[str(current_user.id)] = ticket_history
        # ticket_history_database_uniqueID[str(current_user.id)] = ticket_history_count
        ticket_history_database.close()
        # ticket_history_database_uniqueID.close()

        flash("Ticket Sent Successfully", category='success')

    return render_template('ticket.html', form=ticket_form)


@app.route('/ticket_requests', methods=['GET', 'POST'])
@login_required
def ticket_requests_page():
    ticket_reply_form = Ticket_Reply_Form()
    tickets = {}
    count = 0
    try:
        ticket_database = shelve.open('website/databases/Ticket/ticket.db', 'r')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'r')
        if 'TicketInfo' in ticket_database:
            tickets = ticket_database['TicketInfo']
        else:
            ticket_database['TicketInfo'] = tickets

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    return render_template('ticketRequest.html', tickets=tickets, ticker_response=ticket_reply_form)


@app.route('/ticket_history', methods=['GET', 'POST'])
@login_required
def ticket_history():
    count = 0
    ticket_history = {}
    try:
        ticket_history_database = shelve.open('website/databases/Ticket_History/ticket_history.db', 'c')
        # ticket_history_database_uniqueID = shelve.open('website/databases/Ticket_History/ticket_history_uniqueID.db',
        #                                                'c')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'c')
        if str(current_user.id) in ticket_history_database:
            ticket_history = ticket_history_database[str(current_user.id)]
        else:
            ticket_history_database[str(current_user.id)] = ticket_history

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

        # if str(current_user.id) in ticket_history_database_uniqueID:
        #     ticket_history_count = ticket_history_database_uniqueID[str(current_user.id)]
        # else:
        #     ticket_history_database_uniqueID[str(current_user.id)] = ticket_history_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    return render_template('TicketHistory.html', tickets=ticket_history)


@app.route('/delete_ticket_history/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_ticket_history(id):
    count = 0
    ticket_history = {}
    try:
        ticket_history_database = shelve.open('website/databases/Ticket_History/ticket_history.db', 'c')
        # ticket_history_database_uniqueID = shelve.open('website/databases/Ticket_History/ticket_history_uniqueID.db',
        #                                                'c')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'c')
        if str(current_user.id) in ticket_history_database:
            ticket_history = ticket_history_database[str(current_user.id)]
        else:
            ticket_history_database[str(current_user.id)] = ticket_history

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

        # if str(current_user.id) in ticket_history_database_uniqueID:
        #     ticket_history_count = ticket_history_database_uniqueID[str(current_user.id)]
        # else:
        #     ticket_history_database_uniqueID[str(current_user.id)] = ticket_history_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    else:
        del ticket_history[str(id)]
        ticket_history_database[str(current_user.id)] = ticket_history
        flash('Ticket Deleted', category='success')
        ticket_history_database.close()
        ticket_database_uniqueID.close()
    return redirect(url_for("ticket_history"))


@app.route('/Booking', methods=['GET', 'POST'])
@login_required
def Booking_Page():
    form = Booking_form()
    booking_database = shelve.open('website/databases/Bookings/Booking.db', 'c')
    booking_database_uniqueID = shelve.open('website/databases/Bookings/Booking_uniqueID.db', 'c')
    bookings_dict = {}
    count = 0
    try:
        if str(current_user.id) in booking_database:
            bookings_dict = booking_database[str(current_user.id)]
        else:
            booking_database[str(current_user.id)] = bookings_dict

        if str(current_user.id) in booking_database_uniqueID:
            count = booking_database_uniqueID[str(current_user.id)]
        else:
            booking_database_uniqueID[str(current_user.id)] = count

    except IOError:
        flash("An Error Has Occurred Trying to Read The Database", category="error")
    except Exception as e:
        flash(f"An Unknown Error has occurred, {e}")
    else:
        if request.method == 'POST':
            count += 1
            booking = Booking(
                id=count,
                description=form.reason.data,
                time_added=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
                time_updated=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
                date=form.date.data,
                timeslot=form.time.data
            )
            bookings_dict[count] = booking
            booking_database[str(current_user.id)] = bookings_dict
            booking_database_uniqueID[str(current_user.id)] = count
            booking_database.close()
            booking_database_uniqueID.close()
            print(bookings_dict)
            flash("Booking Made Successfully", category='success')

    return render_template("Booking.html", form=form)


@app.route('/delete_ticket/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_ticket_request(id):
    tickets = {}
    count = 0
    try:
        ticket_database = shelve.open('website/databases/Ticket/ticket.db', 'w')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'w')
        if 'TicketInfo' in ticket_database:
            tickets = ticket_database['TicketInfo']
        else:
            ticket_database['TicketInfo'] = tickets

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    else:
        del tickets[str(id)]
        ticket_database['TicketInfo'] = tickets
        flash('Ticket Deleted', category='success')
        ticket_database.close()
        ticket_database_uniqueID.close()
    return redirect(url_for("ticket_requests_page"))


@app.route('/ticket_reply/<int:id>', methods=['GET', 'POST'])
@login_required
def ticket_reply(id):
    ticket_reply_form = Ticket_Reply_Form()
    tickets = {}
    tickets_response_dict = {}
    count = 0
    response_count = 0
    userID = User.query.filter_by(id=id).first()
    ticket_history = {}
    # ticket_history_count = 0
    try:
        ticket_database = shelve.open('website/databases/Ticket/ticket.db', 'w')
        ticket_database_uniqueID = shelve.open('website/databases/Ticket/ticket_uniqueID.db', 'w')
        ticket_response_database = shelve.open('website/databases/Messages/messages.db', 'c')
        ticket_response_uniqueID = shelve.open('website/databases/Messages/messages_uniqueID', 'c')
        ticket_history_database = shelve.open('website/databases/Ticket_History/ticket_history.db', 'c')
        # ticket_history_database_uniqueID = shelve.open('website/databases/Ticket_History/ticket_history_uniqueID.db',
        #                                                'c')
        # Ticket History(For owner of ticket) database
        if str(id) in ticket_history_database:
            ticket_history = ticket_history_database[str(id)]
        else:
            ticket_history_database[str(id)] = ticket_history

        # if str(id) in ticket_history_database_uniqueID:
        #     ticket_history_count = ticket_history_database_uniqueID[str(id)]
        # else:
        #     ticket_history_database_uniqueID[str(current_user.id)] = ticket_history_count

        # Ticket Response Database
        if str(id) in ticket_response_database:
            tickets_response_dict = ticket_response_database[str(id)]
        else:
            ticket_response_database[str(id)] = tickets_response_dict

        if str(id) in ticket_response_uniqueID:
            response_count = ticket_response_uniqueID[str(id)]
        else:
            ticket_response_uniqueID[str(id)] = response_count

        # TicketInfo Database
        if 'TicketInfo' in ticket_database:
            tickets = ticket_database['TicketInfo']
        else:
            ticket_database['TicketInfo'] = tickets

        if 'ID' in ticket_database_uniqueID:
            count = ticket_database_uniqueID['ID']
        else:
            ticket_database_uniqueID['ID'] = count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    else:
        if request.method == 'POST':
            if userID:
                response_count += 1
                ticket_response = Tickets_Response(
                    id=str(response_count),
                    description=ticket_reply_form.description.data,
                    title=ticket_reply_form.title.data,
                    time_added=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
                    owner=current_user.username,
                    status=ticket_reply_form.issue_status.data,
                    recipient=userID.username
                )
                tickets[str(request.form.get('uuid'))].set_pending_status(ticket_reply_form.issue_status.data)
                if str(request.form.get('uuid')) in ticket_history:
                    ticket_history[str(request.form.get('uuid'))].set_pending_status(
                        ticket_reply_form.issue_status.data)
                tickets_response_dict[str(response_count)] = ticket_response

                ticket_response_database[str(id)] = tickets_response_dict
                ticket_response_uniqueID[str(id)] = response_count
                # Fix Set Pending Status issue in morning pls
                ticket_response_database.close()
                ticket_response_uniqueID.close()
                print(tickets)
                ticket_database['TicketInfo'] = tickets
                ticket_database.close()
                ticket_database_uniqueID.close()
                # Ticket History Database
                ticket_history_database[str(id)] = ticket_history
                ticket_history_database.close()
                flash(f"Ticket Response Sent Successfully to {userID.username}", category='success')
                userID.messages = len(tickets_response_dict)
            else:
                flash("User does not exist, user may have disabled or deleted his/her account", category='danger')

            db.session.commit()
    return redirect(url_for('ticket_requests_page'))


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages_page():
    userID = User.query.filter_by(id=current_user.id).first()
    tickets_response_dict = {}
    response_count = 0
    try:
        ticket_database = shelve.open('website/databases/Messages/messages.db', 'w')
        ticket_database_uniqueID = shelve.open('website/databases/Messages/messages_uniqueID', 'w')
        # Ticket Response Database
        if str(current_user.id) in ticket_database:
            tickets_response_dict = ticket_database[str(current_user.id)]
            ticket_database.close()
        else:
            ticket_database[str(current_user.id)] = tickets_response_dict
            ticket_database.close()

        if str(current_user.id) in ticket_database_uniqueID:
            response_count = ticket_database_uniqueID[str(current_user.id)]
            ticket_database_uniqueID.close()
        else:
            ticket_database_uniqueID[str(current_user.id)] = response_count
            ticket_database_uniqueID.close()

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    userID.messages = len(tickets_response_dict)
    db.session.commit()
    print(tickets_response_dict)
    print(response_count)

    return render_template('messages.html', tickets_response=tickets_response_dict)


@app.route('/delete_messages/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_messages_page(id):
    userID = User.query.filter_by(id=current_user.id).first()
    tickets_response_dict = {}
    response_count = 0

    try:
        ticket_response_database = shelve.open('website/databases/Messages/messages.db', 'c')
        ticket_response_uniqueID = shelve.open('website/databases/Messages/messages_uniqueID', 'c')

        # Ticket Response Database
        if str(current_user.id) in ticket_response_database:
            tickets_response_dict = ticket_response_database[str(current_user.id)]
        else:
            ticket_response_database[str(current_user.id)] = tickets_response_dict

        if str(current_user.id) in ticket_response_uniqueID:
            response_count = ticket_response_uniqueID[str(current_user.id)]
        else:
            ticket_response_uniqueID[str(current_user.id)] = response_count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    else:
        del (tickets_response_dict[str(id)])
        ticket_response_database[str(current_user.id)] = tickets_response_dict
        ticket_response_database.close()
        ticket_response_uniqueID.close()
        userID.messages = len(tickets_response_dict)
        flash("Message Deleted", category='success')

    return redirect(url_for('messages_page'))


@app.route('/Feedback_Form', methods=['GET', 'POST'])
@login_required
def Feedback_Page():
    feedback_form = Feedback_form()
    feedback_dict = {}
    feedback_database = shelve.open('website/databases/Feedbacks/Feedback.db', 'c')
    # feedback_database_uniqueID = shelve.open('website/databases/Feedbacks/Feedback_uniqueID.db', 'c')
    try:
        if 'feedbackinfo' in feedback_database:
            feedback_dict = feedback_database['feedbackinfo']
        else:
            feedback_database['feedbackinfo'] = feedback_dict

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")

    if request.method == 'POST':
        id = uuid4()
        feedback = Feedback(
            id=str(id),
            description=feedback_form.description.data,
            time_added=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
            time_updated=datetime.now().strftime("%d/%m/%y %I:%M:%S:%p"),
            rating=int(request.form.get('rate')),
            favourite=feedback_form.favourite.data,
            least_favourite=feedback_form.least_favourite.data,
            improvement=feedback_form.improvement.data,
            title=feedback_form.title.data,
            sender=current_user.username,
            sender_id=current_user.id
        )
        feedback_dict[str(id)] = feedback
        feedback_database['feedbackinfo'] = feedback_dict
        feedback_database.close()
        print("Feedback Dictionary")
        print(feedback_dict)
        flash("Feedback Submitted, Thank you very much!", category='success')

    return render_template("feedbackform.html", form=feedback_form)


@app.route('/Feedback_Page', methods=['GET', 'POST'])
@login_required
def Feedbacks():
    feedback_dict = {}
    star_sum = 0
    try:
        feedback_database = shelve.open('website/databases/Feedbacks/Feedback.db', 'r')
        # feedback_database_uniqueID = shelve.open('website/databases/Feedbacks/Feedback_uniqueID.db', 'r')
        if 'feedbackinfo' in feedback_database:
            feedback_dict = feedback_database['feedbackinfo']
            feedback_database.close()
        else:
            feedback_database['feedbackinfo'] = feedback_dict
            feedback_database.close()

        # if 'feedbackinfo_ID' in feedback_database:
        #     count = feedback_database_uniqueID['feedbackinfo_ID']
        #     feedback_database_uniqueID.close()
        # else:
        #     feedback_database_uniqueID['feedbackinfo_ID'] = count
        #     feedback_database_uniqueID.close()
    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    for i in feedback_dict:
        star_sum += feedback_dict[i].get_rating()

    if star_sum > 0:
        star_average = round(star_sum / len(feedback_dict))
    else:
        star_average = 0

    return render_template('feedback.html', feedback_dict=feedback_dict, star_average=star_average)


@app.route('/delete_feedback', methods=['GET', 'POST'])
@login_required
def delete_feedback():
    feedback_database = shelve.open('website/databases/Feedbacks/Feedback.db', 'w')
    # feedback_database_uniqueID = shelve.open('website/databases/Feedbacks/Feedback_uniqueID.db', 'w')
    feedback_dict = {}
    # count = 0
    try:
        if 'feedbackinfo' in feedback_database:
            feedback_dict = feedback_database['feedbackinfo']
        else:
            feedback_database['feedbackinfo'] = feedback_dict

        # if 'feedbackinfo_ID' in feedback_database:
        #     count = feedback_database_uniqueID['feedbackinfo_ID']
        # else:
        #     feedback_database_uniqueID['feedbackinfo_ID'] = count

    except IOError:
        print("An Error Has Occurred Trying to Read The Database")
    except Exception as e:
        print(f"An Unknown Error has occurred, {e}")
    else:
        if request.method == 'POST':
            del feedback_dict[str(request.form.get('uuid'))]
            feedback_database['feedbackinfo'] = feedback_dict
            feedback_database.close()
            # feedback_database_uniqueID.close()
            flash('Feedback deleted successfully!', category='success')

    return redirect(url_for('Feedbacks'))



@app.route('/warrantyview')
@login_required
def warranty_view():
    warranty_dict = {}
    
    try:
        warranty_db = shelve.open('website/databases/warranty/warranty.db', 'r')
        warranty_dict = warranty_db['warranty']
        warranty_db.close()
    except IOError:
        print("Failed to read file")
    except Exception as e:
        print(f"An unknown error has occurred, {e}")

    warranty_list = []
    users = User.query.all()
    for key in warranty_dict:
        
        warranty = warranty_dict.get(key)
        warranty_list.append(warranty)
        print("Warranty: ", users)

    return render_template('warranty5.html', count=len(warranty_list), warranty_list=warranty_list, users=users)
#for dexter

    

@app.route('/retail')
@login_required
def retail_homepage():
    userID = User.query.filter_by(id=current_user.id).first()
    admin_user()
    return render_template('retail.html', user=userID)


@app.route('/retail/retail_profile')
@login_required
def retail_profile():
    Owned_Items_Dict = {}

    Wish_Dict = {}
    Items_Dict = {}
    Products = {}
    try:
        Item_Database = shelve.open('website/databases/items/items.db', 'r')
        Wish_Database = shelve.open('website/databases/wishlist/wishlist.db', 'r')

        if str(current_user.id) in Wish_Database:
            Wish_Dict = Wish_Database[str(current_user.id)]
            Wish_Database.close()
        else:
            Wish_Database[str(current_user.id)] = Wish_Dict
            Wish_Database.close()
        if 'ItemInfo' in Item_Database:
            Items_Dict = Item_Database['ItemInfo']
            Item_Database.close()
        else:
            Item_Database['ItemInfo'] = Items_Dict
            Item_Database.close()

    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    try:
        products_database = shelve.open('website/databases/products/products.db', 'r')
        if str(current_user.id) in products_database:
            Products = products_database[str(current_user.id)]
            products_database.close()

        else:
            products_database[str(current_user.id)] = Products
            products_database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")

    try:
        Owned_Items_Database = shelve.open('website/databases/Owned_Items/ownedItems.db', 'r')
        if str(current_user.id) in Owned_Items_Database:
            Owned_Items_Dict = Owned_Items_Database[str(current_user.id)]
            Owned_Items_Database.close()
        else:
            Owned_Items_Database[str(current_user.id)] = Owned_Items_Dict
            Owned_Items_Database.close()
    except IOError:
        print("Unable to Read File")

    except Exception as e:
        print(f"An unknown error has occurred,{e}")


    Selling_Items = []
    print(Items_Dict)



    for i in Items_Dict:
        Item = Items_Dict.get(i)
        if Item.get_owner_id() == current_user.id:
            print('hello')
            Selling_Items.append(Item)

    update_username_form = Update_Username()
    update_email_form = Update_Email()
    update_gender_form = Update_Gender()
    update_password_form = Update_Password()
    update_retailer_form = UpdateRetailerForm
    if update_username_form.validate_on_submit:
        pass
    if update_username_form.errors != {}:  # If there are not errors from the validations
        errors = []
        for err_msg in update_username_form.errors.values():
            errors.append(err_msg)
        err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
        flash(f'{err_message}', category='danger')

    return render_template('retail_profile.html', username_form=update_username_form, email_form=update_email_form,
                           gender_form=update_gender_form, retailer_form=update_retailer_form, password_form=update_password_form,
                           owned_items=Owned_Items_Dict, wished_items=Wish_Dict, selling_items=len(Selling_Items),
                           products=Products)





@app.route('/retailers/retail_database')
@login_required
def retrieve_retailers():
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/retailer/retailer.db', 'r')
    retailer_dict = retailer_db["Retailers"]

    for key in retailer_dict:
        print(retailer_dict[key])

    
    print(retailer_dict)

    retailer_db.close()

    retailers_list = []
    #location_list = []
    retailersid_list = []
    users = User.query.all()
    
    for user in users:
        retailersid_list.append(user.retailer_id)
    print("retailersid_list: ", retailersid_list)
    
   

    for key in retailer_dict:
        retail = retailer_dict.get(key)
        #retail_location = retail.get_map_url()
        #location_list.append(retail_location)
        retailers_list.append(retail)

    return render_template('retail_database.html', count=len(retailers_list), retailers_list=retailers_list, retailersid_list=retailersid_list, users=users)

@app.route('/retailers/create', methods=['GET', 'POST'])
def create_retailer():
    from website.models import Retail
    from website.forms import RegisterRetailerForm

    form = RegisterRetailerForm()
   
    
    if request.method == 'POST':
        if form.validate_on_submit():
            register_retailer_form = RegisterRetailerForm()

            retailer_dict = {}
            retailer_db = shelve.open('website/databases/retailer/retailer.db', 'c')
            retailer_id_db = shelve.open('website/databases/retailer/retailer_id_db', 'c')
            location_db = shelve.open('website/databases/retailer/location.db', 'c')
            id = 0
            try:
                try:
                    retailer_dict = retailer_db['Retailers']
                except Exception as e:
                    print(f"An unknown error, \"{e}\" has occured!")

                if "ID" in retailer_id_db:
                    id = retailer_id_db["ID"]

                else:
                    retailer_id_db['ID'] = id

                current_time = datetime.now()

                retailer = Retail(id, register_retailer_form.company_id.data, register_retailer_form.shop.data, register_retailer_form.postal_code.data,
                                      register_retailer_form.unit_number.data, register_retailer_form.address.data,
                                      register_retailer_form.office_no.data, register_retailer_form.email_address.data, 
                                      current_time.year)#, register_retailer_form.location.data)   

                id += 1
                retailer.set_retailer_id(id)
                retailer_dict[retailer.get_retailer_id()] = retailer
                retailer_db['Retailers'] = retailer_dict
                retailer_id_db['ID'] = id
                retailer_db.close()
                flash(f"Submitted record successfully", category='success')

            except Exception as e:
                flash(f"{e} error occurred!", category='danger')
                retailer_db.close()
            
        return redirect(url_for('landing_page'))
    return render_template("registerRetail.html", form=form)

@app.route('/retailersedit/<int:id>', methods=['POST'])
@login_required
def update_retailer(id):
    form = UpdateRetailerForm()

    if request.method == "POST" and form.validate_on_submit():

        retailer_dict = {}
        retailer_db = shelve.open('website/databases/retailer/retailer.db', 'c')
        retailer_dict = retailer_db["Retailers"]
        retailer = retailer_dict.get(id)
        print("retailer: ", retailer)
        retailer.set_company_id(form.company_id.data)
        retailer.set_location(form.shop.data)
        retailer.set_email_address(form.email_address.data)
        retailer.set_postal_code(form.postal_code.data)
        retailer.set_office_no(form.office_no.data)
        retailer.set_unit_number(form.unit_number.data)
        retailer.set_address(form.address.data)

        retailer_db['Retailers'] = retailer_dict
        retailer_db.close()

        return redirect(url_for('retrieve_retailers'))
    else:
        retailer_dict = {}
        retailer_db = shelve.open('website/databases/retailer/retailer.db', 'c')
        retailer_dict = retailer_db['Retailers']
        retailer_db.close()
        retailer = retailer_dict.get(id)
        print("retailer: ", retailer)
        form.company_id.data = retailer.get_company_id()
        form.shop.data = retailer.get_location()
        form.postal_code.data = retailer.get_postal_code()
        form.unit_number.data = retailer.get_unit_number()
        form.address.data = retailer.get_address()
        form.email_address.data = retailer.get_email_address()
        form.office_no.data = retailer.get_office_no()
        
        if form.errors != {}:  # If there are not errors from the validations
            errors = []
            for err_msg in form.errors.values():
                errors.append(err_msg)
            err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
            flash(f'{err_message}', category='danger')


        return render_template('updateRetailer.html', form=form)


@app.route('/retailers/delete/<int:id>', methods=['POST'])
@login_required
def retailer_delete(id):
    try:
        retailer_dict = {}
        retailer_db = shelve.open('website/databases/retailer/retailer.db', 'w')
        retailer_dict = retailer_db['Retailers']

        current_id = retailer_dict.get(id)
        retailer_dict.pop(id)
        retailer_db['Retailers'] = retailer_dict

        if current_id not in retailer_db['Retailers']:
            flash("Deletion Successful!", category="success")
        else:
            flash("Deletion unsuccessful!", category='danger')

        retailer_db.close()

    except IOError:
        flash("Something went wrong with the database!", category='danger')

    # except Exception as e:
    #     flash(f"{e} went wrongly!")

    return redirect(url_for('retrieve_retailers'))




@app.route('/retail/retail_management')
@login_required
def retail_management():
    users = User.query.all()
    print("Retailers: ", users)
    return render_template('RetailAccount_Management.html', users=users)


@app.route('/registerRetailAccount/<int:id>', methods=['GET', 'POST'])
@login_required
def register_retail_account(id):
    form = RegisterRetailAccountForm()
    retailer = ''
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/retailer/retailer.db', 'w')
    retailer_dict = retailer_db["Retailers"]
   
    retailer = retailer_dict.get(id)
    current_id = retailer.get_retailer_id()
    print(current_id)
   
    if request.method == 'POST' and form.validate_on_submit():
        password = request.form.get('password1')
        print('password: ', password)
    
        user_to_create = User(username=form.username.data,
                            retailer_id = retailer.get_retailer_id(),
                            email_address=retailer.get_email_address(),
                            password=form.password1.data,
                            usertype="retailers")
        db.session.add(user_to_create)
        db.session.commit()
        
        user_email = {}
        user_email = retailer.get_email_address()
        print(user_email)

        if form.errors != {}:  # If there are not errors from the validations
            errors = []
            for err_msg in form.errors.values():
                errors.append(err_msg)
            err_message = '<br/>'.join([f'({number}){error[0]}' for number, error in enumerate(errors, start=1)])
            flash(f'{err_message}', category='danger')

        db_tempemail = shelve.open('website/databases/tempemail/tempemail.db', 'c')
        try:
            db_tempemail['email'] = user_email
            db_tempemail.close()
        except Exception as e:
            print(f'{e} error has occurred! Database will close!')
            db_tempemail.close()
            return redirect(url_for('register_retail_account', id=current_id))

        msg = Message('Login credentials for retail account creation', sender='agegracefullybothelper@gmail.com',
                        recipients=[retailer.get_email_address()])
        msg.body = f"Dear valued retailer, \n\n We have received a request to create a retail account for you. Your login credentials are: \nUsername: {form.username.data} \nPassword: {form.password1.data} \nPlease do not respond back to this message as this is just a bot account."
        mail.send(msg)
        
        flash(f"Success! Account {user_to_create.username} created!", category='success')

        return redirect(url_for('landing_page'))

    return render_template('registerRetailAccount.html', form=form, retailer=retailer)


@app.route('/retail/retail_management/update/<int:id>', methods=['POST', 'GET'])
@login_required
def retail_management_update(id):
    form = Update_Retailer_Account()
    userID = User.query.filter_by(id=id).first()

    if request.method == 'POST' and form.validate_on_submit():
        # NOTE THAT FORM DOES NOT VALIDATE ON SUBMIT!
        # Also note that below does not work
        userID.username = form.username.data
        userID.email_address = form.email_address.data
        db.session.commit()
        flash("User's Particulars updated to database successfully!", category="success")
    else:
        flash("Some error occurred!", category="danger")

    if request.method == 'GET':
        return render_template('update_retail_management.html', form=form, user=userID)

    flash(form.errors, category="danger")
    return redirect(url_for("retail_management"))

@app.route('/retail/retail_management/enable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def retail_management_enable(id):
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Enabled'
    flash(f"{userID.username} account has been enabled", category='success')
    db.session.commit()
    return redirect(url_for('retail_management'))


@app.route('/retail/retail_management/disable/<int:id>', methods=['POST'])
@login_required
# Inheritance
def retail_management_disable(id):
    userID = User.query.filter_by(id=id).first()
    userID.status = 'Disabled'
    flash(f'{userID.username} account has been disabled', category='danger')
    db.session.commit()
    return redirect(url_for('retail_management'))

@app.route('/retail/retail_management/retail_info/<int:id>', methods=['GET'])
@login_required
def retail_information(id):
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/retailer/retailer.db', 'w')
    retailer_dict = retailer_db["Retailers"]

    current_retail = retailer_dict.get(id-7)
    print(current_retail)
    retailer_db.close()

    return render_template("retail_information.html", current_retail=current_retail, retail_id=id)



  
@app.route('/location')
@login_required
def location():
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/retailer/retailer.db', 'r')
    location_db = shelve.open('website/databases/retailer/location.db', 'c')
    retailer_dict = retailer_db['Retailers']
    location_dict = location_db['Location']
    location_list=[]
    for key in retailer_dict:
        retail = retailer_dict.get(key)
        retail_location = retail.get_map_url()
        location_list.append(retail_location)

    return render_template('retailerlocation.html', location_list=location_list)

@app.route("/locationadd")
@login_required
def location_add(id):
    retailer_dict = {}
    retailer_db = shelve.open('website/databases/retailer/retailer.db', 'r')
    location_db = shelve.open('website/databases/retailer/location.db', 'w')
    location_dict = {}
    location_list = []
    try:
        location_dict = location_db['Location']
    except Exception as e:
        flash(f"An unknown error, \"{e}\" has occured!", category="danger")

    retailer = retailer_dict.get(id)
    current_id = retailer.get_retailer_id()

    print(current_id)
    location = retailer.get_map_url() 
    current_location = Location(current_id, location)
    #current_id += 1
    location_dict[current_id] = current_location
    location_db['Location'] = location_dict
    location_db.close()    
    flash("Location URL added to database!", category="success")
    return redirect(url_for('location'))


    
@app.route('/locationedit')
@login_required
def location_edit():
    return render_template('locationeditor.html')

@app.route('/404')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404
@app.route('/legal')
def legal():
    return render_template('legal.html')
@app.route('/contact')
def contact_us():
    return render_template('contact.html')
@app.route('/service')
def service_help():
    return render_template('service.html')
@app.route('/articles')
def articles():
    return render_template('articles.html')
@app.route('/payment')
@login_required
def payment_page():
    return render_template('payment.html')
@app.route('/thankyou')
@login_required
def thankyou_page():
    return render_template('thank.html')

@app.route('/deals')
@login_required
def deals_page():
    return render_template('deals.html')

@app.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')


@app.route('/updatingwarranty')
@login_required
def updats():
    return render_template('warranty2.html')

@app.route('/adminwarranty')
@login_required
def updatewarranty():
    return render_template('warranty3.html')

@app.route('/deletewarranty')
def deletewarranty():
    return render_template('warranty4.html')

@app.route('/Place')
def Place_Page():
    return render_template('benefits.html')

@app.route('/')
@app.route('/index')
def index_page():
    return render_template('index_page.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')



@app.route('/blog', methods=['GET', 'POST'])
def blog():
    db = shelve.open('blog.db')
    blogs = db.get('blogs', [])
    if request.method == 'POST':
        if request.form.get('blog'):
            blogs.append({
                'text': request.form['blog'],
                'comments': []
            })
        elif request.form.get('comment'):
            blog_id = int(request.form['blog_id'])
            blogs[blog_id - 1]['comments'].append(request.form['comment'])
        db['blogs'] = blogs
    db.close()
    return render_template('blog.html', blogs=blogs)

@app.route('/like', methods=['POST'])
def like():
    # Open the like.db shelve file
    db = shelve.open('like.db', 'c')
    
    # Get the blog id and like count
    blog_id = request.form['blog_id']
    likes = db.get(blog_id, 0)
    
    # Increment the like count
    likes += 1
    
    # Store the updated like count in the like.db file
    db[blog_id] = likes
    
    # Close the like.db file
    db.close()
    return str(likes)