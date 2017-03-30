import os,data,logging,datetime,time

logging.basicConfig(filename="launcher-logs/%s.log"%str(datetime.datetime.now()),level=logging.DEBUG)

def log(string,level="debug"):
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

try:
    f = open("data.py","a")
    f.write("reboot = False\n")
    f.write("update = False\n")
    f.close()
    log("saved")
except Exception as error:
    log(error)
    log("saving failed. recovering backup...")
    os.system("sudo cp dataBackup.py data.py")
    log("backup recovered")
os.system("sudo cp data.py dataBackup.py")

while True:
    log("starting bot...")
    os.system("sudo python bot.py")
    log("bot closed")
    time.sleep(1)
    reload(data)
    if data.update:
        log("attempting update...")
        os.system("git pull")
        log("update complete")
    if not data.reboot:
        log("shutting down launcher...")
        break
    
