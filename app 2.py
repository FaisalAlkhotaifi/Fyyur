#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    show_list = db.relationship('Show', backref='venue', lazy=True)
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    show_list = db.relationship('Show', backref='artist', lazy=True)
    
class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, nullable=False) 
   date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   date_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"))
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venue_list = Venue.query.all()
  
  venue_data_groupedby_city = []
  cities = []

  for venue in venue_list:
    if venue.city not in cities:
      cities.append(venue.city)
      venue_data_groupedby_city.append({
        "city": venue.city,
        "state": venue.state,
        "venues": []
      })

    num_upcoming_shows = 0
    for show in venue.show_list:
      if show.start_time >= datetime.utcnow():
        num_upcoming_shows += 1
        
    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    }

    city_index = cities.index(venue.city)
    venue_data_groupedby_city[city_index]['venues'].append(venue_data)

  return render_template('pages/venues.html', areas=venue_data_groupedby_city)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  venue_data = []

  search_term = request.form.get('search_term')
  searched_venue_list = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  for venue in searched_venue_list:
    num_upcoming_shows = 0
    for show in venue.show_list:
      if show.start_time >= datetime.utcnow():
        num_upcoming_shows += 1

    venue_data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  
  response = {
    "count": len(venue_data),
    "data": venue_data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue is None:
    abort(404)

  past_shows = []
  upcoming_shows = []

  show_list = Show.query.filter(Show.venue_id == venue_id)
  for show in show_list:
    show_data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat(sep='T')[:-3] + 'Z' 
    }

    if show.start_time < datetime.utcnow():
      past_shows.append(show_data)
    else: 
      upcoming_shows.append(show_data)

  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  is_error = False

  try:
    venue_form = VenueForm()
    seeking_talent = False

    if venue_form.seeking_talent.data == 'Yes':
      seeking_talent = True

    new_venue = Venue(
      name = venue_form.name.data,
      city = venue_form.city.data,
      state = venue_form.state.data,
      address = venue_form.address.data,
      phone = venue_form.phone.data,
      image_link = venue_form.image_link.data,
      genres = venue_form.genres.data,
      facebook_link = venue_form.facebook_link.data,
      website = venue_form.website.data,
      seeking_talent = seeking_talent,
      seeking_description = venue_form.seeking_description.data
    )
    
    db.session.add(new_venue)
    db.session.commit()
  except:
    is_error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if is_error:
    flash('Error: Venue ' + request.form['name'] + ' could not be listed!')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []

  for a in artists:
    data.append({
      "id": a.id,
      "name": a.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  artist_data = []

  search_term = request.form.get('search_term')
  searched_artist_list = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  for artist in searched_artist_list:
    num_upcoming_shows = 0
    for show in artist.show_list:
      if show.start_time >= datetime.utcnow():
        num_upcoming_shows += 1

    artist_data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
  
  response = {
    "count": len(artist_data),
    "data": artist_data
  }

  print("search term: %s", request.form.get('search_term'))

  #searched_venue = Venue.query.filter(Venue.name.ilike())

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist is None:
    abort(404)

  seeking_venue = False
  past_shows = []
  upcoming_shows = []

  show_list = Show.query.filter(Show.artist_id == artist_id)
  for show in show_list:
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.isoformat(sep='T')[:-3] + 'Z' 
    }

    if show.start_time < datetime.utcnow():
      past_shows.append(show_data)
    else: 
      upcoming_shows.append(show_data)

  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  seeking_venue = 'No'
  if artist.seeking_venue:
    seeking_venue = 'Yes'

  form.state.data = artist.state
  form.genres.data = artist.genres
  form.seeking_venue.data = seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  is_error = False

  try:
    artist_form = ArtistForm()
    artist = Artist.query.get(artist_id)

    seeking_venue = False

    if artist_form.seeking_venue.data == 'Yes':
      seeking_venue = True

    artist.name = artist_form.name.data
    artist.city = artist_form.city.data
    artist.state = artist_form.state.data
    artist.phone = artist_form.phone.data
    artist.image_link = artist_form.image_link.data
    artist.genres = artist_form.genres.data
    artist.facebook_link = artist_form.facebook_link.data
    artist.website = artist_form.website.data
    artist.seeking_venue = seeking_venue
    artist.seeking_description = artist_form.seeking_description.data

    db.session.commit()
  except:
    is_error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if is_error:
    flash('Error: Artists ' + request.form['name'] + ' could not be updated!')
    form = ArtistForm()
    artist = Venue.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    flash('Artists ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  seeking_talent = 'No'
  if venue.seeking_talent:
    seeking_talent = 'Yes'

  form.state.data = venue.state
  form.genres.data = venue.genres
  form.seeking_talent.data = seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  is_error = False

  try:
    venue_form = VenueForm()
    venue = Venue.query.get(venue_id)

    seeking_talent = False

    if venue_form.seeking_talent.data == 'Yes':
      seeking_talent = True

    venue.name = venue_form.name.data
    venue.city = venue_form.city.data
    venue.state = venue_form.state.data
    venue.address = venue_form.address.data
    venue.phone = venue_form.phone.data
    venue.image_link = venue_form.image_link.data
    venue.genres = venue_form.genres.data
    venue.facebook_link = venue_form.facebook_link.data
    venue.website = venue_form.website.data
    venue.seeking_talent = seeking_talent
    venue.seeking_description = venue_form.seeking_description.data

    db.session.commit()
  except:
    is_error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if is_error:
    flash('Error: Venue ' + request.form['name'] + ' could not be updated!')
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  is_error = False

  try:
    artist_form = ArtistForm()
    seeking_venue = False

    if artist_form.seeking_venue.data == 'Yes':
      seeking_venue = True

    new_artist = Artist(
      name = artist_form.name.data,
      city = artist_form.city.data,
      state = artist_form.state.data,
      phone = artist_form.phone.data,
      image_link = artist_form.image_link.data,
      genres = artist_form.genres.data,
      facebook_link = artist_form.facebook_link.data,
      website = artist_form.website.data,
      seeking_venue = seeking_venue,
      seeking_description = artist_form.seeking_description.data
    )
    
    db.session.add(new_artist)
    db.session.commit()
  except:
    is_error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if is_error:
    flash('Error: Artist ' + request.form['name'] + ' could not be listed!')
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []

  for s in shows:
    data.append(
      {
        "venue_id": s.venue_id,
        "venue_name": s.venue.name,
        "artist_id": s.artist_id,
        "artist_name": s.artist.name,
        "artist_image_link": s.artist.image_link,
        "start_time": s.start_time.isoformat(sep='T')[:-3] + 'Z'
      }
    )

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  is_error = False
  is_not_found = False
  error_message = ''

  try:
    show_form = ShowForm()

    artist_info = Artist.query.get(show_form.artist_id.data)
    if artist_info is None:
      is_not_found = True
      error_message = "Artist not found!"
      raise Exception("Artist not found!")

    venues_info = Venue.query.get(show_form.venue_id.data)
    if venues_info is None:
      is_not_found = True
      error_message = "Venue not found!"
      raise Exception("Venue not found!")

    new_show = Show(
      artist_id = show_form.artist_id.data,
      venue_id = show_form.venue_id.data,
      start_time = show_form.start_time.data
    )

    db.session.add(new_show)
    db.session.commit()
  except:
    is_error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if is_error:
    if is_not_found:
      flash(error_message)
    else:
      flash('Error: Show could not be listed!')

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
