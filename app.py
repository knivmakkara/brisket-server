from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.secret_key = 'key123'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()

def sample_data(db):
    u1 = User(username='niklas', password='niklas123')
    db.session.add(u1)
    db.session.commit()

sample_data(db)

def require_login(resource):
    @wraps(resource)
    def wrapper(*args, **kwargs):
        if not 'logged_in_user' in session:
            return redirect(url_for('login'))
        return resource(*args, **kwargs)
    return wrapper



@app.route('/')
@require_login
def index():
    return render_template('layout.html', name='Kristoffer', users=User.query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()

        if u:
            session['logged_in_user'] = u.username
            return redirect(url_for('index'))
        else:
            error = 'Felaktigt användarnamn eller lösenord'

    return render_template('login.html', error=error)








if __name__ == '__main__':
    app.run(debug=True)