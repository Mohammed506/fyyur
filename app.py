#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort, name
import dateutil.parser
import babel
from flask_migrate import Migrate
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler, error
from flask_wtf import Form, csrf
from sqlalchemy.orm import backref
from flask_wtf.csrf import CSRFProtect
from forms import *
from models import * 



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf= CSRFProtect(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# class Venue(db.Model):
#     __tablename__ = 'venue'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     seeking_talent = db.Column(db.Boolean, default= False )
#     seeking_description = db.Column(db.String(400), default='')
#     show = db.relationship('Show', backref='venue')

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate


# class Artist(db.Model):
#     __tablename__ = 'artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website = db.Column(db.String(120))
#     seeking_venue = db.Column(db.Boolean)
#     seeking_description = db.Column(db.String(400), default='')
#     show = db.relationship('Show', backref='artist')

# # TODO: implement any missing fields, as a database migration using Flask-Migrate

# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


# class Show(db.Model):
#     __tablename__ = 'show'
#     id = db.Column(db.Integer, primary_key=True)
#     venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
#     start_time = db.Column(db.DateTime,nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    venues = Venue.query.all()
    data = []
    location = set()

    for venue in venues:
    
        location.add((venue.city, venue.state))

 
    for loc in location:
        data.append({
      "city": loc[0],
      "state": loc[1],
      "venues": []
    })

    for venue in venues:
        upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        current_date = datetime.now()

        for show in shows:
            if show.start_time > current_date:
                upcoming_shows += 1
    

        for venue_location in data:
            if venue.state == venue_location['state'] and venue.city == venue_location['city']:
                venue_location['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming_shows
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term','')
    Search_data = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    response={
    "count": Search_data.count(),
    "data": Search_data
  }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # try:

        venue = Venue.query.get(venue_id)
        if not venue :
            abort(404)
        shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
        past_shows = []
        upcoming_shows = []
        current_time = datetime.now()
        if shows :



            for show in shows:


                    data = {
                    'artist_id': show.artist_id,
                    'artist_name': show.artist.name,
                    'artist_image_link': show.artist.image_link,
                    'start_time': format_datetime(str(show.start_time))
                    }
                    if show.start_time > current_time:
                        upcoming_shows.append(data)
                    else:
                        past_shows.append(data)

        data={
                    'id': venue.id,
                    'name': venue.name,
                    'genres': venue.genres.split(', '),
                    'address': venue.address,
                    'city': venue.city,
                    'state': venue.state,
                    'phone': venue.phone,
                    'website': venue.website,
                    'facebook_link': venue.facebook_link,
                    'seeking_talent': venue.seeking_talent,
                    'seeking_description':venue.seeking_description,
                    'image_link': venue.image_link,
                    'past_shows': past_shows,
                    'upcoming_shows': upcoming_shows,
                    'past_shows_count': len(past_shows),
                    'upcoming_shows_count': len(upcoming_shows)
                }
            
            
        
        return render_template('pages/show_venue.html', venue=data)

    # except: 
        
    #     abort(404)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    

    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():


    # TODO: insert form data as a new Venue record in the db, instead


    
   try:
        form = VenueForm(request.form)



        
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,website=form.website_link.data, seeking_talent=form.seeking_talent.data)
        

        if form.validate_on_submit():

        
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else :
            flash('Phone number should only contain digits')
            return render_template('forms/new_venue.html', form=form)
    
   except:

    
        db.session.rollback()
        flash('An error occurred. Venue'+ request.form['name'] + ' could not be listed')
   finally:

    
        db.session.close()

 
 




    
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
   print(form.errors)

   return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try : 
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except : 
        db.session.rollback()
    finally : 
        db.session.close()


    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    art = Artist.query.all()
    data = []

    for artist in art :
        data.append({
            'id':artist.id , 
            'name' : artist.name
        })


    
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term=request.form.get('search_term', '')
    search_art = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response = { 
        'count': search_art.count() , 
        'data' : search_art
    }
    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()
    if not artist : 

        abort(404)
    if shows :


   

        for show in shows:
            data = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': format_datetime(str(show.start_time))
            }
            if show.start_time > current_time:
                upcoming_shows.append(data)
            else:
                past_shows.append(data)

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres.split(', '),
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'facebook_link': artist.facebook_link,
        'image_link': artist.image_link,
        'seeking_venue' : artist.seeking_venue,
        'seeking_description' : artist.seeking_description ,
        'website' : artist.website , 
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_data = Artist.query.get(artist_id)

    artist={
    'id': artist_data.id,
    'name': artist_data.name,
    'genres': artist_data.genres,
    'city': artist_data.city,
    'state': artist_data.state,
    'phone': artist_data.phone,
    'facebook_link': artist_data.facebook_link,
    'image_link': artist_data.image_link , 
    'seeking_venue' : artist_data.seeking_venue, 
    'seeking_description' : artist_data.seeking_description,
    'website' : artist_data.website 
    
    }

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        if form.validate():

            
            name = form.name.data

            artist.name = name
            artist.phone = form.phone.data
            artist.state = form.state.data
            artist.city = form.city.data
            artist.genres = form.genres.data
            artist.image_link = form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.website= form.website_link.data
            artist.seeking_venue= form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data

            db.session.commit()
            flash('The Artist ' + request.form['name'] + ' has been successfully updated!')
        else:
            flash('phone number should only contain digits')
    except:
        db.session.rollback()
        flash('An Error has occured and the update unsucessful')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
     form = VenueForm()
     venue = Venue.query.get(venue_id)
     
     

     venue = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website':venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link
        }  
    
   
    # TODO: populate form with values from venue with ID <venue_id>
     return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        if form.validate():

        

            venue.name = form.name.data
            venue.genres = form.genres.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website_link.data
            venue.image_link = form.image_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.commit()
            flash('Venue ' + request.form['name'] + ' has been updated')
        else :
            flash('phone number should only contain digits')
    except:
        db.session.rollback()
        flash('An error occured while trying to update Venue')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
        try:
            form = ArtistForm()
            
            if form.validate_on_submit():

        
            
                artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                                phone=form.phone.data, genres=form.genres.data,
                                image_link=form.image_link.data, facebook_link=form.facebook_link.data, seeking_venue=True if 'seeking_venue' in request.form else False, seeking_description=form.seeking_description.data)
                db.session.add(artist)
                db.session.commit()
  
                flash('Artist ' + request.form['name'] + ' was successfully listed!')
            else:
                flash('phone number should only contain digits')
                return render_template('forms/new_artist.html', form=form)

        except:
            db.session.rollback()
            flash('An error ocurred, Artist ' + request.form['name'] + ' could not be listed')
        finally:
            db.session.close()

        # on successful db insert, flash success
        
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows =Show.query.all()
    data=[]
    for s in shows : 
        data.append({

            'venue_id' : s.venue_id,
            'venue_name': s.venue.name,
            'artist_id' :s.artist_id ,  
            'artist_name' : s.artist.name,
            'artist_image_link' :s.artist.image_link, 
            'start_time': format_datetime(str(s.start_time))


            })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
        try:
            show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'],
                        start_time=request.form['start_time'])

            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
  
        except:
            db.session.rollback()
            flash('An error occured. show could not be listed')
        finally:
            db.session.close()

    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

