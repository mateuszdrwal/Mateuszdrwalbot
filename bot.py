from __future__ import division
debug = 1

import traceback,requests,classes,socket,time,re,threading,json,time,math,datetime,os,gspread,loginInfo,data,enchant,string,sys,logging
from oauth2client.service_account import ServiceAccountCredentials
from utilityFunctions import utilityFunctions
from urllib2 import urlopen


#--------------------
#    variables
#--------------------
uf = utilityFunctions()
info = classes.info()
ralle = classes.info()
timer = classes.timer()
joke = classes.randomMessages()
quote = classes.randomMessages()
usrTable = classes.ssTable()
wordTable = classes.ssTable()

CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
streamtime = 0
mvd = 0
md = 0
lastChat = ""
status = False
usrTableAdd = []
wordTableAdd = []
ss2val = None
dic = enchant.Dict("en_US")
prefix = "!"
streamUptime = ""
shutdown = 0

channel = int(json.loads(uf.url("https://api.twitch.tv/kraken/users?login=%s&client_id=%s&api_version=5"%(data.channelName, loginInfo.twitchApiId)).read().decode('utf-8')).get("users")[0].get("_id"))
perms = data.perms
info.info = data.info
ralle.info = data.ralle
joke.load(data.joke)
quote.load(data.quote)
commands = data.commands
timer.started = data.timerStarted
timer.active = data.timerActive
wiki = data.wiki
if data.savedAt == str(datetime.datetime.date(datetime.datetime.now())):
    mvd = data.mvd
    md = data.md
    streamtime = data.streamtime

#--------------------
# configuring stuff
#--------------------
s = socket.socket()
s.connect(("irc.twitch.tv", 6667))
s.send(("PASS %s\r\n"%loginInfo.twitchPass).encode("utf-8"))
s.send(("NICK %s\r\n"%loginInfo.twitchUsername).encode("utf-8"))
s.send(("JOIN #%s\r\n"%data.channelName).encode("utf-8"))

logging.basicConfig(filename="logs/%s.log"%str(datetime.datetime.now()),level=logging.INFO)

