from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.orm import composite
from forms import CustomerForm, PromemoriaForm
from method_rewrite import MethodRewriteMiddleware

import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.secret_key = 'key123'
app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)

def __repr__(self):
    return '<User %r>' % self.username

class Address:
    def __init__(self, row1, row2, zip_code, post_town):
        self.row1, self.row2, self.zip_code, self.post_town = row1, row2, zip_code, post_town
    
    def __composite_values__(self):
        return self.row1, self.row2, self.zip_code, self.post_town

    def __eq__(self, other):
        return isinstance(other, Address) and self.__composite_values__() == other.__composite_values__()
    
    def __ne__(self,other):
        return not self.__eq__(other)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    contact = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    notes = db.Column(db.String)

    invoice_row1 = db.Column(db.String)
    invoice_row2 = db.Column(db.String)
    invoice_zip_code = db.Column(db.String)
    invoice_post_town = db.Column(db.String)

    visitation_row1 = db.Column(db.String)
    visitation_row2 = db.Column(db.String)
    visitation_zip_code = db.Column(db.String)
    visitation_post_town = db.Column(db.String)

    invoice_address = composite(Address, invoice_row1, invoice_row2, invoice_zip_code, invoice_post_town)
    visitation_address = composite(Address, visitation_row1, visitation_row2, visitation_zip_code, visitation_post_town)

class Promemoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    contact = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    notes = db.Column(db.String)

    invoice_row1 = db.Column(db.String)
    invoice_row2 = db.Column(db.String)
    invoice_zip_code = db.Column(db.String)
    invoice_post_town = db.Column(db.String)

    visitation_row1 = db.Column(db.String)
    visitation_row2 = db.Column(db.String)
    visitation_zip_code = db.Column(db.String)
    visitation_post_town = db.Column(db.String)

    due = db.Column(db.DateTime)
    number_guests = db.Column(db.Integer)
    menu = db.Column(db.String)
    allergies = db.Column(db.String)
    created_by = db.Column(db.String)
    delivery_type = db.Column(db.String)
    staff = db.Column(db.String)
    rental = db.Column(db.String)
    misc = db.Column(db.String)

db.create_all()

def sample_data(db):
    u1 = User(username='niklas', password='niklas123')
    db.session.add(u1)
    db.session.commit()

    for i in range(100):
        attrs = 'name', 'contact' ,'phone', 'email', 'notes', 'invoice_row1', 'invoice_row2', 'invoice_zip_code', 'invoice_post_town', 'visitation_row1', 'visitation_row2', 'visitation_zip_code', 'visitation_post_town'
        c = Customer(**{v: 'Customer {} {}'.format(i, v) for v in attrs})
        db.session.add(c)

    for i in range(100):
        attrs = 'name', 'contact' ,'phone', 'email', 'notes', 'invoice_row1', 'invoice_row2', 'invoice_zip_code', 'invoice_post_town', 'visitation_row1', 'visitation_row2', 'visitation_zip_code', 'visitation_post_town'
        c = Promemoria(**{v: 'Customer {} {}'.format(i, v) for v in attrs})
        c.due = datetime.datetime.now() - datetime.timedelta(days=i)
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

@app.context_processor
def utility_processor():
    return dict(merge=lambda a,b: {**a, **b})

@app.template_filter('date_time')
def date_time(s):
    return s.strftime('%Y-%m-%d %H:%M')

@app.template_filter('append_class')
def append_class(d, class_name):
    d['class'] =  ' '.join(d.get('class', '').split(' ') + [class_name])
    return d


@app.route('/')
@require_login
def index():
    return render_template('dashboard.html')

@app.route('/customers/<int:id>', methods=['PATCH', 'DELETE'])
@require_login
def customer(id):
    customer = Customer.query.get(id)
    if request.method == 'DELETE':
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for('customers'))
    else:
        form = CustomerForm(request.form)
        if form.validate():
            form.populate_obj(customer)
            db.session.add(customer)
            db.session.commit()
            return redirect(url_for('customers'))
        else:
            return render_template('edit_customer.html', form=form, customer=customer)

@app.route('/customers/<int:id>/edit')
@require_login
def edit_customer(id):
    customer = Customer.query.get(id)
    form = CustomerForm(obj=customer)
    return render_template('edit_customer.html', form=form, customer=customer)

@app.route('/customers/new')
@require_login
def new_customer():
    form = CustomerForm()
    return render_template('new_customer.html', form=form)

@app.route('/pm/new')
@require_login
def new_pm():
    form = None
    if 'copy_from' in request.args:
        form = PromemoriaForm(obj=Customer.query.get(request.args['copy_from']))
    else:
        form = PromemoriaForm()

    return render_template('new_pm.html', form=form)

@app.route('/pm/<int:id>/edit')
@require_login
def edit_pm(id):
    pm = Promemoria.query.get(id)
    form = PromemoriaForm(obj=pm)
    return render_template('edit_pm.html', form=form, pm=pm)

@app.route('/pm/<int:id>', methods=['PATCH', 'DELETE'])
@require_login
def pm(id):
    pm = Promemoria.query.get(id)
    if request.method == 'DELETE':
        db.session.delete(pm)
        db.session.commit()
        return redirect(url_for('pms'))
    else:
        form = PromemoriaForm(request.form)
        if form.validate():
            form.populate_obj(pm)
            db.session.add(pm)
            db.session.commit()
            return redirect(url_for('pms'))
        else:
            return render_template('edit_pm.html', form=form, pm=pm)

@app.route('/pm', methods=['GET','POST'])
@require_login
def pms():
    if request.method == 'POST':
        form = PromemoriaForm(request.form)
        pm = Promemoria()

        if form.validate():
            form.populate_obj(pm)
            db.session.add(pm)
            db.session.commit()
            return redirect(url_for('pms'))
        else:
            return render_template('new_pm.html', form=form)
    else:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        filter = request.args.get('filter', None)
        order_by = request.args.get('order_by', None)
        order = request.args.get('order', None)
        order = order if order in ['ASC', 'DESC'] else 'ASC'

        q = Promemoria.query
        if filter:
            q = q.filter(getattr(Promemoria, 'name').like('%{}%'.format(filter)))
        count = q.count()

        if order_by:
            q = q.order_by('{} {}'.format(order_by, order))

        q = q.offset((page - 1) * page_size)
        pms = q.limit(page_size)
        total_pages = (count // page_size) + (0 if (count % page_size) == 0 else 1)
    return render_template('pms.html', pms=pms, page=page, page_size=page_size, count=count, total_pages=total_pages)

@app.route('/customers', methods=['GET','POST'])
@require_login
def customers():
    if request.method == 'POST':
        form = CustomerForm(request.form)
        customer = Customer()

        if form.validate():
            form.populate_obj(customer)
            db.session.add(customer)
            db.session.commit()
            return redirect(url_for('customers'))
        else:
            return render_template('new_customer.html', form=form)
    else:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        filter = request.args.get('filter', None)
        order_by = request.args.get('order_by', None)
        order = request.args.get('order', None)
        order = order if order in ['ASC', 'DESC'] else 'ASC'

        q = Customer.query
        if filter:
            q = q.filter(getattr(Customer, 'name').like('%{}%'.format(filter)))
        count = q.count()

        if order_by:
            q = q.order_by('{} {}'.format(order_by, order))

        q = q.offset((page - 1) * page_size)
        customers = q.limit(page_size)
        total_pages = (count // page_size) + (0 if (count % page_size) == 0 else 1)
    return render_template('customers.html', customers=customers, page=page, page_size=page_size, count=count, total_pages=total_pages)

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