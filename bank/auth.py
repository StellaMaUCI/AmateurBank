import functools
import re
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    Response
)
from werkzeug.security import check_password_hash, generate_password_hash

from bank.db import get_db

# creates a Blueprint named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
# Don't import anything here from account.py because it will cause circular import


bp = Blueprint('auth', __name__, url_prefix='/auth')  # jinja2.exceptions.TemplateNotFound: ../base.html
query_userid = 'SELECT id FROM user WHERE username = ?'


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


# User experience is too bad, we decide to make username only registration page
@bp.route('/register-username', methods=(['GET', 'POST']))
def register_username():
    if request.method == 'POST':
        username = request.form['username']
        db = get_db()
        error = None

        if not username:
            error = 'User name is required.'
        elif len(username) > 127:
            error = 'Username is too long, max 127.'
        elif not verify_username_format(username):
            error = 'Username is not valid input.'

        # Check if this user existed
        if db.execute(query_userid, (username,)).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            session['username'] = username
            # return redirect(url_for('auth.register', username=username))
            return redirect(url_for('auth.register', username_reg=username))
        flash(error)
    return render_template('auth/register-username.html')


# The View: Register
# @bp.route('/register', methods=('GET', 'POST'))
@bp.route('/register', methods=(['GET', 'POST']))
def register():
    # username = request.args.get('username')
    username = request.args.get('username_reg')

    print('step 0', request.method)
    if request.method == 'POST':
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        initial_amount = request.form['initial_amount']
        phone = request.form['phone']
        db = get_db()
        error = None

        # Flash error in the window prompting user input
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
        elif not (phone.isnumeric() or len(phone) != 10):
            error = 'Phone number should be numbers only and 10 digits.'

        elif len(username) > 127:
            error = 'Username is too long, max 127.'
        elif len(password) > 127:
            error = 'Password is too long, max 127.'
        elif not verify_amount_format(initial_amount):
            error = 'Initial_amount should be numbers only.'
        elif not verify_username_format(username):
            error = 'Username has invalid characters.'
        elif not verify_password_format(password):
            error = 'Password has invalid characters.'

        print("error = ", error)
        if error is None:
            try:
                print("step1.0")
                # Put registration information into user table
                db.execute(  # SQL resolution scope choose 项目名称
                    'INSERT INTO user (username, password, firstname, lastname, initial_amount, phone) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                #     (username, generate_password_hash(password), firstname, lastname, initial_amount, phone),
                # )  # Hashes the password for security
                    (username, password, firstname, lastname, initial_amount, phone),
                )  # Hashes the password for security
                db.commit()

                # Put user table pertinent information to account table
                get_userid = db.execute(query_userid, (username,)).fetchone()
                user_id = get_userid['id']
                db.execute(
                    'INSERT INTO account (user_id, amount) VALUES (?, ?)',
                    (user_id, initial_amount),
                )
                db.commit()

            except db.IntegrityError:
                error = f"Sqlite3 database error"
            else:  # url_for() generates the URL for the login view based on its name

                return redirect(url_for("auth.login"))  # generates a redirect response to the generated URL
        flash(error)
        session['username'] = username
        print("before render_template auth/register.html', username=username")
    return render_template('auth/register.html', username=username)


# The View: Login(same pattern as register)
@bp.route('/login', methods=('GET', 'POST'))
def login():  # 此处应为小写
    print("request.method = ", request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # user_row = db.execute(
        #     'SELECT * FROM user WHERE username = ?', (username,)
        # ).fetchone()  # returns one row from the query.
        # if user_row is None:
        #     error = 'Username is wrong.'
        # elif not check_password_hash(user_row['password'], password):
        #     # hashes the submitted password in the same way as the stored hash and securely compares them
        #     error = 'Password is wrong.'

        # Start Bad Code (Vulnerability #2)
        bad_query = "SELECT * FROM user WHERE username = '" + username + "' and password= '" + password + "'"
        user_row = db.execute(bad_query).fetchone()
        if user_row is None:
            error = "Login failed."
        # END BAD CODE (VULNERABILITY #2)

        # if user_row is None:
        #     error = "Login failed."

        if error is None:
            session.clear()
            session['user_id'] = user_row['id']
            print("session=", session)
            return redirect(url_for('index'))
        flash(error)
    return render_template("auth/login.html")

    # 登录页面不显示，因为缺少get
    if request.method == 'GET':
        # username = session.get('username', None) or (g.user and g.user['username'])
        # if username:
        #     db = get_db()
        #     user_id = db.execute(query_userid, (username,)).fetchone()
        #
        #     if user_id is not None and user_id['id']:
        #         session['user_id'] = user_id['id']
        if g.user is not None:
            return redirect(url_for('index'))
            # If username has been in the view, redirect to index

        return render_template('auth/login.html')

        # # Start Bad Code (Vulnerability #1)
        # # source: https://rules.sonarsour.ce.com/python/RSPEC-5146
        # target = request.args.get('target')
        # if target is not None:
        #     return redirect(target)
        # # End Bad Code  (Vulnerability #1)

        whitelist = ['login', 'auth', '5000', 'localhost', ':', '/', 'register', 'user']
        target = request.args.get('target')
        if target and len(target) > 0 and (target in whitelist):
            print("target is not null and in whitelist")
            return render_template('target')
        else:
            print("target is not in whitelist, go to login page")
        return render_template('auth/login.html')


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
