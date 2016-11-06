class utilityFunctions:
    
    def isSplit(splits,splitName): #check if string is a valid split, if yes return column letter from spreadsheet
        for i in range(0,len(splits)):
            for j in range(0,len(splits[i][0])):
                if splitName == splits[i][0][j]:
                    return splits[i][1]
        return ""

    def readableTime(timestamp): #converts timestamp into readable time
        m, sec = divmod(timestamp, 60)
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

    def length(array,int): #returns number of rows at a specific column in a 2D array
        num = 0
        try:
            while True:
                if array[num][int] == "":
                    raise IndexError
                num += 1
        except IndexError:
            return num

    def getColumn(int): #returns a specific column in a 2D array
        spreadsheet = ss.get_all_values()
        column = []
        for i in range(1,pos(int)):
            column.append(spreadsheet[i][int-1])
        return column

    def streak(array): #returns the highest number of "items in a row" that are not 0
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

    def def isOp(nick): #returns True if nick is in the ops array
        global ops
        for i in range(0,len(ops)):
            if ops[i] == nick:
                return True
        return False
