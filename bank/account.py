# https://flask.palletsprojects.com/en/2.1.x/tutorial/blog/

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from bank.auth import login_required
from bank.db import get_db

import re
import sys

bp = Blueprint('account', __name__)


@bp.route('/')
def index():
    db = get_db()
    pass_to_HTML_accounts = []
    if g.user is not None:
        accounts = db.execute(
            'SELECT a.id, user_id, username, amount'
            ' FROM account a JOIN user u ON a.user_id = u.id'
            ' WHERE user_id = ?', (g.user['id'],)
        ).fetchall()
        for account in accounts:
            account_instance = {}
            init_amount = account['amount']
            account_instance['amount'] = f'{init_amount:.2f}'
            account_instance['username'] = account['username']
            account_instance['id'] = account['id']
            pass_to_HTML_accounts.append(account_instance)
    return render_template('account/index.html', accounts=pass_to_HTML_accounts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        init_amount = request.form['amount']
        error = None

        if not init_amount:
            error = 'Initial amount required.'
        if verify_amount_format(init_amount) == False:
            error = 'Not a valid numeric input'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO account (amount, user_id)'
                ' VALUES (?, ?)',
                (init_amount, g.user['id'])
            )
            db.commit()
            return redirect(url_for('account.index'))

    return render_template('account/create.html')


def get_account(id, check_author=True):
    account = get_db().execute(
        'SELECT a.id, user_id, username, amount'
        ' FROM account a JOIN user u ON a.id = u.id'
        ' WHERE a.id = ?',
        (id,)
    ).fetchone()

    return account


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    account = get_account(id)

    if request.method == 'POST':
        amount = request.form['amount']
        error = None

        if not amount:
            error = 'Amount is required.'

        if not verify_amount_format(amount) == False:
            error = 'Not a valid numeric input'

        result_amount = account['amount']
        if request.form['withposit'] == "Withdraw":
            result_amount = result_amount - float(amount)
            if result_amount < 0:
                error = "Cannot withdraw more than balance"
        elif request.form['withposit'] == "Deposit":
            result_amount = result_amount + float(amount)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE account SET amount = ?'
                ' WHERE id = ?',
                (result_amount, id)
            )
            db.commit()
            return redirect(url_for('account.index'))

    return render_template('account/update.html', account=account)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_account(id)
    db = get_db()
    db.execute('DELETE FROM account WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('account.index'))


def verify_amount_format(amount):
    pattern = re.compile('(0|[1-9][0-9]*)(\\.[0-9]{2})?')
    match = pattern.fullmatch(amount)
    if match is None:
        return False
    else:
        return True
