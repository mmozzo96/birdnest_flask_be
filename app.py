from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from database import database
from flask_cors import cross_origin
import requests
import xmltodict

database_connection = database()

count = 0
jobIsPaused = False

def job_function():
  global count, job, jobIsPaused
  
  database_connection.update_database()

  count = count + 1
  if count == 1800:
    job.pause()
    jobIsPaused = True


sched = BackgroundScheduler(daemon=True)
job = sched.add_job(job_function,'interval', seconds=2, id="AdfaF345we")
sched.start()

app = Flask(__name__)

@app.route('/dronesandpilots')
@cross_origin()
def drones_and_pilots():
  global count, job

  drones_and_pilots = database_connection.getDrones()

  count = 0
  job.resume()

  return drones_and_pilots

@app.route('/drones')
@cross_origin()
def drones():
  global count, job

  response = requests.get("https://assignments.reaktor.com/birdnest/drones")
  report = xmltodict.parse(response.content)['report']

  count = 0
  job.resume()

  return report['capture']['drone']


if __name__=="__main__":
  app.run(debug=True)
