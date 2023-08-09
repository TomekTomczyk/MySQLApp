from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

import json

# Create a Flask Instance
app = Flask(__name__)

# Add SQLite Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Add MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MYSQLPassword123@localhost/mysql_users'

# Secret Key
app.config['SECRET_KEY'] = "secret key"
# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    phone_number = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    except:
        flash("User not deleted. Try again.")
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)


# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = IntegerField("Phone Number")
    submit = SubmitField("Submit")


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.phone_number = request.form['phone_number']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
        except:
            flash('User not updated. Try again.')
            return render_template('update.html',
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template('update.html',
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, phone_number=form.phone_number.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.phone_number.data = ''
        flash('User added successfully')
    our_users = Users.query.order_by(Users.date_added)
    users_count = Users.query.count()
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users,
                           users_count=users_count)


@app.route('/getNoOfRecs', methods=['GET'])
def get_no_of_recs():
    users_count = Users.query.count()
    result = json.dumps(users_count)
    return result


# Create a route decorator
@app.route('/')
def index():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"

    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff)


# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


with app.app_context():
    db.create_all()
