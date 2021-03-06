import bcrypt
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SuPerDuberSecreTKeY!111!1!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = request.form.to_dict()
        pw_to_hash = bytes(f"{user_data['password']}", encoding='ascii')
        hashed = bcrypt.hashpw(pw_to_hash, bcrypt.gensalt())
        user = User(name=user_data['name'], email=user_data['email'], password=hashed)

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
        except IntegrityError:
            flash('That email is already registered!')
            return redirect(url_for('register'))
        return redirect(url_for('secrets'))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user is not None:
            if bcrypt.checkpw(bytes(f'{password}', encoding='ascii'), user.password):
                login_user(user)
            else:
                flash('The password you entered is incorrect.')
                return redirect(url_for('login'))
        else:
            flash('The email you entered is incorrect.')
            return redirect(url_for('login'))
    return render_template("index.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
