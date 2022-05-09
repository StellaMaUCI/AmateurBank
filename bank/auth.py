import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from bank.db import get_db

# creates a Blueprint named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
# Don't import anything here from account.py because it will cause circular import

bp = Blueprint('auth', __name__, url_prefix='/auth')  # jinja2.exceptions.TemplateNotFound: ../base.html


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
    print("step0")
    # request.method = 'POST'
    print(request.method)
    success_registration = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        initial_amount = request.form['initial_amount']
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
        elif not initial_amount:
            error = 'Initial amount is required.'
        elif not (phone.isnumeric() or len(phone) == 0):  # Phone number should be numbers only
            error = 'Phone number should be numbers only.'
        elif len(username) > 127:
            error = 'Username is too long, max 127.'
        elif len(password) > 127:
            error = 'Password is too long, max 127.'
        elif not verify_amount_format(initial_amount):
            error = 'Initial_amount should be numbers only.'
        elif not verify_username_format(username):
            error = 'Username restricted to underscores, hyphens, dots, digits, and lowercase alphabetical characters.'
        elif not verify_password_format(password):
            error = 'Password restricted to underscores, hyphens, dots, digits, and lowercase alphabetical characters.'
        print("step0.2")
        print("error = ", error)
        if error is None:
            try:
                print("step1.0")
                db.execute(  # SQL resolution scope choose 项目名称
                    'INSERT INTO user (username, password, firstname, lastname, initial_amount, phone) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (username, generate_password_hash(password), firstname, lastname, initial_amount, phone),
                )  # Hashes the password for security
                db.commit()
                error = f"User \"{username}\" is successfully registered, please login"
                print("step1.1")
                success_registration = True
            except db.IntegrityError:  # sqlite3.IntegrityError will occur if the username exists
                print("step1.48")
                error = f"User \"{username}\" is already registered, please enter another username"
        # else:  # url_for() generates the URL for the login view based on its name
        #     # redirect() generates a redirect response to the generated URL
        #     print("step1.5")
        #     #return redirect(url_for("auth.login"))
        #     return redirect(url_for("auth.register"))
        print("step1.9")
        flash(error)
    print("before render_template auth/register.html")
    if success_registration:
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


#    return render_template("auth/login.html")


# The Second View: Login(same pattern as register)
@bp.route('/login', methods=('GET', 'POST'))
def login():  # 此处应为小写
    print("step2.0")
    print("request.method = ", request.method)
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
        # 登录页面不显示，因为缺少get module
    if request.method == 'GET':
        username = session.get('username', None)

        if username:
            query = 'SELECT id from user WHERE username="' + username + '"'
            db = get_db()
            user_id = db.execute(query).fetchone()

            if user_id['id']:
                session['user_id'] = user_id['id']
                return redirect(url_for('index'))
    return render_template('auth/login.html')


# Log out
# you need to remove the user id from the session.
# Then load_logged_in_user won’t load a user on subsequent requests.

@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))


def verify_amount_format(amount):
    """
* matches the previous token between zero and unlimited times, as many times as possible, giving back as needed (greedy)
. matches any character (except for line terminators)
{2} matches the previous token exactly 2 times
？matches the previous token 0 or 1 time
    """
    pattern = re.compile('(0|[1-9][0-9]*)(\\.[0-9]{2})?')
    match = pattern.fullmatch(amount)
    if match is None:
        return False
    else:
        return True


def verify_username_format(username):
    """
  + matches the previous token between 1 and unlimited times, as many times as possible, giving back as needed (greedy)
  . matches any character (except for line terminators)
  _ matches the character _ with index 9510 (5F16 or 1378)
  \\-\\ matches a single character in the range between \ (index 92) and \ (index 92) (case sensitive)
      """
    pattern = re.compile('[_\\-\\.0-9a-z]+')
    match = pattern.fullmatch(username)
    if match is None:
        return False
    else:
        return True


def verify_password_format(password):
    pattern = re.compile('[_\\-\\.0-9a-z]+')
    match = pattern.fullmatch(password)
    if match is None:
        return False
    else:
        return True