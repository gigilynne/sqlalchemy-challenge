#import Flask and other dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Set up database
engine = create_engine("sqlite:///hawaii.sqlite")
session = Session(engine)

# reflect an existing database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create app, pass name
app = Flask(__name__)

#Define the inital route and state alternatives
@app.route("/")
def about():
    return (
        f"Welcome to the climate API.<br/>"
        f"Please see the available routes below:<br/>"
        f"**************************************<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
# create paths for alternative routes
@app.route('/api/v1.0/<start>')
def start(start):
    
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    tobs_all = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    
    session.close()

    tobs_all = []
    for min,avg,max in query_result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route('/api/v1.0/tobs')
def tobs():
    recent_dt = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(recent_dt, '%Y-%m-%d')
    query_date = dt.date(last_date.year -1, last_date.month, last_date.day)
    sel = [Measurement.date,Measurement.tobs]
    query_result = session.query(*sel).filter(Measurement.date >= query_date).all()
    
    # session.close()

    tobs_all = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)

@app.route('/api/v1.0/stations')
def stations():
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    query_result = session.query(*sel).all()
   
    # session.close()

    stations = []
    for station,name,lat,lon,el in query_result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    sel = [Measurement.date,Measurement.prcp]
    query_result = session.query(*sel).all()

    session.close()

    precipitation = []
    for date, prcp in query_result:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

if __name__ == '__main__':
    app.run(debug=True)