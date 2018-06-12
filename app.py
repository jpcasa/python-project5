from flask import Flask, g, render_template, redirect, url_for, flash
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_required, login_user,
                         logout_user, current_user)

import models
from forms import LoginForm, NewEntryForm

PORT = 8000
DEBUG = True
HOST = 'localhost'

app = Flask(__name__)
app.secret_key = 'hhbjb78a76s8dhasuybda./((*&&^$))asdasd--565849...[\]$'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or password doesn\'t match!', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You\'ve been logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password doesn\'t match!', 'error')
    return render_template('login.html', form=form)


@app.route('/new-entry', methods=('GET', 'POST'))
@login_required
def new():
    form = NewEntryForm()
    if form.validate_on_submit():
        models.Entry.create(
            title=form.title.data,
            date=form.date.data,
            timeSpent=form.timeSpent.data,
            whatILearned=form.whatILearned.data.strip(),
            resourcesToRemember=form.resourcesToRemember.data.strip(),
            tags=form.tags.data.strip(),
            user=g.user.id
        )
        flash("Entry Created! Congrats!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/detail')
@login_required
def detail():
    return render_template('detail.html')





@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out! Come back soon!', 'success')
    return redirect(url_for('login'))



if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            email='hola@jpcasabianca.com',
            password='1234567890'
        )
    except ValueError:
        pass
    app.run(port=PORT,debug=DEBUG, host=HOST)
