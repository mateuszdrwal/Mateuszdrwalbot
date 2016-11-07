import classes,socket,time,re,threading,json,time,math,datetime,os,gspread,loginInfo,data
from oauth2client.service_account import ServiceAccountCredentials
from utilityFunctions import utilityFunctions
from urllib2 import urlopen

#--------------------
#    constants
#--------------------
uf = utilityFunctions()


#--------------------
#    functions
#--------------------
def save(self):
    global channel,info,ops,records
    try:
        f = open("data.py","w")
        f.write("channel = \""+channel+"\"\n")
        f.write("info = \""+info+"\"\n")
        f.write("ops = "+str(ops)+"\n")
        f.write("records = "+str(records)+"\n")
        f.write("ralle = \""+str(ralle)+"\"\n")
        f.close()
    except:
        print("saving failed. recovering backup...")
        os.system("sudo cp dataBackup.py data.py")
    os.system("sudo cp data.py dataBackup.py")

#--------------------
#     threads
#--------------------
def spreadsheetUpdater():
    global ss,ss2,ss3,ssval,ss2val,ss3val
    while True:
        try:
            ss3 = sss.worksheet("TimerSplits")
            ss2 = sss.worksheet("Charts")
            ss = sss.worksheet("Data")
            ssval = ss.get_all_values()
            ss2val = ss2.get_all_values()
            ss3val = ss3.get_all_values()
        except:
            scope = ['https://spreadsheets.google.com/feeds']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(loginInfo.gspread, scope)
            gs = gspread.authorize(credentials)
            sss = gs.open("brians stream spreadsheet")

#--------------------
#initializing threads
#--------------------
thread1 = threading.Thread(target=spreadsheetUpdater)
thread1.start()
