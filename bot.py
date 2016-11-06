import socket,time,re,threading,json,time,math,datetime,os,gspread,loginInfo,data
from oauth2client.service_account import ServiceAccountCredentials
from utilityFunctions import utilityFunctions
from urllib2 import urlopen

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
