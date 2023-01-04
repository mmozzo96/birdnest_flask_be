from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from database import database
from flask_cors import cross_origin

database_connection = database()

sched = BackgroundScheduler(daemon=True)
sched.add_job(database_connection.update_database,'interval',seconds=2)
sched.start()

app = Flask(__name__)

@app.route('/dronesandpilots')
@cross_origin()
def drones_and_pilots():
  drones_and_pilots = database_connection.getDrones()

  return drones_and_pilots

@app.route('/drones')
@cross_origin()
def drones():
  drones_and_pilots = database_connection.getDrones()

  return drones_and_pilots


if __name__=="__main__":
  app.run(debug=True)