#--------------------
#    bot commands
#--------------------
class botCommands:

    @staticmethod
    def addcommand(args,usr):
        if args[1:] == []:
            chat("Command name cannot be empty.")
            return
            
        if args[1].startswith(prefix):
            args[1] = args[1].strip(prefix)

        cmd = args[1]
        args[1] = ""
        for char in cmd:
            if char in string.ascii_letters+string.digits:
                args[1] += char
            
        if args[1] in commands:
            chat("That command already exists.")
            return

        if len(args[1]) > 20:
            chat("The command cannot be longer than 20 chars.")
            return

        if args[2:] == []:
            chat("The text cannot be empty.")
            return

        commands[args[1]] = {
            'help': 'This command returns simple text.',
            'removeable': True,
            'reply': ' '.join(args[2:]),
            'perm': 0,
            'hidden': False
        }
        save()
        chat("Command %s has been added with message \"%s\"."%(prefix+args[1]," ".join(args[2:])))

    @staticmethod
    def removecommand(args,usr):
        if args[1:] == []:
            chat("Command name cannot be empty.")
            return
        
        if args[1].startswith(prefix):
            args[1] = args[1].strip(prefix)
            
        command = commands.get(args[1],False)

        if not command:
            chat("%s is not a command and thus cannot be removed."%(prefix+args[1]))
            return

        if not command["removeable"]:
            chat("%s is not removeable."%(prefix+args[1]))
            return

        commands.pop(args[1])
        save()
        chat("Command %s has been removed."%(prefix+args[1]))

    @staticmethod
    def commands(args,usr):
        commandList = []
        tempCommands = commands.copy()
        tempCommands["info set"] = {"perm":1,"hidden":False}
        tempCommands["timer start/stop/add/remove/split"] = {"perm":1,"hidden":False}
        for i,name in [[0,""],[1,"(helper)"],[2,"(op)"],[3,"(owner)"]]:
            for command,values in tempCommands.items():
                if values["perm"] == i and not values["hidden"]:
                    commandList.append(prefix+command+name)
            
        chat("Available commands: "+", ".join(commandList))
        
    @staticmethod
    def help(args,usr):
        if args[1:] == []:
            chat("Bot created by mateuszdrwal. For available commands do !commands. For help with a specific command do !help <command>.")
            return
        
        cmdHelp = commands.get(args[1],False)
        if not cmdHelp:
            chat("That command does not exist.")
            return

        chat(cmdHelp["help"])

    @staticmethod
    def uptime(args,usr):
        if streamUptime == "":
            chat("Stream is offline")
            return
        chat("Stream has been up for %s"%streamUptime)

    @staticmethod
    def info(args,usr):
        if args[1:] == []:
            chat(info.info)
            return
        
        if args[1] == "set":
            chat(info.set(perms,usr," ".join(args[2:])))
            save()

    @staticmethod
    def ralle(args,usr):
        if args[1:] == []:
            chat(ralle.info)
            return
        
        if args[1] == "set":
            chat(ralle.set({'rallekralle11':1},usr," ".join(args[2:])))
            save()

    @staticmethod
    def permissions(args,usr):
        if args[1:] == []:
            permissions = perms.get(usr,0)
        else:
            permissions = perms.get(args[1],0)
            usr = args[1]
        
        if permissions == 0:
            chat("%s does not have special permissions."%usr)
            return

        if permissions == 1:
            chat("%s is a helper."%usr)
            return

        if permissions == 2:
            chat("%s is an op."%usr)
            return

        if permissions == 3:
            chat("%s is an owner."%usr)
            return

    @staticmethod
    def setperms(args,usr):

        if args[1:] == []:
            chat("The first argument must be a username.")
            return
        
        try:
            int(args[2])
        except:
            chat("The second argument must be an int. 0:normal 1:helper 2:op")
            return

        if int(args[2]) > 2:
            chat("Owner permissions are hardcoded. You can not set them.")
            return

        perms[args[1]] = int(args[2])
        chat("user %s has been granted %s permissions."%(args[1],["normal","helper","operator"][int(args[2])]))

    @staticmethod
    def shutdown(args,usr):
        global shutdown
        log("Manual shutdown")
        chat("Manual shutdown")
        shutdown = 2
    
    @staticmethod
    def reboot(args,usr):
        global shutdown
        log("Manual reboot")
        chat("Manual reboot")
        shutdown = 1

    @staticmethod
    def update(args,usr):
        global shutdown
        log("udpate")
        chat("updating bot...")
        shutdown = 3

    @staticmethod
    def brianstime(args,usr):
        nyctime1 = json.loads(uf.url("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
        chat("Brians timezone is now %s"%nyctime1.get("fulldate").replace(" -0500",""))

    @staticmethod
    def timer(args,usr):
        global ss3,ss3val,perm
        if args[1:] == []:
            chat(timer.status())
            return

        if not uf.perm(perms,usr,1):
            chat("You do not have permission to do that!")
            return
        
        if args[1] == "start":
            if len(args[1:]) < 2:
                chat("Usage: !timer start <title>")
                return
            chat(timer.start(args[2],ss3,ss3val))

        if args[1] == "stop":
            if len(args[1:]) < 2:
                chat("Usage: !timer stop <message>")
                return
            chat(timer.stop(args[2],ss3,ss3val))

        if args[1] == "add":
            if len(args[1:]) < 2:
                chat("Usage: !timer add <seconds>")
                return
            chat(timer.add(args[2]))

        if args[1] == "remove":
            if len(args[1:]) < 2:
                chat("Usage: !timer remove <seconds>")
                return
            chat(timer.remove(args[2]))

        if args[1] == "split":
            if len(args[1:]) < 2:
                chat("Usage: !timer split <split>")
                return
            chat(timer.split(args[2],ss3,ss3val))

    @staticmethod
    def wiki(args,usr):
        global wiki
        if args[1:] == []:
            chat("usage: !wiki <atricle>")
            return

        if args[1] == "set":
            if not uf.perm(perms,usr,1):
                chat("You do not have permission to do that!")
                return
            
            if requests.get("http://%s.gamepedia.com"%args[2]).url == "http://www.gamepedia.com/":
                chat("could not find that wiki on gamepedia")
                return

            chat("successfully set the %s wiki as the wiki"%args[2])
            wiki = args[2]
            save()
            return

        searchResult = requests.get("http://%s.gamepedia.com/api.php?action=opensearch&search=%s"%(wiki," ".join(args[1:]))).json()
        if searchResult[3] == []:
            chat("No results for that query were found.")
            return

        chat("I found an article about %s:%s"%(searchResult[1][0],searchResult[3][0]))

    @staticmethod
    def crash(args,usr):
        if not uf.perm(perms,usr,3):
            print("https://goo.gl/21YA1b")
        raise Exception("Manual debug crash")
    
#--------------------
#     functions
#--------------------
def log(string,level="info"):
    string = str(datetime.datetime.now())+": "+string
    print(string)
    if level=="debug":
        logging.debug(string)
    if level=="info":
        logging.info(string)
    if level=="warning":
        logging.warning(string)
    if level=="error":
        logging.error(string)
    if level=="critical":
        logging.critical(string)
    
def save(override=False,reboot=False,update=False):
    global channel,info,perms,records,mvd,md,shutdown,timer
    if shutdown and not override:
        log("not saving, about to shut down")
        return
    try:
        f = open("data.py","w")
        f.write("channelName = \""+data.channelName+"\"\n")
        f.write("info = \""+info.info+"\"\n")
        f.write("ralle = \""+ralle.info+"\"\n")
        f.write("quote = "+str(quote.array)+"\n")
        f.write("joke = "+str(joke.array)+"\n")
        f.write("commands = "+str(commands).replace("{","{\n").replace("',","',\n").replace("e,","e,\n").replace("},","},\n").replace("0,","0,\n").replace("1,","1,\n").replace("2,","2,\n").replace("3,","3,\n").replace("}","\n}")+"\n")
        f.write("perms = "+str(perms).replace("{","{#0: normal 1: helper 2: op 3: owner\n").replace(",",",\n").replace("}","\n}")+"\n")
        f.write("mvd = "+str(mvd)+"\n")
        f.write("md = "+str(md)+"\n")
        f.write("streamtime = "+str(streamtime)+"\n")
        f.write("savedAt = \""+str(datetime.datetime.date(datetime.datetime.now()))+"\"\n")
        f.write("reboot = "+str(reboot)+"\n")
        f.write("update = "+str(update)+"\n")
        f.write("timerActive = "+str(timer.active)+"\n")
        f.write("timerStarted = "+str(timer.started)+"\n")
        f.write("wiki = \""+wiki+"\"\n")
        f.close()
        log("saved")
    except Exception as error:
        log(error)
        log("saving failed. recovering backup...")
        os.system("sudo cp dataBackup.py data.py")
        log("backup recovered")
    os.system("sudo cp data.py dataBackup.py")

def chat(msg):
    global s,channel,lastChat
    if msg == lastChat:
        msg = str(msg)+" ."
    s.send(("PRIVMSG #%s :%s\r\n"%(data.channelName,msg)).encode("utf-8"))
    #log(str(msg)+"\r\n")
    lastChat = msg

def isWord(word):
    allowedChars = string.ascii_letters
    word2 = ""
    for char in word:
        if char in allowedChars:
            word2 += char
    
    if dic.check(word2):
        return word2
    return ""

#--------------------
#     threads
#--------------------
def spreadsheetUpdater(): #handles all spreadsheet vars and updating
    global ss,ss2,ss3,ssval,ss2val,ss3val,gs,sss,er,shutdown,spreadsheetUpdaterHB
    try:
        while True:
            spreadsheetUpdaterHB = time.time()
            try:
                ss3 = sss.worksheet("TimerSplits")
                ss2 = sss.worksheet("Charts")
                ss = sss.worksheet("Data")
                ssval = ss.get_all_values()
                ss2val = ss2.get_all_values()
                ss3val = ss3.get_all_values()
            except Exception as error:
                log("spreadsheet updating failed: "+str(error))
                try:
                    scope = ['https://spreadsheets.google.com/feeds']
                    credentials = ServiceAccountCredentials.from_json_keyfile_name(loginInfo.gspread, scope)
                    gs = gspread.authorize(credentials)
                    sss = gs.open("brians stream spreadsheet")
                    log("reauthed")
                except Exception as error:
                    log("reauth failed: " + str(error))
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def socketUpdater(): #necessary as socket sometimes randomly stop listening
    global s,shutdown,socketUpdaterHB
    try:
        socketTimer = time.time()
        while True:
            socketUpdaterHB = time.time()
            if socketTimer + 3600 < time.time():
                while True:
                    try:
                        socketTimer = time.time()
                        s2 = socket.socket()
                        s2.connect(("irc.twitch.tv", 6667))
                        s2.send(("PASS %s\r\n"%loginInfo.twitchPass).encode("utf-8"))
                        s2.send(("NICK %s\r\n"%loginInfo.twitchUsername).encode("utf-8"))
                        s2.send(("JOIN #%s\r\n"%channelName).encode("utf-8"))
                        break
                    except Exception as error:
                        log("failed reloading socket: %s"%str(error),"error")
                        log(traceback.format_exc(),"error")
                s = s2
            time.sleep(0.1)
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def streamCheck(): #handles most stream info like live status and uptime
    global status,streamInfo,seconds,streamtime,streamUptime,shutdown,streamCheckHB
    try:
        while True:
            streamCheckHB = time.time()
            streamInfo = json.loads(uf.url("https://api.twitch.tv/kraken/streams/%s?client_id=%s&api_version=5"%(channel, loginInfo.twitchApiId)).read().decode('utf-8'))
            if streamInfo.get("stream") == None:
                if status == True:
                    status = False
                    #to execute when stream stops, usualy about 5 minutes late
                    log("stream Stop\r\n")
                    chat("stream stopped, stream was up %s. Thanks for the stream brian!"%streamUptime)
                    streamtime += seconds
                    time.sleep(120) #to prevent buggy twitch api being buggy
                status = False
                streamUptime = ""
            else:
                if status == False:
                    status = True
                    #to execute when stream starts, usualy a minute late
                    log("stream Start\r\n")
                    chat("1, 2? 1, 2? brian is streaming!")
                    time.sleep(60) #to prevent buggy twitch api being buggy
                status = True
            
            #timezone converting madness for uptime
            if status:
                weirdTime = streamInfo.get("stream").get("created_at")
                date, times = weirdTime.split("T")
                times = times.split("Z")
                h, m, se = times[0].split(":")
                y, mo, d = date.split("-")
                dt = datetime.datetime(int(y),int(mo),int(d),int(h),int(m),int(se))
                start = time.mktime(dt.timetuple())
                seconds = time.mktime(datetime.datetime.utcfromtimestamp(time.time()).timetuple())-start
                streamUptime = uf.readableTime(seconds)
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def spreadsheetHandler(): #handles all the spreadsheet updating for data
    global spreadsheetTimer,streamtime,ss,ssval,mvd,md,ss2,shutdown,spreadsheetHandlerHB
    try:
        spreadsheetTimer = uf.nyctime().date()
        while ss2val == None:
            time.sleep(0.1)
        while True:
            spreadsheetHandlerHB = time.time()
            try:
                if uf.nyctime().date() != spreadsheetTimer: #if its time to update spreadsheet
                    log("new day")
                    strlen = str(uf.length(ssval,0)+1)
                    nostrlen = str(uf.length(ssval,8)+1)

                    ss.update_acell("M"+nostrlen,"0")
                    
                    if streamtime: #if there was a stream today
                        ss.update_acell("A"+strlen,str(spreadsheetTimer))
                        ss.update_acell("B"+strlen,str(streamtime))
                        ss.update_acell("C"+strlen,uf.readableTime(streamtime))
                        ss.update_acell("D"+strlen,str(spreadsheetTimer))
                        ss.update_acell("E"+strlen,mvd)
                        ss.update_acell("F"+strlen,str(spreadsheetTimer))
                        ss.update_acell("G"+strlen,int(md/(streamtime/60/60)))
                        ss.update_acell("M"+nostrlen,"1")

                    ss.update_acell("H"+nostrlen,str(spreadsheetTimer))
                    ss.update_acell("I"+nostrlen,int(json.loads(uf.url("https://api.twitch.tv/kraken/channels/%s?client_id=%s&api_version=5"%(channel,loginInfo.twitchApiId)).read()).get("views"))-int(ss.acell("K"+str(int(nostrlen)-1)).value))#dont question the readability, it works
                    ss.update_acell("J"+nostrlen,str(spreadsheetTimer))
                    ss.update_acell("K"+nostrlen,str(int(json.loads(uf.url("https://api.twitch.tv/kraken/channels/%s?client_id=%s&api_version=5"%(channel,loginInfo.twitchApiId)).read()).get("views"))))
                    ss.update_acell("L"+nostrlen,str(spreadsheetTimer))

                    
                    spreadsheetTimer = uf.nyctime().date()
                    mvd = 0
                    md = 0
                    streamtime = 0
                    log("spreadsheet updated, rebooting bot...")
                    chat("daily bot reboot...")
                    shutdown = 1

                ss2.update_acell("B3",uf.readableTime(uf.largest(uf.getColumn(ssval,2))))
                ss2.update_acell("C3",uf.largest(uf.getColumn(ssval,5)))
                ss2.update_acell("D3",uf.streak(uf.getColumn(ssval,13)))
                num = 0
                for i in range(0,len(uf.getColumn(ssval,2))):
                    num += int(uf.getColumn(ssval,2)[i])
                num = num / len(uf.getColumn(ssval,2))
                ss2.update_acell("E3",uf.readableTime(num))
                ss2.update_acell("B6",uf.largest(uf.getColumn(ssval,7)))
                ss2.update_acell("C6",uf.largest(uf.getColumn(ssval,9)))
            except Exception as error:
                pass
                #log(error)
                
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def recordsHandler():
    global streamInfo,seconds,mvd,shutdown,recordsHandlerHB
    try:
        while True:
            recordsHandlerHB = time.time()
            try:
                if int(streamInfo.get("stream").get("viewers")) > mvd:
                        mvd = int(streamInfo.get("stream").get("viewers"))
            except:
                time.sleep(10)
            time.sleep(0.1)
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def responseHandler(): #handles socket responses
    global method,s,commands,md,status,usrTableAdd,wordTableAdd,shutdown,responseHandlerHB
    try:
        pingTimer = time.time()
        while True:
            responseHandlerHB = time.time()
            response = s.recv(1024).decode("utf-8")
            #print(response)
            if not response:
                continue
            
            if response == "PING :tmi.twitch.tv\r\n":
                s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                continue
            try:
                username = re.search(r"\w+", response).group(0)
            except:
                continue
            
            message = CHAT_MSG.sub("", response)
            message = message.replace("\r\n","")
            message2,message = message,""
            
            for char in message2:
                if char in string.printable:
                    message += char
            
            messageSplit = message.split(" ")
            messageSplit[0] = messageSplit[0].strip(prefix)

            if status:
                md += 1
                for word in message.split(" "):
                    if isWord(word) != "":
                        usrTableAdd.append(username.lower())
                    wordTableAdd.append(isWord(word))

            if message.startswith(prefix):
                log(messageSplit[0])
                try:
                    method = getattr(botCommands, messageSplit[0], False)
                except UnicodeEncodeError:
                    chat("verry funny %s"%username)
                    continue

                if method:
                    if uf.perm(perms,username,commands.get(method.func_name)["perm"]):
                        method(messageSplit,username)
                        continue
                    chat("You do not have permission to use that command!")
                    continue

                command = commands.get(messageSplit[0],False)
                if command:
                    chat(command["reply"])
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def tableUpdater():
    global usrTable,wordTable,usrTableAdd,wordTableAdd,ss2val,auth,shutdown,tableUpdaterHB
    tableUpdaterHB = time.time()
    try:
        while ss2val == None:
            time.sleep(0.1)
        usrTable.init(10,9,ss2val)
        wordTable.init(13,9,ss2val)
        while True:
            tableUpdaterHB = time.time()
            
            for usr in usrTableAdd:
                usrTable.add(usr)

            usrTableAdd = []
            
            for word in wordTableAdd:
                if word != "":
                    wordTable.add(word)

            wordTableAdd = []

            usrTable.update(ss2)
            wordTable.update(ss2)

            time.sleep(3500)
    except Exception as error:
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

def heartbeatHandler():
    global shutdown,spreadsheetUpdaterHB,socketUpdaterHB,streamCheckHB,spreadsheetHandlerHB,recordsHandlerHB,responseHandlerHB,tableUpdaterHB
    time.sleep(15)
    try:
        while True:
            if shutdown:
                time.sleep(10)
                continue
            for heartbeat,name in [(spreadsheetUpdaterHB,"spreadsheetUpdater"),(socketUpdaterHB,"socketUpdater"),(streamCheckHB,"streamCheck"),(spreadsheetHandlerHB,"spreadsheetHandler"),(recordsHandlerHB,"recordsHandler"),(responseHandlerHB,"responseHandler")]:
                if time.time() - heartbeat > 300:
                    log("thread %s has not sent a heartbeat for 5 minutes, attempting reboot..."%name)
                    chat("thread %s has not sent a heartbeat for 5 minutes, attempting reboot..."%name)
                    shutdown = 1
                    time.sleep(100)
            time.sleep(1)
    except Exception as error:
        import traceback
        traceback.print_exc()
        log("error in thread "+threading.currentThread().name+": "+str(error),"error")
        log(traceback.format_exc(),"error")
        chat("error in thread "+threading.currentThread().name+": '%s'. attempting reboot..."%str(error))
        shutdown = 1

save()
#--------------------
#initializing threads
#--------------------
threads = []
for i,func in [[0,spreadsheetUpdater],[1,socketUpdater],[2,streamCheck],[3,spreadsheetHandler],[4,recordsHandler],[5,responseHandler],[6,tableUpdater],[7,heartbeatHandler]]:
    threads.append(threading.Thread(target=func,name=func.func_name))
    threads[i].daemon = True
    threads[i].start()

if data.update:
    log("Update complete")
    chat("Update complete")

elif data.reboot:
    log("Reboot complete")
    chat("Reboot complete")
    
if not debug:
    while not shutdown:
        time.sleep(1)
        
    if shutdown == 1:
        log("rebooting bot...")
        time.sleep(5)
        save(True,True)
    elif shutdown == 2:
        log("shutting down bot...")
        time.sleep(5)
        save(True,False)
    elif shutdown == 3:
        log("updating down bot...")
        time.sleep(5)
        save(True,True,True)
    else:
        raise Exception("shutdown variable is neither 1 nor 2 nor 3 at shutdown")

    log("shutdown")

    
