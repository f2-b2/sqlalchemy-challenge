#################################################
# Import the dependencies.
#################################################
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#1 - Home Page 
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"<h3>Available Routes:</h3><br/>"
        f"<b>Precipitation observations for the last 12 months of data:</b> <br/>/api/v1.0/precipitation<br/>"
        f"<br/><b>Weather stations:</b> <br/>/api/v1.0/stations<br/>"
        f"<br/><b>Temperature observations for the last 12 months of the data:</b> <br/>/api/v1.0/tobs<br/>"
        f"<br/><b>Temperature summary for a specific date: </b><br/>(replace place holders with date)<br/>/api/v1.0/YYYY-MM-DD<start><br/>"
        f"<br/><b>Temperature summary for a date range: </b><br/>(replace place holders with dates)<br/>/api/v1.0/YYYY-MM-DD<start>/YYYY-MM-DD<end><br/>"
    )

#2- # Convert the query results from your precipitation analysis. Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set
    recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first().date
    dt_year_prior = ((dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d'))
    
    # Retrieve the data and precipitation scores
    year_prior_data  = (session.query(measurement.date, measurement.prcp).filter(measurement.date >= dt_year_prior).all()) 

    # Close Session                                                  
    session.close()

    # Create a dictionary 
    prcp_data = []
    for date, prcp in year_prior_data:
        prior_dict = [f"{date}",f"{prcp} inches"]
        prcp_data.append(prior_dict)

    return jsonify(prcp_data)


#3 - stations list
@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Retrieve data for all stations
    stations = session.query(station.name, station.station).all()
    
    # Close Session                                                  
    session.close()
              
    return jsonify(stations)


#4 - temperature observations of the most-active station for the previous year
@app.route("/api/v1.0/tobs")
def temps():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and temperature scores
    temps_data = (session
             .query(measurement.station, measurement.tobs)
             .filter(measurement.date >= '2016-08-23') 
             .filter(measurement.station == 'USC00519281')
             .all())

    session.close()

    #Return a JSON list
    return jsonify(dict(temps_data))


#5 - Return the temperature summary for a specified start or start-end range.
#5a
@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the temperature summary for a specified start date to the end of the dataset
    results = (session
                .query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))
                .filter(measurement.date >= start)
                .all())
    
        
    (min, max, avg) = results[0] 

    session.close()

    #Reture a JSON
    return jsonify(f"Start date: {start}",f"Temperature (F) High: {round(min,1)}, Low: {round(max,1)}, Average: {round(avg,1)}")

#5b
@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the temperature summary for a specified start date to the specified end date
    results = (session
                .query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))
                .filter(measurement.date >= start)
                .filter(measurement.date <= end)
                .all())

    
    (min, max, avg) = results[0] 
                                              
    session.close()

    #Reture a JSON
    return jsonify(f"Start Date: {start}",
                   f"End Date: {start}",
                   f"Temperature (F) High: {round(min,1)}, Low: {round(max,1)}, Average: {round(avg,1)}")

if __name__ == '__main__':
    app.run(debug=True)