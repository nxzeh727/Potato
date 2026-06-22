from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from datetime import datetime

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
import secrets
import os
from dotenv import load_dotenv
from flask_migrate import Migrate


load_dotenv()
app = Flask(__name__)
db_url = os.environ.get("DATABASE_URL", "sqlite:///project.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
db = SQLAlchemy(app)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_urlsafe(16))
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

class Users(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50),unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(255))

    def make_password(self,passowrd):
        self.password= generate_password_hash(passowrd)
    def check_password(self, passowrd):
        return check_password_hash(self.password,passowrd)
    
    tasks = db.relationship("Tasks", backref = 'user', lazy=True)

class Tasks(db.Model):

    __tablename__ = "tasks"
    id:Mapped[int] = mapped_column(primary_key=True)
    task_anme: Mapped[str] = mapped_column(String(300), nullable=False)
    priority: Mapped[str] = mapped_column()
    datedue: Mapped[datetime] = mapped_column()
    completed: Mapped[bool] = mapped_column(default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)


class SignUp(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(8,40)])
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired(), Length(10,40)])
    submit = SubmitField("submit")

class Login(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(8,40)])
    password = PasswordField("password", validators=[DataRequired(), Length(10,40)])
    submit = SubmitField("submit")

@app.route("/")
def index():
    return(render_template("index.html"))

@app.route("/signup", methods=["GET","POST"])
def signup():
    form = SignUp()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data 
        potato = Users(username = username, email=email)
        potato.make_password(password)
        db.session.add(potato)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    form = Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        potaot = Users.query(username=username).first()
        if potaot and potaot.check_password(password):
            session['username'] = potaot.username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@app.route("/home", methods=["GET","POST"])
def home():
    return render_template("home.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0")