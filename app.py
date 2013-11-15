from flask import Flask, request, session, g, render_template, redirect, url_for
import MySQLdb as sql

app = Flask(__name__)
app.config.from_object('config.db')
app.config.from_object('config.app')


app.config["DEBUG"] = True

def connect_db():
    return sql.connect(host=app.config["HOST"], db=app.config["DATABASE"], user=app.config["USERNAME"], passwd=app.config["PASSWORD"])  


@app.before_request
def before_request():
    g.db = connect_db()
    g.user = session['username'] if 'username' in session else False

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
       db.close()

@app.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return render_template("example.html", rows=rows, user=g.user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['email']
        return redirect(url_for('index'))
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run()
