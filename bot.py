import classes,socket,time,re,threading,json,time,math,datetime,os,gspread,loginInfo,data,enchant,string
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

channel = data.channel
perms = data.perms
info.info = data.info
ralle.info = data.ralle
joke.load(data.joke)
quote.load(data.quote)
commands = data.commands

#--------------------
# configuring socket
#--------------------
s = socket.socket()
s.connect(("irc.twitch.tv", 6667))
s.send(("PASS %s\r\n"%loginInfo.twitchPass).encode("utf-8"))
s.send(("NICK %s\r\n"%loginInfo.twitchUsername).encode("utf-8"))
s.send(("JOIN #%s\r\n"%channel).encode("utf-8"))

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
            'op': 0,
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
        chat("available commands: "+", ".join(prefix+command for command, values in commands.items() if not values["op"] and not values["hidden"])+" for commands for ops do %sopcommands"%(prefix))

    @staticmethod
    def opcommands(args,usr):
        chat("available opcommands: "+", ".join(prefix+command for command, values in commands.items() if values["op"] and not values["hidden"]))

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

#--------------------
#     functions
#--------------------
def save():
    global channel,info,perms,records
    try:
        f = open("data.py","w")
        f.write("channel = \""+channel+"\"\n")
        f.write("info = \""+info.info+"\"\n")
        f.write("ralle = \""+ralle.info+"\"\n")
        f.write("quote = "+str(quote.array)+"\n")
        f.write("joke = "+str(joke.array)+"\n")
        f.write("commands = "+str(commands).replace("{","{\n").replace(",",",\n").replace("}","\n}")+"\n")
        f.write("perms = "+str(perms).replace("{","{#0: normal 1: helper 2: op 3: owner\n").replace(",",",\n").replace("}","\n}")+"\n")
        f.close()
    except:
        print("saving failed. recovering backup...")
        os.system("sudo cp dataBackup.py data.py")
    os.system("sudo cp data.py dataBackup.py")

def chat(msg):
    global s,channel,lastChat
    if msg == lastChat:
        msg = str(msg)+" ."
    s.send(("PRIVMSG #%s :%s\r\n"%(channel,msg)).encode("utf-8"))
    #print(str(msg)+"\r\n")
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
    global ss,ss2,ss3,ssval,ss2val,ss3val,gs,sss,er
    ecount = 0
    er = False
    while True:
        try:
            def reloadSpreadsheets():
                global ss,ss2,ss3,ssval,ss2val,ss3val,sss,er
                try:
                    ss3 = sss.worksheet("TimerSplits")
                    ss2 = sss.worksheet("Charts")
                    ss = sss.worksheet("Data")
                    ssval = ss.get_all_values()
                    ss2val = ss2.get_all_values()
                    ss3val = ss3.get_all_values()
                except:
                    er = True

            if not uf.timeout(reloadSpreadsheets, 60):
                raise Exception("reload timed out")

            if er:
                er = False
                raise Exception("error when reloading")
                
        except Exception as error:
            import traceback
            traceback.print_exc()
            print("spreadsheet updating failed: "+str(error))
            try:
                def reauth():
                    try:
                        global sss,gs,er
                        scope = ['https://spreadsheets.google.com/feeds']
                        credentials = ServiceAccountCredentials.from_json_keyfile_name(loginInfo.gspread, scope)
                        gs = gspread.authorize(credentials)
                        sss = gs.open("brians stream spreadsheet")
                    except:
                        er = True

                if not uf.timeout(reauth, 30):
                    raise Exception("reauth timed out")
                else:
                    ss = sss.worksheet("Data")
                    ssval = ss.get_all_values()

                if er:
                    er = False
                    raise Exception("error while reauthing")

                print("reauthed")
            except Exception as error:
                print("reauth failed: " + str(error))

def socketUpdater(): #necessary as socket sometimes randomly stop listening
    global s
    socketTimer = time.time()
    while True:
        if socketTimer + 3600 < time.time():
            while True:
                try:
                    socketTimer = time.time()
                    s2 = socket.socket()
                    s2.connect(("irc.twitch.tv", 6667))
                    s2.send(("PASS %s\r\n"%loginInfo.twitchPass).encode("utf-8"))
                    s2.send(("NICK %s\r\n"%loginInfo.twitchUsername).encode("utf-8"))
                    s2.send(("JOIN #%s\r\n"%channel).encode("utf-8"))
                    break
                except:
                    pass
            s = s2
        time.sleep(0.1)

def streamCheck(): #handles most stream info like live status and uptime
    global status,streamInfo,seconds,streamtime,streamUptime
    while True:
        streamInfo = json.loads(uf.url("https://api.twitch.tv/kraken/streams/%s?client_id=%s"%(channel, loginInfo.twitchApiId)).read().decode('utf-8'))
        if streamInfo.get("stream") == None:
            if status == True:
                status = False
                #to execute when stream stops, usualy about 5 minutes late
                print("stream Stop\r\n")
                chat("stream stop detected, stream was up %s. Thanks for the stream brian!"%uptime)
                streamtime += seconds
                time.sleep(120) #to prevent buggy twitch api being buggy
            status = False
            streamUptime = ""
        else:
            if status == False:
                status = True
                #to execute when stream starts, usualy a minute late
                print("stream Start\r\n")
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

