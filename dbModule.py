from http.client import REQUEST_URI_TOO_LONG
import sqlite3
import random
import hashlib
con = sqlite3.connect('game.db', check_same_thread=False)
cur = con.cursor()

def createGameTable():
    cur.execute('''CREATE TABLE IF NOT EXISTS game (name TEXT NOT NULL UNIQUE, nick TEXT NOT NULL UNIQUE, death_code TEXT NOT NULL UNIQUE, 
    amount_of_kills INTEGER DEFAULT 0, status TEXT DEFAULT "alive")''')

    con.commit()

def createTargetTable():
    killers,targets = generatePairs()
    cur.execute("CREATE TABLE targets(name TEXT NOT NULL, target TEXT NOT NULL)") # table creation
    for i in range(len(killers)):
        cur.execute("INSERT INTO targets('name','target') VALUES(?,?)", (killers[i][0], targets[i][0])) # filling with accordances

    con.commit()

def addUser(name, nick, codeWord):
    prehash = name+codeWord
    killCode = str(hashlib.md5(prehash.encode()).hexdigest())   
    cur.execute("INSERT INTO game('name', 'nick', 'death_code') VALUES(?,?,?)", (name, nick, killCode))

    con.commit()

def dropTable():
    cur.execute("DROP TABLE game")
    cur.execute("DROP TABLE targets")

    con.commit()

def killerById(identificator):
    cur.execute("SELECT name FROM game WHERE nick = ?", (identificator, ))

    con.commit()
    return(cur.fetchall()[0][0])

def targetById(identificator):
    name = killerById(identificator)
    cur.execute("SELECT target FROM targets WHERE name = ?", (name, ))

    con.commit()
    return(cur.fetchall())
    
def showScoreboard():
    cur.execute("SELECT name, amount_of_kills FROM game ORDER BY amount_of_kills DESC")
    return(cur.fetchall())

def generatePairs():
    cur.execute("SELECT name FROM game")
    killers = cur.fetchall()
    targets = []

    for i in range(len(killers)):
        targets.append(killers[i%len(killers)-1])

    con.commit()
    return(killers, targets)

def getGameState():
    cur.execute("SELECT * FROM targets")
    return(cur.fetchall())

def getAllIds():
    cur.execute("SELECT nick FROM game")
    ids = cur.fetchall()

    return ids

def killRequest(killerNick, deathCode):
    killerName = killerById(killerNick)
    cur.execute("SELECT name FROM game WHERE death_code = ?", (deathCode,))
    tmp = cur.fetchall()
    if (tmp != []):
        mbTarget = tmp[0][0]
    else:
        return('NotACode')
    cur.execute("SELECT name FROM targets WHERE target = ?", (mbTarget,))
    tmp = cur.fetchall()
    if (tmp == []):
        return('AlreadyDead')

    elif (tmp[0][0] == killerName):
        cur.execute("DELETE FROM targets WHERE target = ?", (mbTarget,))
        cur.execute("UPDATE targets SET name = ? WHERE name = ?", (killerName, mbTarget))
        cur.execute("UPDATE game SET status = ? WHERE name = ?",('dead', mbTarget))
        cur.execute("UPDATE game SET amount_of_kills = amount_of_kills + 1 WHERE name= ?", (killerName,))
        con.commit()
        return('Killed')
    else:
        con.commit()
        return('StoleACode')

