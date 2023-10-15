import os
import secrets
from PIL import Image
from functools import wraps
from datetime import datetime,date, time
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import render_template,redirect, url_for, flash,session,request,g, current_app
from flaskshow import app,db,bcrypt , user_login_manager, admin_login_manager
from flaskshow.models import Admin, Event, Venue, Ticket, Buyer
from flask_login import login_user, logout_user, login_required, current_user, login_manager
from flaskshow.forms import BuyerRegistrationForm, AdminRegistrationForm, BuyerLoginForm,AdminLoginForm, VenueForm, EventForm, DeleteVenueForm, EditVenueForm, BuyTicketForm

csrf = CSRFProtect(app)


def generate_csrf():
    return secrets.token_hex(16)

def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Buyer) or not current_user.is_buyer():
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

def user_role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return abort(401)  # Unauthorized
        return func(*args, **kwargs)
    return decorated_view

@app.route('/')
def home():
    events = Event.query.all()
    return render_template('home.html', events=events)     
@app.route("/user")
@user_login_required
def user_dashboard():
    events = Event.query.all()
    return render_template('user_dashboard.html', events=events)

@app.route("/admin")
@admin_login_required
def admin_dashboard():
    venues = Venue.query.all()
    events = Event.query.all()
    return render_template("admin_dashboard.html", venues=venues,events=events)    


@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    form = BuyerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        buyer = Buyer(name=form.name.data, email=form.email.data, password=hashed_password,phone=form.phone.data, tickets_purchased=[])
        db.session.add(buyer)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_signup.html', form=form)


@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        admin = Admin(username=form.username.data, email=form.email.data, password=hashed_password, venue_id=form.venue_id.data)
        db.session.add(admin)
        db.session.commit()
        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for('admin_login'))
    return render_template('admin_signup.html', form=form)


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    form = BuyerLoginForm()
    if form.validate_on_submit():
        buyer = Buyer.query.filter_by(email=form.email.data).first()
        if buyer and bcrypt.check_password_hash(buyer.password, form.password.data):
            login_user(buyer)
            session['buyer_id'] = buyer.id  # store buyer id in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('user_login.html', form=form)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_admin(admin)
            session['admin_id'] = admin.id  # store admin id in session
            flash('You have been logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('admin_login.html', form=form)

@app.route('/admin/add_venue', methods=['GET', 'POST'])
@admin_login_required
def add_venue():
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(name=form.name.data,address=form.address.data, capacity=form.capacity.data,id=form.venue_id.data )
        db.session.add(venue)
        db.session.commit()
        flash('The venue has been added.', 'success')
        return redirect(url_for('venues_list'))
    return render_template('add_venue.html', form=form)

@app.route('/admin/add_show', methods=['GET', 'POST'])
@admin_login_required
def add_show():
    form = EventForm()
    form.venue.choices = [(v.id, v.name) for v in Venue.query.all()]
    if form.validate_on_submit():
        start_time_str = form.start_time.data
        end_time_str = form.end_time.data
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')
        image_file = None
        if form.image.data:
            image_file = save_picture(form.image.data)
        event = Event(
            name=form.name.data,start_time=start_time,end_time=end_time,image=image_file,venue_id=form.venue.data,ticket_price=form.ticket_price.data)
        db.session.add(event)
        db.session.commit()
        flash('Your show has been added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_show.html', title='Add Show', form=form)


@app.route('/venues_list')
def venues_list():
    venues = Venue.query.all()
    return render_template('venues_list.html', venues=venues)


@app.route('/shows_list')
def shows_list():
    events = Event.query.all()
    return render_template('shows_list.html', events=events)

@app.route('/admin/edit_venue/<int:venue_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = EditVenueForm()
    if form.validate_on_submit():
        venue.name = form.name.data
        venue.address = form.address.data
        venue.capacity = form.capacity.data
        db.session.commit()
        flash('The venue has been updated.', 'success')
        return redirect(url_for('venues_list'))
    elif request.method == 'GET':
        form.name.data = venue.name
        form.address.data = venue.address
        form.capacity.data = venue.capacity
    return render_template('edit_venue.html', form=form, venue=venue)

@app.route('/admin/delete_venue/<int:venue_id>', methods=['GET', 'POST'])
@admin_login_required
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = DeleteVenueForm()
    if form.validate_on_submit():
        db.session.delete(venue)
        db.session.commit()
        flash('The venue has been deleted.', 'success')
        return redirect(url_for('venues_list'))
    form.csrf_token.data = generate_csrf()
    return render_template('delete_venue.html', venue=venue, form=form)





@app.route('/admin/edit_show/<int:event_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_show(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    form.venue.choices = [(v.id, v.name) for v in Venue.query.all()]
    if form.validate_on_submit():
        start_time = datetime.strptime(form.start_time.data, '%H:%M')
        end_time = datetime.strptime(form.end_time.data, '%H:%M')
        event.name = form.name.data
        event.start_time = start_time
        event.end_time = end_time
        event.venue_id = form.venue.data
        if form.image.data:
            event.image_file = save_picture(form.image.data)
        db.session.commit()
        flash('Your changes have been saved!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_show.html', title='Edit Show', form=form, event=event, venues=Venue.query.all())


@app.route('/admin/delete_show/<int:event_id>', methods=['GET', 'POST'])
@admin_login_required
def delete_show(event_id):
    event = Event.query.get_or_404(event_id)
    print(event)
    form = EventForm()
    if form.validate_on_submit():
        db.session.delete(event)
        db.session.commit()
        flash('The event has been deleted.', 'success')
        return redirect(url_for('shows_list'))
    form.csrf_token.data = generate_csrf()
    print(form.csrf_token.data)    
    return render_template('delete_show.html', event=event, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/event_images', picture_fn)
    output_size = (500, 500)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_fn

@app.route('/buy_ticket/<int:event_id>', methods=['GET', 'POST'])
@user_login_required
def buy_ticket(event_id):
    form = BuyTicketForm()
    event = Event.query.get(event_id)
    buyer = Buyer.query.get(session['buyer_id'])
    ticket = Ticket(
        event_id=event.id,
        price=event.ticket_price,
        quantity=form.quantity.data
    )
    if form.validate_on_submit():
        buyer.tickets_purchased.append(ticket)
        db.session.add(buyer)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket purchased successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('buy_ticket.html', event=event, form=form, ticket=ticket)

@app.route('/search', methods=['GET'])
@user_login_required
def search_results():
    query = request.args.get('query')
    venues = Venue.query.filter(Venue.address.like('%{}%'.format(query))).all()
    events = Event.query.filter(Event.name.like('%{}%'.format(query))).all()
    return render_template('search_results.html', query=query, venues=venues, events=events)





 

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


