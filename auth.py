import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from AmateurBank.db import get_db

# creates a Blueprint named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


# The First View: Register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not firstname:
            error = 'Firstname is required.'
        elif not lastname:
            error = 'Firstname is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user "
                    "(username, password, firstname, lastname, phone) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (username, generate_password_hash(password), firstname, lastname, phone),
                )
                db.commit()
            except db.IntegrityError:  # sqlite3.IntegrityError will occur if the username exists
                error = f"User {username} is already registered."
            else:  # url_for() generates the URL for the login view based on its name
                # redirect() generates a redirect response to the generated URL
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


# The Second View: Login(same pattern as register)
@bp.route('/register', methods=('GET', 'POST'))
def Login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()  # returns one row from the query.
        # If the query returned no results, it returns None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

        return render_template('auth/login.html')
