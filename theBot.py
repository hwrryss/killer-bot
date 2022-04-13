import telebot
import qrModule
import dbModule
import conModule
import msgs
import os

token='5087247335:AAHhTsiYXbEx8o58A5tphyPBHr8UVFa40EE'
bot=telebot.TeleBot(token)
gameStatus = False
registrationStatus = True
adminId =  os.environ['ADMIN']
dbModule.createGameTable()

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, msgs.welcoming)


@bot.message_handler(commands=['Rules'])
def registration_message(message):
    bot.send_message(message.chat.id, msgs.rules)


@bot.message_handler(commands=['Registration'])
def registration_message(message):
    global mes
    global registrationStatus

    if registrationStatus == True:
        mes = message.text.split()[1:]
        if len(mes) == 3:
            name = mes[0] + '_' + mes[1]
            dbModule.addUser(name, message.from_user.username, mes[2]) # новый пользователь в таблице 
            bot.send_photo(message.chat.id, qrModule.generateQr(name, mes[2]))
            bot.send_message(message.chat.id,  msgs.regsuc)
        else:
            bot.send_message(message.chat.id,  msgs.regerr)
    else:
        bot.send_message(message.chat.id, msgs.regclosed)

    
@bot.message_handler(commands=['GameStart'])
def gamestart_message(message):
    global gameStatus
    global registrationStatus
    
    if message.from_user.username == adminId and gameStatus == False:
        gameStatus = True
        registrationStatus = False
        conModule.startGame()

@bot.message_handler(commands=['EndGame'])
def gameend_message(message):
    global gameStatus
     
    if gameStatus == True and message.from_user.username == adminId:
        gameStatus = False
        conModule.endGame

    dbModule.dropTable()


@bot.message_handler(commands=['GameState'])
def scoreboard_message(message):
    if gameStatus == True and message.from_user.username == adminId:
        theGameState = '-------Current---Targets-------' + '\n'
        gameState = dbModule.getGameState()
        for i in range(len(gameState)):
            theGameState += gameState[i][0] + ' x ' + gameState[i][1] + '\n'
        bot.send_message(message.chat.id, theGameState)


@bot.message_handler(commands=['Scoreboard'])
def scoreboard_message(message):
    global gameStatus
    
    if gameStatus == True:
        theScoreboard = '-------Scoreboard-------' + '\n'
        scoreboard = dbModule.showScoreboard()
        for i in range(len(scoreboard)):
            if i == 0:
                theScoreboard += '🥇' + ' ' + scoreboard[i][0] + ' ' + str(scoreboard[i][1]) + '\n'
            elif i == 1:
                theScoreboard += '🥈' + ' ' + scoreboard[i][0] + ' ' + str(scoreboard[i][1]) + '\n'
            elif i == 2:
                theScoreboard += '🥉' + ' ' + scoreboard[i][0] + ' ' + str(scoreboard[i][1]) + '\n'
            else:
                theScoreboard += str((i+1)) + ' ' + scoreboard[i][0] + ' ' + str(scoreboard[i][1]) + '\n'
        bot.send_message(message.chat.id, theScoreboard[:-1])
    else:
        bot.send_message(message.chat.id, msgs.wait)


@bot.message_handler(commands=['Status'])
def status_message(message):
    global mes
    global gameStatus

    if gameStatus == True:
        name = mes[0] + '_' + mes[1]
        bot.send_message(message.chat.id, dbModule.targetById(message.from_user.username)) # выводит твою цель 
        bot.send_photo(message.chat.id, qrModule.generateQr(name, mes[2]))
    else:
        bot.send_message(message.chat.id, msgs.wait)


@bot.message_handler(content_types=['text'])
def message_reply(message):
    global gameStatus
    if gameStatus == True:
        request =  dbModule.killRequest(message.from_user.username, message.text)
        if request == 'AlreadyDead':
            bot.send_message(message.chat.id, msgs.alreadydead) 
        elif request == 'NotACode':
            bot.send_message(message.chat.id, msgs.notacode)
        elif request == 'StoleACode':
            bot.send_message(message.chat.id, msgs.codestolen)
        elif request == 'Killed':
            bot.send_message(message.chat.id, msgs.kill)
    else:
        bot.send_message(message.chat.id, msgs.wait)

    
mes = ''
Game_started=False
bot.infinity_polling()
dbModule.dropTable()