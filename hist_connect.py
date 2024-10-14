import sqlite3
from qgis.core import QgsApplication
import os
import xml.etree.ElementTree as et

def getProfileDb(app: QgsApplication):
    # returns path of user-history.db
    profile_root = os.path.dirname(app.qgisUserDatabaseFilePath())
    history_db = os.path.join(profile_root, 'user-history.db')

    return history_db

def fetchHistory(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    res = cur.execute('SELECT timestamp, xml FROM history')
    # returns a list of tuples (timestamps, raw XML text of history items)
    raw_hist = res.fetchall()
    return raw_hist

def parseHistory(hist): 
    '''takes the raw history (list of tuples)
    will return a list of dicts where each dict represents a single history item
    each dict will have a timestamp, an algo name, and a string of delimited parameter
    names and values'''
    parsed_list = []
    for item in hist:
        item_dict = {}
        item_dict['timestamp'] = item[0]
        # second field in the tuple is a raw XML string, so we need to parse that
        root = et.fromstring(item[1])
        id = root[0].attrib['value']
        item_dict['id'] = id
        alg = QgsApplication.processingRegistry().algorithmById(id)
        try:
            item_dict['algorithm'] = alg.displayName()
        except AttributeError:
            item_dict['algorithm'] = 'unknown'
        params_string = ""
        for child in root[2][3]:
            try:
                name = child.attrib['name']
            except KeyError:
                name = 'unknown'
            try:
                value = child.attrib['value']
            except KeyError:
                value = 'unknown'
            params_string = params_string + name + ': ' + value + '; '
            item_dict['params'] = params_string
        parsed_list.append(item_dict)
    return parsed_list

def writeHistory(db, parsed_list):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("CREATE TABLE history(timestamp, id, algorithm, params)")
    cur.executemany("INSERT INTO history (timestamp, id, algorithm, params) VALUES (:timestamp, :id, :algorithm, :params)", parsed_list)
    con.commit()
    cur.close()
    con.close()

'''order of operations:
- getProfileDb
- fetchHistory
- parseHistory
'''

# TODO: add icon
# TODO: save parsed history to new sqlite db
