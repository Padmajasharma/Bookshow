import os
import secrets
from PIL import Image
from functools import wraps
from datetime import datetime,date, time
from flask import jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import render_template,redirect, url_for, flash,session,request,g, current_app
from flaskshow import app,db,bcrypt , user_login_manager, admin_login_manager
from flaskshow.models import Admin, Event, Venue, Ticket, Buyer
from flask_login import login_user, logout_user, login_required, current_user, login_manager
from werkzeug.exceptions import abort
from flaskshow.forms import BuyerRegistrationForm, AdminRegistrationForm, BuyerLoginForm,AdminLoginForm, VenueForm, EventForm, DeleteVenueForm, EditVenueForm, BuyTicketForm,DeleteShowForm

csrf = CSRFProtect(app)

@app.route('/api/venues', methods=['GET'])
def get_venues():
    venues = Venue.query.all()
    serialized_venues = [{'id': v.id, 'name': v.name, 'address': v.address, 'capacity': v.capacity} for v in venues]
    return jsonify(venues=serialized_venues)

@app.route('/api/venues/<int:venue_id>', methods=['GET'])
def get_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    serialized_venue = {'id': venue.id, 'name': venue.name, 'address': venue.address, 'capacity': venue.capacity}
    return jsonify(venue=serialized_venue)

@app.route('/api/venues', methods=['POST'])
def create_venue():
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(name=form.name.data, address=form.address.data, capacity=form.capacity.data)
        db.session.add(venue)
        db.session.commit()
        return jsonify(message='Venue created successfully')
    return jsonify(errors=form.errors), 400

@app.route('/api/venues/<int:venue_id>', methods=['PUT'])
def update_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    if form.validate_on_submit():
        venue.name = form.name.data
        venue.address = form.address.data
        venue.capacity = form.capacity.data
        db.session.commit()
        return jsonify(message='Venue updated successfully')
    return jsonify(errors=form.errors), 400

@app.route('/api/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    return jsonify(message='Venue deleted successfully')


# API endpoints for shows
@app.route('/api/shows', methods=['GET'])
def get_shows():
    shows = Show.query.all()
    serialized_shows = [{'id': s.id, 'name': s.name, 'start_time': s.start_time.isoformat(),
                         'end_time': s.end_time.isoformat(), 'venue_id': s.venue_id} for s in shows]
    return jsonify(shows=serialized_shows)

@app.route('/api/shows/<int:show_id>', methods=['GET'])
def get_show(show_id):
    show = Show.query.get_or_404(show_id)
    serialized_show = {'id': show.id, 'name': show.name, 'start_time': show.start_time.isoformat(),
                       'end_time': show.end_time.isoformat(), 'venue_id': show.venue_id}
    return jsonify(show=serialized_show)

@app.route('/api/shows', methods=['POST'])
def create_show():
    form = ShowForm()
    if form.validate_on_submit():
        show = Show(name=form.name.data, start_time=form.start_time.data,
                    end_time=form.end_time.data, venue_id=form.venue_id.data)
        db.session.add(show)
        db.session.commit()
        return jsonify(message='Show created successfully')
    return jsonify(errors=form.errors), 400

@app.route('/api/shows/<int:show_id>', methods=['PUT'])
def update_show(show_id):
    show = Show.query.get_or_404(show_id)
    form = ShowForm(obj=show)
    if form.validate_on_submit():
        show.name = form.name.data
        show.start_time = form.start_time.data
        show.end_time = form.end_time.data
        show.venue_id = form.venue_id.data
        db.session.commit()
        return jsonify(message='Show updated successfully')
    return jsonify(errors=form.errors), 400

@app.route('/api/shows/<int:show_id>', methods=['DELETE'])
def delete_show(show_id):
    show = Show.query.get_or_404(show_id)
    db.session.delete(show)
    db.session.commit()
    return jsonify(message='Show deleted successfully')



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
def search_results():
    query = request.args.get('query')
    venues = Venue.query.filter(Venue.address.like('%{}%'.format(query))).all()
    events = Event.query.filter(Event.name.like('%{}%'.format(query))).all()
    return render_template('search_results.html', query=query, venues=venues, events=events)

@app.route("/logout/user")
def logout_us():
    logout_user()
    return redirect(url_for('home'))

@app.route("/logout/admin")
def logout_ad():
    logout_user()
    return redirect(url_for('home'))
