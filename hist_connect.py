import sqlite3
from qgis.core import QgsApplication
import os
import xml.etree.ElementTree as et

def getProfileDb(app: QgsApplication):
    # returns path of user-history.db
    profile_root = os.path.dirname(app.qgisUserDatabaseFilePath())
    history_db = os.path.join(profile_root, 'user-history.db')

    return history_db

def getNewDb(app: QgsApplication):
    plugin_root = os.path.dirname(os.path.realpath(__file__))
    newdbpath = os.path.join(plugin_root, 'param-history.db')

    return newdbpath

def getSingleEntry(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    res = cur.execute('SELECT timestamp, xml FROM history ORDER BY timestamp DESC')
    raw_hist = res.fetchone()
    cur.close()
    con.close()

    return raw_hist

def fetchHistory(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    res = cur.execute('SELECT timestamp, xml FROM history')
    # returns a list of tuples (timestamps, raw XML text of history items)
    raw_hist = res.fetchall()
    cur.close()
    con.close()
    return raw_hist

def parseSingleEntry(hist):
    item_dict = {}
    item_dict['timestamp'] = hist[0]
    root = et.fromstring(hist[1])
    for child in root:
        if child.attrib['name'] == 'algorithm_id':
            id = child.attrib['value']
            item_dict['id'] = id
            alg = QgsApplication.processingRegistry().algorithmById(id)
            try:
                item_dict['algorithm'] = alg.displayName()
            except AttributeError:
                item_dict['algorithm'] = id
        elif child.attrib['name'] == 'parameters':
            params_string = ""
            for grandchild in child:
                try:
                    name = grandchild.attrib['name']
                except KeyError:
                    name = 'unknown'
                if name == "inputs":
                    for ggchild in grandchild:
                        try:
                            name = ggchild.attrib['name']
                        except KeyError:
                            name = 'unknown'
                        if name == 'TABLE':
                            value = []
                            for gggchild in ggchild:
                                try: 
                                    value.append(gggchild.attrib['value'])
                                except KeyError:
                                    continue
                            value = ' '.join(str(x) for x in value)
                        else:
                            try: 
                                value = ggchild.attrib['value']
                            except KeyError:
                                value = 'N/A'
                        if value == '':
                            value = 'N/A'
                        params_string = params_string + name + ': ' + value + '; '
                        item_dict['params'] = params_string
        else:
            continue
    return item_dict                

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
        for child in root:
            if child.attrib['name'] == 'algorithm_id':
                id = child.attrib['value']
                item_dict['id'] = id
                alg = QgsApplication.processingRegistry().algorithmById(id)
                try:
                    item_dict['algorithm'] = alg.displayName()
                except AttributeError:
                    item_dict['algorithm'] = id
            elif child.attrib['name'] == 'parameters':
                params_string = ""
                for grandchild in child:
                    try:
                        name = grandchild.attrib['name']
                    except KeyError:
                        name = 'unknown'
                    if name == "inputs":
                        for ggchild in grandchild:
                            try:
                                name = ggchild.attrib['name']
                            except KeyError:
                                name = 'unknown'
                            if name == 'TABLE':
                                value = []
                                for gggchild in ggchild:
                                    try: 
                                        value.append(gggchild.attrib['value'])
                                    except KeyError:
                                        continue
                                value = ' '.join(str(x) for x in value)
                            else:
                                try: 
                                    value = ggchild.attrib['value']
                                except KeyError:
                                    value = 'N/A'
                            if value == '':
                                value = 'N/A'
                            params_string = params_string + name + ': ' + value + '; '
                            item_dict['params'] = params_string
            else:
                continue
        parsed_list.append(item_dict)
    return parsed_list

def writeSingleEntry(db, parsed_hist):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute('INSERT INTO history (timestamp, id, algorithm, params) VALUES (:timestamp, :id, :algorithm, :params)', parsed_hist)
    con.commit()
    cur.close()
    con.close()

def writeHistory(db, parsed_list):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("CREATE TABLE history(timestamp, id, algorithm, params)")
    cur.executemany("INSERT INTO history (timestamp, id, algorithm, params) VALUES (:timestamp, :id, :algorithm, :params)", parsed_list)
    con.commit()
    cur.close()
    con.close()

def readNewHistory(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT id, algorithm, params, timestamp FROM history")
    res = cur.fetchall()
    cur.close()
    con.close()
    return res

def readSingleNewEntry(db):
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("SELECT id, algorithm, params, timestamp FROM history ORDER BY timestamp DESC")
    res = cur.fetchone()
    cur.close()
    con.close()
    return res
