from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.orm import composite

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.secret_key = 'key123'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

def __repr__(self):
    return '<User %r>' % self.username

class Address:
    def __init__(self, row1, row2, zip_code, postal):
        self.row1, self.row2, self.zip_code, self.postal = row1, row2, zip_code, postal
    
    def __composite_values__(self):
        return self.row1, self.row2, self.zip_code, self.postal

    def __eq__(self, other):
        return isinstance(other, Address) and self.__composite_values__() == other.__composite_values__()
    
    def __ne__(self,other):
        return not self.__eq__(other)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    notes = db.Column(db.String)

    invoice_row1 = db.Column(db.String)
    invoice_row2 = db.Column(db.String)
    invoice_zip_code = db.Column(db.String)
    invoice_postal = db.Column(db.String)

    visitation_row1 = db.Column(db.String)
    visitation_row2 = db.Column(db.String)
    visitation_zip_code = db.Column(db.String)
    visitation_postal = db.Column(db.String)

    invoice_address = composite(Address, invoice_row1, invoice_row2, invoice_zip_code, invoice_postal)
    visitation_address = composite(Address, visitation_row1, visitation_row2, visitation_zip_code, visitation_postal)

db.create_all()

def sample_data(db):
    u1 = User(username='niklas', password='niklas123')
    db.session.add(u1)
    db.session.commit()

    for i in range(100):
        attrs = 'name', 'phone', 'email', 'notes', 'invoice_row1', 'invoice_row2', 'invoice_zip_code', 'invoice_postal'
        c = Customer(**{v: 'Customer {} {}'.format(i, v) for v in attrs})
        db.session.add(c)
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

@app.route('/customers')
@require_login
def customers():
    page = int(request.args.get('page', 1))
    pageSize = int(request.args.get('pageSize', 15))
    filter = request.args.get('filter', None)

    q = Customer.query
    if filter:
        q = q.filter(getattr(Customer, 'name').like('%{}%'.format(filter)))
    q = q.offset((page - 1) * pageSize)
    c = q.count()
    print(c)
    customers = q.limit(pageSize)
    return render_template('customers.html', customers=customers)
    #return render_template('customers.html', customers=Customer.query.offset((page - 1) * pageSize).limit(pageSize))

@app.route('/logout')
def logout():
    session.pop('logged_in_user', None)
    return redirect(url_for('index'))

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