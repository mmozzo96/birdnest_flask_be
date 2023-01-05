from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from database import database
from flask_cors import cross_origin
import requests
import xmltodict

database_connection = database()

def test():
  print('hello')

sched = BackgroundScheduler(daemon=True)
sched.add_job(test,'interval',seconds=2)
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
  response = requests.get("https://assignments.reaktor.com/birdnest/drones")
  report = xmltodict.parse(response.content)['report']

  return report['capture']['drone']


if __name__=="__main__":
  app.run(debug=True)
