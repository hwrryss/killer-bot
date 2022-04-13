import dbModule


def startGame():
    dbModule.createTargetTable()
    pass

def endGame():
    dbModule.dropTable()
    pass
