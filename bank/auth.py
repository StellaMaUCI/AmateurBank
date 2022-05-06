import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from bank.db import get_db

# creates a Blueprint named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed.
# The url_prefix will be prepended to all the URLs associated with the blueprint.

bp = Blueprint('auth', __name__, url_prefix='/auth') #jinja2.exceptions.TemplateNotFound: ../base.html
# bp = Blueprint('auth', __name__) # The requested URL was not found on the server

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


# The First View: Register, Validates that the username is not already taken.
# @bp.route('/register', methods=('GET', 'POST'))
@bp.route('/register', methods=(['GET', 'POST']))
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
            error = 'Lastname is required.'

        if error is None:
            try:
                db.execute(  # SQL resolution scope choose 项目名称
                    'INSERT INTO user (username, password, firstname, lastname, phone) '                  
                    'VALUES (?, ?, ?, ?, ?)',
                    (username, generate_password_hash(password), firstname, lastname, phone),
                )  # Hashes the password for security
                db.commit()
            except db.IntegrityError:  # sqlite3.IntegrityError will occur if the username exists
                error = f"User {username} is already registered."
            else:  # url_for() generates the URL for the login view based on its name
                # redirect() generates a redirect response to the generated URL
                return redirect(url_for("auth.login"))

        flash(error)
    return render_template("auth/register.html")

# The Second View: Login(same pattern as register)
@bp.route('/login', methods=('GET', 'POST'))
def login():  # 此处应为小写
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()  # returns one row from the query.
        # If the query returned no results, it returns None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            # hashes the submitted password in the same way as the stored hash and securely compares them
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            """
            session is a dict that stores data across requests. 
            When validation succeeds, the user’s id is stored in a new session. 
            The data is stored in a cookie that is sent to the browser, and the browser then sends it back with subsequent requests. 
            Flask securely signs the data so that it can’t be tampered with.
            """
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

        return render_template("auth/login.html")


# Log out
# you need to remove the user id from the session.
# Then load_logged_in_user won’t load a user on subsequent requests.

@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))