def spreadsheetHandler(): #handles all the spreadsheet updating for data
    global spreadsheetTimer,streamtime,ss,ssval,mvd,md,ss2
    spreadsheetTimer = uf.nyctime().date()
    time.sleep(10)
    while True:
        try:
            if uf.nyctime().date() != spreadsheetTimer: #if its time to update spreadsheet
                print("new day")
                strlen = str(uf.length(ssval,0)+1)
                nostrlen = str(uf.length(ssval,8)+1)

                uf.uf.updateCell(ss, "M"+nostrlen,"0")
                
                if mvd: #if there was a stream today
                    uf.uf.updateCell(ss, "A"+strlen,str(spreadsheetTimer))
                    uf.updateCell(ss, "B"+strlen,str(streamtime))
                    uf.updateCell(ss, "C"+strlen,uf.readableTime(streamtime))
                    uf.updateCell(ss, "D"+strlen,str(spreadsheetTimer))
                    uf.updateCell(ss, "E"+strlen,mvd)
                    uf.updateCell(ss, "F"+strlen,str(spreadsheetTimer))
                    uf.updateCell(ss, "G"+strlen,md)
                    uf.updateCell(ss, "M"+nostrlen,"1")

                uf.updateCell(ss, "H"+nostrlen,str(spreadsheetTimer))
                uf.updateCell(ss, "I"+nostrlen,int(json.loads(uf.url("https://api.twitch.tv/kraken/channels/lorgon?client_id=%s"%loginInfo.twitchApiId).read()).get("views"))-int(ss.acell("K"+str(int(nostrlen)-1)).value))#dont question the readability, it works
                uf.updateCell(ss, "J"+nostrlen,str(spreadsheetTimer))
                uf.updateCell(ss, "K"+nostrlen,str(int(json.loads(uf.url("https://api.twitch.tv/kraken/channels/lorgon?client_id=%s"%loginInfo.twitchApiId).read()).get("views"))))
                uf.updateCell(ss, "L"+nostrlen,str(spreadsheetTimer))

                
                spreadsheetTimer = uf.nyctime().date()
                mvd = 0
                md = 0

            uf.updateCell(ss2, "B3",uf.readableTime(uf.largest(uf.getColumn(ssval,2))))
            uf.updateCell(ss2, "C3",uf.largest(uf.getColumn(ssval,5)))
            uf.updateCell(ss2, "D3",uf.streak(uf.getColumn(ssval,13)))
            num = 0
            for i in range(0,len(uf.getColumn(ssval,2))):
                num += int(uf.getColumn(ssval,2)[i])
            num = num / len(uf.getColumn(ssval,2))
            uf.updateCell(ss2, "E3",uf.readableTime(num))
            uf.updateCell(ss2, "B6",uf.largest(uf.getColumn(ssval,7)))
            uf.updateCell(ss2, "C6",uf.largest(uf.getColumn(ssval,9)))
        except Exception as error:
            print error
            pass

def recordsHandler():
    global streamInfo,seconds,mvd
    while True:
        try:
            if int(streamInfo.get("stream").get("viewers")) > mvd:
                    mvd = int(streamInfo.get("stream").get("viewers"))
            if seconds > records[1]:
                    records[1] = seconds
                    save()
        except:
            time.sleep(10)
        time.sleep(0.1)

def responseHandler(): #handles socket responses
    global s,commands,md,status,usrTableAdd,wordTableAdd
    pingTimer = time.time()
    response = s.recv(1024).decode("utf-8")
    response = s.recv(1024).decode("utf-8")
    response = s.recv(1024).decode("utf-8")
    while True:
        response = s.recv(1024).decode("utf-8")
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
            print messageSplit[0]
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

def TableUpdater():
    global usrTable,wordTable,usrTableAdd,wordTableAdd,ss2val,auth
    while ss2val == None:
        time.sleep(0.1)
    usrTable.init(10,9,ss2val)
    wordTable.init(13,9,ss2val)
    while True:
        
        for usr in usrTableAdd:
            usrTable.add(usr)

        usrTableAdd = []
        
        for word in wordTableAdd:
            if word != "":
                wordTable.add(word)

        wordTableAdd = []

        usrTable.update(ss2)
        wordTable.update(ss2)

        time.sleep(10)
        
#--------------------
#initializing threads
#--------------------
thread1 = threading.Thread(target=spreadsheetUpdater)
thread1.start()
thread2 = threading.Thread(target=socketUpdater)
thread2.start()
thread3 = threading.Thread(target=streamCheck)
thread3.start()
thread4 = threading.Thread(target=spreadsheetHandler)
thread4.start()
thread5 = threading.Thread(target=recordsHandler)
thread5.start()
thread6 = threading.Thread(target=responseHandler)
thread6.start()
thread7 = threading.Thread(target=TableUpdater)
thread7.start()
