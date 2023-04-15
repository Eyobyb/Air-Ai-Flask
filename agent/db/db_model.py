from tinydb import TinyDB ,Query
db = TinyDB('db.json')
from datetime import datetime

Conv = Query()

def insert(data):
   now = datetime.now()
   return db.insert({**data , "created_date":"%s" % now})

def search(session_id:str):
    return db.search(Conv.session_id  == session_id)