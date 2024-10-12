import sqlite3
from qgis.core import QgsUserProfile, QgsApplication
import os
import xml.etree.ElementTree as et

def getProfileDbs(app: QgsApplication):
    # will return a list of strings representing all user-history.db files
    # in the profiles directory
    historydbs = []
    profiles_root = os.path.split(os.path.dirname(app.qgisUserDatabasePath()))[0]
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
    # returns a list of tuples (timestamps, raw XML text of history items)
    raw_hist = res.fetchall()
    return raw_hist

def parseHistory(hist): # takes the raw history from fetchHistory (list of tuples)
    # will return a list of dicts where each dict represents a single history item
    # each dict will have a timestamp, an algo name, and a series of key-value pairs
    # for every input parameter used in the algorithm
    parsed_list = []
    for item in hist:
        item_dict = {}
        item_dict['timestamp'] = item[0]
        # second field in the tuple is a raw XML string, so we need to parse that
        root = et.fromstring(item[1])
        raw_name = root[0].attrib['value']
        item_dict['algorithm'] = root[0].attrib['value']
        for child in root[2][3]:
            item_dict[child.attrib['name']] = child.attrib['value']
        parsed_list.append(item_dict)
    return parsed_list

def combineHistories(db_list):
    # list of lists of tuples
    hist_list = []
    for db in db_list:
        raw_history = fetchHistory(db)
        if len(raw_history) == 0:
            continue
        else:
            hist_list.append(raw_history)
    return hist_list

def mergeHistories(hist_list):
    if len(hist_list) == 0:
        return []
    elif len(hist_list) == 1:
        return hist_list[0]
    else:
        master_hist = hist_list[0]
        for hist in hist_list[1:]:
            for item in hist:
                master_hist.append(item)
        # sorts master history by first element of each tuple
        # only called if more than one history db to save time
        # presumes an individual history db will be sorted
        sorted_hist = sorted(master_hist, key=lambda tup: tup[0])
        return sorted_hist
