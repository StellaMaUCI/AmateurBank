from flask import Flask
import account
app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

app.register_blueprint(account.bp)
app.add_url_rule('/', endpoint='index')

if __name__ == '__main__':
    app.run()
