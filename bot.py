import socket,time,re,threading,json,time,math,datetime,config,os,gspread,loginInfo
from urllib2 import urlopen
from oauth2client.service_account import ServiceAccountCredentials

time.sleep(1)

channel = config.channel
info = config.info
ops = config.ops
records = config.records #viewers, time streamed
ralle = config.ralle

kill = False
CHAT_MSG=re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
status = False
start = 0
nyctime = json.loads(urlopen("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
t = datetime.datetime(nyctime.get("year"),nyctime.get("month"),nyctime.get("day"))
streamtime = 0
mvd = 0
timer = 0
timer2 = 0
delay = 720
timerStatus = 0
lastChat = ""
splits = [
	[["ks","king slime"],"C"],
	[["eoc","eye of cthulhu"],"D"],
	[["eow","boc","eater of worlds","brain of cthulhu"],"E"],
	[["qb","queen bee"],"F"],
	[["s","skeletron"],"G"],
	[["wof","wall of flesh","hardmode"],"H"],
	[["td","d","the destroyer","destroyer"],"I"],
	[["sp","skeletron prime"],"J"],
	[["tt","t","the twins","twins"],"K"],
	[["p","plantera"],"L"],
	[["g","golem"],"M"],
	[["df","duke fishron"],"N"],
	[["lc","lunatic cultist"],"O"],
	[["ml","moon lord"],"P"],
	[["gi","ga","goblin invasion","goblin army"],"Q"],
	[["pi","pirate invasion"],"R"],
	[["mm","martian madness"],"S"],
	[["ne","nights edge","night's edge"],"T"],
	[["tb","terra blade"],"U"]]

s = socket.socket()
s.connect(("irc.twitch.tv", 6667))
s.send(("PASS %s\r\n"%loginInfo.twitchPass).encode("utf-8"))
s.send(("NICK %s\r\n"%loginInfo.twitchUsername).encode("utf-8"))
s.send(("JOIN #%s\r\n"%channel).encode("utf-8"))

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(loginInfo.gspread, scope)
gs = gspread.authorize(credentials)
ss = gs.open("brians stream spreadsheet")
ss3 = ss.worksheet("TimerSplits")
ss2 = ss.worksheet("Charts")
ss = ss.worksheet("Data")

def isSplit(splitName):
    global splits
    for i in range(0,len(splits)):
        for j in range(0,len(splits[i][0])):
            if splitName == splits[i][0][j]:
                return splits[i][1]
    return ""

def readableTime(intt):
    m, sec = divmod(intt, 60)
    h, m = divmod(m, 60)
    h = int(h)
    m = int(m)
    sec = int(sec)
    if m < 10:
        m = "0"+str(m)
    if sec < 10:
        sec = "0"+str(sec)
    h = str(h)
    return "%s:%s:%s"%(h, m, sec)

def pos(int):
    return length(ss.get_all_values(),int-1)
    
def length(array,int):
##    invArray = []
##    array1 = []
##    for i in range(0,len(array)):
##        for j in range(0, len(array[i])):
##            array1.append(array[j][i])
##        invArray.append(array1)
##        array1 = []
##        
##    return invArray
    num = 0
    try:
        while True:
            if array[num][int] == "":
                raise IndexError
            num += 1
    except IndexError:
        return num

def getColumn(int):
    spreadsheet = ss.get_all_values()
    column = []
    for i in range(1,pos(int)):
        column.append(spreadsheet[i][int-1])
    return column

def streak(array):
    intt = 0
    rec = 0
    for i in range(0,len(array)):
        array[i] = int(array[i])
        if array[i] != 0:
            intt += 1
        else:
            intt = 0
        if intt > rec:
            rec = intt
    return rec

def save():
    global channel,info,ops
    f = open("config.py","w")
    f.write("channel = \""+channel+"\"\n")
    f.write("info = \""+info+"\"\n")
    f.write("ops = "+str(ops)+"\n")
    f.write("records = "+str(records)+"\n")
    f.write("ralle = \""+str(ralle)+"\"\n")
    f.close()

def chat(msg):
    global s,channel,lastChat
    if msg == lastChat:
        msg = str(msg)+" ."
    s.send(("PRIVMSG #%s :%s\r\n"%(channel,msg)).encode("utf-8"))
    #print(str(msg)+"\r\n")
    lastChat = msg

def streamStart():
    global start
    print("stream Start\r\n")
    time.sleep(60)

def streamStop():
    global start,uptime,seconds,streamtime
    print("stream Stop\r\n")
    chat("stream stop detected, stream was up %s. Thanks for the stream brian!"%uptime)
    streamtime += seconds
    start = 0
    time.sleep(120)

def isOp(nick):
    global ops
    for i in range(0,len(ops)):
        if ops[i] == nick:
            return True
    return False

def dayCheck():
    global t,streamtime,uptime2,ss,ss2,ss3,gs,mvd,nyctime
    times = 0
    while True:
        try:
            nyctime = json.loads(urlopen("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
            gs = gspread.authorize(credentials)
            ss = gs.open("brians stream spreadsheet")
            ss3 = ss.worksheet("TimerSplits")
            ss2 = ss.worksheet("Charts")
            ss = ss.worksheet("Data")
            if t != datetime.datetime(nyctime.get("year"),nyctime.get("month"),nyctime.get("day")):
                m, sec = divmod(streamtime, 60)
                h, m = divmod(m, 60)
                uptime2 = "%sh%sm%ss"%(int(h), int(m), int(sec))
                ss.update_acell("A"+str(pos(1)+1),str(t).replace("-","/").split(" ")[0])
                ss.update_acell("C"+str(pos(1)),streamtime)
                if uptime2 != "0h0m0s":
                    ss.update_acell("D"+str(pos(1)),uptime2)
                
                if streamtime != 0:
                    ss.update_acell("E"+str(pos(5)+1),str(t).replace("-","/").split(" ")[0])
                    ss.update_acell("G"+str(pos(5)),streamtime)
                    ss.update_acell("H"+str(pos(5)),uptime2)
                    
                if mvd != 0:
                    ss.update_acell("I"+str(pos(9)+1),str(t).replace("-","/").split(" ")[0])
                    ss.update_acell("J"+str(pos(9)),mvd)

                ss.update_acell("K"+str(pos(11)+1),str(t).replace("-","/").split(" ")[0])
                ss.update_acell("L"+str(pos(11)),int(json.loads(urlopen("https://api.twitch.tv/kraken/channels/lorgon?client_id=9int14hk7irvo127euzochvd0ukqomt").read()).get("views")))

                time.sleep(1000)
                nyctime = json.loads(urlopen("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
                t = datetime.datetime(nyctime.get("year"),nyctime.get("month"),nyctime.get("day"))
                streamtime = 0
                mvd = 0

                
                
            m, sec = divmod(records[1], 60)
            h, m = divmod(m, 60)
            uptime2 = "%sh%sm%ss"%(int(h), int(m), int(sec))

            col = getColumn(7)
            summ = 0
            for i in range(0,len(getColumn(7))):
                summ = int(col[i]) + summ
            summ = summ/(pos(7)-1)
            
            ss2.update_acell("B3", uptime2)
            ss2.update_acell("C3", records[0])
            ss2.update_acell("D3", streak(getColumn(3)))

            m, sec = divmod(summ, 60)
            h, m = divmod(m, 60)
            uptime2 = "%sh%sm%ss"%(int(h), int(m), int(sec))

            ss2.update_acell("E3", uptime2)
            
        except Exception as inst:
            times += 1
            print("error "+str(times))
            print inst
    if kill:
            exit()
    time.sleep(1)
    
def recordCheck():
    global streamInfo,records,kill,seconds,mvd
    while True:
        try:
            if int(streamInfo.get("stream").get("viewers")) > records[0]:
                records[0] = int(streamInfo.get("stream").get("viewers"))
                save()
            if int(streamInfo.get("stream").get("viewers")) > mvd:
                mvd = int(streamInfo.get("stream").get("viewers"))
            if seconds > records[1]:
                records[1] = seconds
                save()
        except:
            time.sleep(0.001)
        if kill:
            exit()
        time.sleep(0.1)

def streamCheck():
    global status,streamInfo,kill,seconds
    while True:
        try:
            streamInfo = json.loads(urlopen("https://api.twitch.tv/kraken/streams/%s?client_id=%s"%(channel, loginInfo.twitchApiId), timeout = 15).read().decode('utf-8'))
            if streamInfo.get("stream") == None:
                if status == True:
                    status = False
                    streamStop()
                status = False
            else:
                if status == False:
                    status = True
                    streamStart()
                status = True
            weirdTime = streamInfo.get("stream").get("created_at")
            date, times = weirdTime.split("T")
            times = times.split("Z")
            h, m, se = times[0].split(":")
            y, mo, d = date.split("-")
            dt = datetime.datetime(int(y),int(mo),int(d),int(h),int(m),int(se))
            start = time.mktime(dt.timetuple())
            seconds = time.mktime(datetime.datetime.utcfromtimestamp(time.time()).timetuple())-start
            m, sec = divmod(seconds, 60)
            h, m = divmod(m, 60)
            uptime = "%sh%sm%ss"%(h, m, sec)
        except:
            time.sleep(0.001)
        if kill:
            exit()
        time.sleep(0.1)

def responseHandler():
    global ss3,timerStatus,timer2,timer,ralle,records,response,message,username,s,channel,start,seconds,info,streamInfo,kill,uptime,status
    while True:
        response = s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            
            
            
            if message == "!info\r\n":
                chat(info)
            
            elif message.split(" ")[0] == "!info" and message.split(" ")[1] == "set":
                if isOp(username):
                    info = message.split(" ",2)[2].split("\r\n")[0]
                    chat("Info successfully changed to "+info)
                    save()
                else:
                    chat("You do not have permission to do that!")
            
            elif message == "!uptime\r\n":
                if status == True:
                    weirdTime = streamInfo.get("stream").get("created_at")
                    date, times = weirdTime.split("T")
                    times = times.split("Z")
                    h, m, se = times[0].split(":")
                    y, mo, d = date.split("-")
                    dt = datetime.datetime(int(y),int(mo),int(d),int(h),int(m),int(se))
                    start = time.mktime(dt.timetuple())
                    seconds = time.mktime(datetime.datetime.utcfromtimestamp(time.time()).timetuple())-start
                    m, sec = divmod(seconds, 60)
                    h, m = divmod(m, 60)
                    uptime = "%sh%sm%ss"%(int(h), int(m), int(sec))
                    chat("stream has been up for %s"%uptime)
                else:
                    chat("stream is offline")
        
            elif message == "!ping\r\n":
                chat("pong")

            elif message.split(" ")[0] == "!reoice":
                chat("Reoice %s!"%(message.split(" ")[1]).split("\r\n")[0])

            elif message == "!help\r\n":
                chat("Bot created by mateuszdrwal. !commands for commands.")

            elif message == "!commands\r\n":
                chat("!help, !opcommands, !info, !uptime, !ping, !reoice, !records, !shamelessplug, !briansstuff, !lifefruit, !fastcardgen, !torches, !briansspeedruns, !stats, !briantime, !timer, !splits, !leafwings")

            elif message == "!amiop\r\n":
                if isOp(username):
                    chat(username + " is indeed Op!")
                else:
                    chat(username + " is not Op.")

            elif message.split(" ")[0] == "!op":
                if isOp(username):
                    if not isOp(message.split(" ")[1].split("\r\n")[0].lower()):
                        ops.append(message.split(" ")[1].split("\r\n")[0].lower())
                        chat(message.split(" ")[1].split("\r\n")[0]+" has been Oped!")
                        save()
                    else:
                        chat("They are alredy op!")
                else:
                    chat("You do not have permission to do that!")

            elif message == "!ops\r\n":
                chat(ops)
            #elif
            elif message.split(" ")[0] == "!deop":
                if message.split(" ")[1].split("\r\n")[0].lower() == "mateuszdrwal":
                    chat("Nice try")
                else:
                    if isOp(username):
                        try:
                            ops.remove(message.split(" ")[1].split("\r\n")[0])
                            chat(message.split(" ")[1].split("\r\n")[0] + " has been Deoped!")
                            save()
                        except:
                            chat(message.split(" ")[1].split("\r\n")[0] + " is not Oped!")
                    else:
                        chat("You do not have permission to do that!")

            elif message == "!ralle\r\n":
                if username != "mbxdllfs":
                    chat(ralle)
                else:
                    chat("Hug?")
                    
            elif message == "!records\r\n":
                m1, sec1 = divmod(records[1], 60)
                h1, m1 = divmod(m1, 60)
                uptime1 = "%sh%sm%ss"%(h1, m1, sec1)
                chat("brians stream records(18 oct 2016 - now): viewers: "+str(records[0])+" most time streamed: "+uptime1)

            elif message == "!shamelessplug\r\n":
                chat("sub to the creator of this bot: TheMCmateuszdrwal")

            elif message == "!briansstuff\r\n":
                chat("youtube.com/user/lorgon111 twitter.com/lorgon111 or @lorgon111")

##            elif message == "!reboot\r\n":
##                if isOp(username):
##                    chat(".me disappears")
##                    kill = True
##                    os.system("sudo ./start.sh")
##                else:
##                    chat("You do not have permission to do that!")

            elif message == "!opcommands\r\n":
                chat("!op, !deop, !info set, !reboot, !shutdown, !timer start/stop/add/remove/split")

            elif message == "!shutdown\r\n":
                if isOp(username):
                    chat(".me disappears")
                    kill = True
                else:
                    chat("You do not have permission to do that!")

            elif message == "!lifefruit\r\n":
                chat("Lifefruit, Yum!")

            elif message == "!fastcardgen\r\n":
                chat("tulululululululululup! zingzangzum!")

            elif message == "!torches\r\n":
                chat("torches, torches, torches!")

            elif message == "!briansspeedruns\r\n":
                chat("speedrun.com/user/Lorgon111")
                
            elif message.split(" ")[0] == "!ralle" and message.split(" ")[1] == "set":
                if username == "rallekralle11":
                    ralle = message.split(" ",2)[2]
                    save()
                    chat("!ralle successfully changed to "+ralle)
                else:
                    chat("You do not have permission to do that!")

            elif message == "!fart\r\n":
                chat("*mbxdllfs farts*")
                
            elif message == "!stats\r\n":
                chat("goo.gl/RkGAic")

            elif message == "!briantime\r\n":
                nyctime1 = json.loads(urlopen("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
                chat("Brians timezone is now at %s:%s:%s"%(nyctime1.get("hours"),nyctime1.get("minutes"),nyctime1.get("seconds")))

            elif message == "!timer\r\n":
                if timer != 0:
                    chat("the timer is now at "+readableTime(time.time() - timer))
                else:
                    chat("timer is not counting")

            elif message == "!timer start\r\n":
                chat("Depreacticated. instead use \"!timer start <speedrun category/title>\"")
            
            elif message.split(" ")[0] == "!timer" and message.split(" ")[1] == "start":
                if isOp(username):
                    timer69 = timer
                    timer = time.time()
                    timer2 = -495
                    nyctime1 = json.loads(urlopen("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
                    temp = ss3.get_all_values()
                    ss3.update_acell("A"+str(length(temp,0)+1),str(datetime.datetime(int(nyctime1.get("year")),int(nyctime1.get("month")),int(nyctime1.get("day")),int(nyctime1.get("hours")),int(nyctime1.get("minutes")),int(nyctime1.get("seconds")))).replace("-","/"))
                    ss3.update_acell("B"+str(length(temp,1)+1),message.split(" ",2)[2].split("\r\n")[0])
                    timerStatus = 0
                    if timer69 == 0:
                        chat("timer started for speedrun \"%s\"" % message.split(" ",2)[2].split("\r\n")[0])
                    else:
                        chat("timer restarted for speedrun \"%s\"" % message.split(" ",2)[2].split("\r\n")[0])

                else:
                    chat("You do not have permission to do that!")

            elif message == "!timer stop\r\n":
                if isOp(username):
                    if timer != 0:
                        timerTime = readableTime(time.time() - timer)
                        ss3.update_acell("v"+str(length(ss3.get_all_values(),0)),timerTime)
                        chat("timer stopped at "+timerTime)
                        timer = 0
                        timerStatus = 0
                    else:
                        chat("timer is not counting")
                else:
                    chat("You do not have permission todefhmost- do that!")

            elif message.split(" ")[0] == "!timer" and message.split(" ")[1] == "add":
                if isOp(username):
                    if timer != 0:
                        try:
                            timer -= int(message.split(" ")[2])
                            chat("added "+str(int(message.split(" ")[2]))+" seconds to the timer")
                        except ValueError:
                            chat("That is not a valid integer!")
                    else:
                        chat("timer is not counting")
                else:
                    chat("You do not have permission to do that!")

            elif message.split(" ")[0] == "!timer" and message.split(" ")[1] == "remove":
                if isOp(username):
                    if timer != 0:
                        try:
                            timer += int(message.split(" ")[2])
                            chat("removed "+str(int(message.split(" ")[2]))+" seconds from the timer")
                        except ValueError:
                            chat("That is not a valid integer!")
                    else:
                        chat("timer is not counting")
                else:
                    chat("You do not have permission to do that!")
            elif message.split(" ")[0] == "!timer" and message.split(" ")[1] == "split":
                splitName = message.split(" ",2)[2].split("\r\n")[0].lower()
                if isOp(username):
                    if timer != 0:
                        if isSplit(splitName) != "":
                            timerTime = readableTime(time.time() - timer)
                            ss3.update_acell(isSplit(splitName)+str(length(ss3.get_all_values(),0)),timerTime)
                            chat("split %s has been created"%splitName)
                        else:
                            chat("I do not recognize that split and thus cannot create it")
                    else:
                        chat("timer is not counting")
                else:
                    chat("You do not have permission to do that!")
                    
            elif message == "!splits\r\n":
                chat("goo.gl/BVVJAL")

            elif message == "!leafwings\r\n":
                chat("\"GO VISIT LEAFWINGS DEALER\"")
        time.sleep(0.1)
        #print("1")
        if kill:
            exit()

def autoChat():
    global timer,timer2,kill,timerStatus
    while True:
        if timer != 0:
            if (time.time() - timer)-delay > timer2:
                igt = (time.time() - timer)/1440
                igt = igt - int(igt)
                if timerStatus == 0:
                    chat("@lorgon the timer is now at "+readableTime(time.time() - timer)+" midday")
                    timerStatus = 1
                else:
                    chat("@lorgon the timer is now at "+readableTime(time.time() - timer)+" midnight")
                    timerStatus = 0
                    
                timer2 = time.time() - timer
        if kill:
            exit()
        time.sleep(0.01)
        
#chat(".me appears")
thread1 = threading.Thread(target=responseHandler)
thread1.start()
thread2 = threading.Thread(target=streamCheck)
thread2.start()
thread3 = threading.Thread(target=recordCheck)
thread3.start()
thread4 = threading.Thread(target=dayCheck)
thread4.start()
#thread5 = threading.Thread(target=autoChat)
#thread5.start()
save()
