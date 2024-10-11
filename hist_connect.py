import sqlite3
from qgis.core import QgsUserProfile, QgsApplication
import os
import xml.etree.ElementTree as et

# TODO: figure out the best way to avoid returning an empty history

app = QgsApplication.instance()

def getProfileDbs(app: QgsApplication):
    historydbs = []
    profiles_root = os.path.split(os.path.dirname(QgsApplication.instance().qgisUserDatabasePath()))[0]
    profiles = os.listdir(profiles_root)

    for item in profiles:
        if os.path.isdir(item):
            historydb = os.path.join(item, 'user-history.db')
            if os.path.exists(historydb):
                historydbs.append(historydb)

    return historydbs

def fetchHistory(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    res = cur.execute('SELECT timestamp, name FROM history')
    raw_hist = res.fetchall()
    return raw_hist

def parseHist(hist):
    parsed_list = []
    for item in hist:
        item_dict = {}
        item_dict['timestamp'] = item[0]
        root = et.fromstring(item[1])
        raw_name = root[0].attrib['value']
        item_dict['algorithm'] = root[0].attrib['value']
        for child in root[2][3]:
            item_dict[child.attrib['name']] = child.attrib['value']
        parsed_list.append(item_dict)
    return parsed_list
