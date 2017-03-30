import datetime,time,threading,socket

#==========================README==========================#
# this system for connecting to the bot is clearly broken.
# sometimes broken pipe and bad file descriptor errors come 
# up in the console of the bot upon connecting and the bot 
# cannot use the same port as it did upon reboot. any help 
# would be greatly appreciated.
#==========================================================#

status = False
address = ("192.168.1.5",55555)
perms = {}
pingTimer = time.time()-30
muted = False
reconnect = True
commands = [ 
["help","displays this help"], 
["setaddress [ip]","sets ip address of mateuszdrwalbot"], 
["setport [port]","sets port of mateuszdrwalbot"], 
["disconnect","disconnects from mateuszdrwalbot"], 
["connect","(re)connects to mateuszdrwalbot"], 
["chat [message]","make the bot say [message] in twitch chat"],
["getperms","displays everyone with special permissions"],
["setperms [username] [int]","sets the users permission level"]]

def socketHandler():
	global events,chat,buttons,s,perms,status,pingTimer
	while True:
		if not status:
			while not reconnect:
				time.sleep(1)
			s = socket.socket()
			try:
				s.connect(address)
				status = True
			except Exception as error:
				log("error while connecting: \"%s\" attempting reconnect..."%str(error),"error")
				time.sleep(3)
		else:
			try:
				response = s.recv(1024).decode("utf-8")
			except Exception as error:
				log("error while receiving: \"%s\" attempting reconnect..."%str(error),"error")
				continue
			#print(response)
			commands = response.split("END")
			for command in commands:
				if command == "":
					continue
				command, args = command.split(" ")[0]," ".join(command.split(" ",1)[1:])

				if command == "PERMS":
					perms = eval(args)
					
				elif command == "MUTED":
					muted = eval(args)
				elif command == "PING":
					pingTimer = time.time()
				elif command == "EVENT":
					log(args)
				elif command == "CHAT":
					log(args)
				elif command == "DISCONNECT":
					s.close()
					setstatus(False)

def pingChecker():
	global pingTimer,s,status
	while True:
		if status:
			if time.time()-pingTimer > 60:
				s.close()
				setstatus(False)
				log("have not recieved a ping for a minute. attempting reconnect...", "error")
	
def setstatus(s):
	global status
	if s:
		status = True
		log("connected","info")
	else:
		status = False
		log("disconnected","info")

def log(string,level=None):
	if level:
		print("%s|client: %s"%(level,string))
	else:
		print(string)

time.sleep(1)
socketThread = threading.Thread(target=socketHandler)
socketThread.start()
time.sleep(1)
pingThread = threading.Thread(target=pingChecker)
pingThread.start()

while True:
	command = input("--> ").lower()
	args = " ".join(command.split(" ")[1:])
	command = command.split(" ")[0]
	if command == "help":
		print("\nClient for connecting to Mateuszdrwalbot\n\navailable commands:\n")
		maxlen = 0
		for item in commands:
			if len(item[0]) > maxlen:
				maxlen = len(item[0])
		for command,info in commands:
			print(("{0:%s} - {1:%s}"%(maxlen,maxlen)).format(command,info))
	elif command == "setaddress":
		if len(args.split(".")) == 4 and " " not in args:
			address = (args,address[1])
			print("the address is now %s"%str(address))
		else:
			print("that is not a valid ip address")
	elif command == "setport":
		if len(args) == 5 and " " not in args:
			address = (address[0],args)
			print("the address is now %s"%str(address))
		else:
			print("that is not a valid port")
	elif command == "disconnect":
		reconnect = False
		s.send("DISCONNECT".encode("utf-8"))
		s.close()
		setstatus(False)
	elif command == "connect":
		reconnect = True