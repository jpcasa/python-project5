#!/usr/bin/env python3

from flask import (Flask, g, render_template, redirect,
                   url_for, flash, abort)

from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_required, login_user,
                         logout_user, current_user)
from slugify import slugify

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

        url = slugify(form.title.data)

        models.Entry.create(
            title=form.title.data,
            date=form.date.data,
            timeSpent=form.timeSpent.data,
            whatILearned=form.whatILearned.data.strip(),
            resourcesToRemember=form.resourcesToRemember.data.strip(),
            url=url,
            user=g.user.id
        )

        if form.tags.data:
            tags = current_user.separate_tags(form.tags.data)
            for tag in tags:
                tag_exists = models.Tags.select().where(
                    (models.Tags.user == g.user._get_current_object()) &
                    (models.Tags.tag == tag) &
                    (models.Tags.post_url == url)
                )
                if not tag_exists.exists():
                    models.Tags.create(
                        user=g.user._get_current_object(),
                        tag=tag,
                        post_url=url
                    )

        flash("Entry Created! Congrats!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form, post=None, action='add')


@app.route('/entries/<url>')
@login_required
def get_post(url):
    post = models.Entry.select().where(models.Entry.url == url).get()
    tags = models.Tags.select().where(
        (models.Tags.user == g.user._get_current_object()) &
        (models.Tags.post_url == post.url)
    )

    if not post:
        abort(404)
    return render_template('detail.html', post=post, tags=tags)


@app.route('/entries/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_post(id):

    form = NewEntryForm()
    tags_string = ''

    post = models.Entry.select().where(models.Entry.id == id).get()

    if not post:
        abort(404)

    if form.validate_on_submit():

        url = slugify(form.title.data)

        if form.tags.data:
            tags = current_user.separate_tags(form.tags.data)
            for tag in tags:
                tag_exists = models.Tags.select().where(
                    (models.Tags.user == g.user._get_current_object()) &
                    (models.Tags.tag == tag)
                )
                if not tag_exists.exists():
                    models.Tags.create(
                        user=g.user._get_current_object(),
                        tag=tag
                    )
                else:
                    tag_exists.get().tag = tag
                    tag_exists.get().post_url = url
                    tag_exists.get().save()

        post.title = form.title.data
        post.date = form.date.data
        post.timeSpent = form.timeSpent.data
        post.whatILearned = form.whatILearned.data
        post.resourcesToRemember = form.resourcesToRemember.data
        post.url = url
        post.save()

        flash("Entry Edited Successfully!", "success")
        return redirect(url_for('index'))

    tags = models.Tags.select().where(
        models.Tags.user == g.user._get_current_object()
    )
    for i in range(len(tags)):
        if i < (len(tags) - 1):
            tags_string += tags[i].tag + ', '
        else:
            tags_string += tags[i].tag

    form.title.data = post.title
    form.date.data = post.date
    form.timeSpent.data = post.timeSpent
    form.whatILearned.data = post.whatILearned
    form.resourcesToRemember.data = post.resourcesToRemember
    form.tags.data = tags_string

    return render_template('new.html', form=form, post=post, action='edit')



@app.route('/entries/delete/<int:id>')
@login_required
def delete_post(id):
    post = models.Entry.select().where(models.Entry.id == id).get()
    if not post:
        abort(404)
    return render_template('delete.html', post=post)


@app.route('/entries/delete/<int:id>/confirm')
@login_required
def delete_post_confirm(id):
    post = models.Entry.select().where(models.Entry.id == id).get()
    try:
        post.delete_instance()
    except models.IntegrityError:
        abort(404)
    else:
        flash("You've deleted the entry Successfully!", "success")
        return redirect(url_for('index'))


@app.route('/')
@login_required
def index():
    posts = current_user.get_posts()
    return render_template('index.html', posts=posts)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You\'ve been logged out! Come back soon!', 'success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            email='hi@teamtreehouse.com',
            password='1234567890'
        )
    except ValueError:
        pass
    app.run(port=PORT,debug=DEBUG, host=HOST)
