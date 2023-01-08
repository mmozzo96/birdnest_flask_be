import pymongo
import certifi
import requests
import xmltodict
import datetime
import pprint
import json

class database:

  session = requests.Session()

  def __init__(self): 
    client = pymongo.MongoClient("mongodb+srv://mmozzo:mmozzo1996@reaktor-db.huvxx2m.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
    db = client["reaktor-db"]
    self.drones_collection = db.drones

  def drones_data(self):
    response = self.session.get("https://assignments.reaktor.com/birdnest/drones")
    report = xmltodict.parse(response.content)['report']
    timestamp = report['capture']["@snapshotTimestamp"]

    drones_data = []
    for drone in report['capture']['drone']:
      distance = ((float(drone['positionX'])/1000 - 250)**2 + (float(drone['positionY'])/1000 - 250)**2)**0.5
      drones_data.append({
        'serialNumber': drone['serialNumber'],
        'distance': distance,
        'timestamp': timestamp,
        'expires_at': datetime.datetime.fromisoformat(timestamp[:-1]+'+00:00') + datetime.timedelta(minutes=10),
        'drone': drone,
      })

    return drones_data

  def update_database(self):
    drones_data = database.drones_data(self)
    collection = self.drones_collection
    timestamp = drones_data[0]['timestamp']

    for drone_data in drones_data:

      if drone_data['distance'] < 100:
        pilot={}
        if collection.find_one({'serialNumber': drone_data['serialNumber']})==None:
          try:
            pilot = json.loads(self.session.get(f"https://assignments.reaktor.com/birdnest/pilots/{drone_data['serialNumber']}").content.decode('utf-8'))
          except self.session.exceptions.RequestException as e:
            pilot = {'pilotID': None}

        collection.find_one_and_update(
          {'serialNumber': drone_data['serialNumber']},
          {
            '$setOnInsert': {'serialNumber': drone_data['serialNumber'], 'pilot': pilot, 'droneData': drone_data['drone']},
            '$min': {'distance': drone_data['distance']},
            '$set': {'timestamp': drone_data['timestamp'], 'expires_at': drone_data['expires_at']},
          },
          upsert=True
        )

      else:
        collection.update_many(
          {'serialNumber': drone_data['serialNumber']},
          {
            '$set': {'timestamp': drone_data['timestamp'], 'expires_at': drone_data['expires_at']},
          }
        )

    collection.delete_many({'expires_at': {'$lte': datetime.datetime.fromisoformat(timestamp[:-1]+'+00:00')}})

  def getDrones(self):
    drones = []
    collection = self.drones_collection
    cursor = collection.find({}, {
      '_id': 0,
      'expires_at': 0,
    })

    for document in cursor:
      drones.append(document)

    return drones


if __name__ == "__main__":
  database_connection = database()
  database_connection.update_database()