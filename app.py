import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# Create engine and reflect
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date, prcp from Measurement
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016,8,23').order_by(
            Measurement.date).all()
    session.close()

    # Convert to dictionary and append
    date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict['date'] = date
        date_prcp_dict['prcp'] = prcp
        date_prcp.append(date_prcp_dict)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    results = session.query(Station.station, Station.name).all()

    session.close()


    return jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    highest_tobs_station=session.query(Measurement.station,func.max(Measurement.tobs)).first()
    last_observation=session.query(Measurement.date).\
    filter(Measurement.station==highest_tobs_station[0]).\
    order_by(Measurement.date.desc()).first()
    year_ago=dt.datetime(2017,8,23)-dt.timedelta(days=365)
# Query the last 12 months of tobs for this station
    tobs_total=session.query(Measurement.station,Measurement.tobs).\
    filter(Measurement.station == highest_tobs_station[0]).order_by(Measurement.date).all()

    session.close()


    return jsonify(tobs_total)
@app.route("/api/v1.0/<start>")
def stats(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'), func.avg(Measurement.tobs).label('avg_temp'))\
        .filter(Measurement.date >= start).all()
    session.close()
    stats_tobs = []
    for r in results:
        tobs_dict = {}
        tobs_dict['min_temp'] = r.min_temp
        tobs_dict['max_temp'] = r.max_temp
        tobs_dict['avg_temp'] = r.avg_temp

        stats_tobs.append(tobs_dict)

    return jsonify(f"Start date:{start}",stats_tobs)
@app.route("/api/v1.0/<start>/<end>")
def stats_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs).label('min_temp'), func.max(Measurement.tobs).label('max_temp'), func.avg(Measurement.tobs).label('avg_temp'))\
        .filter(Measurement.date >= start)\
        .filter(Measurement.date<= end).all()
    session.close()
    stats_tobs = []
    for r in results:
        tobs_dict = {}
        tobs_dict['min_temp'] = r.min_temp
        tobs_dict['max_temp'] = r.max_temp
        tobs_dict['avg_temp'] = r.avg_temp

        stats_tobs.append(tobs_dict)

    return jsonify(f"Start date:{start}",f"End date:{end}",stats_tobs)


if __name__ == '__main__':
    app.run(debug=True)