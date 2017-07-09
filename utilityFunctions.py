import json,threading
from datetime import datetime
from urllib2 import urlopen
class utilityFunctions:
	
	def isSplit(self,splits,splitName): #check if string is a valid split, if yes return column letter from spreadsheet
		for i in range(0,len(splits)):
			for j in range(0,len(splits[i][0])):
				if splitName == splits[i][0][j]:
					return splits[i][1]
		return ""

	def readableTime(self,timestamp): #converts timestamp into readable time
		"""input amount of seconds to get readable time string"""
		m, sec = divmod(int(timestamp), 60)
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

	def length(self,array,int): #returns number of rows at a specific column in a 2D array
		num = 0
		try:
			while True:
				if array[num][int] == "":
					raise IndexError
				num += 1
		except IndexError:
			return num

	def getColumn(self,spreadsheet,int): #returns a specific column in a 2D array
		column = []
		for i in range(1,self.length(spreadsheet,int-1)):
			column.append(spreadsheet[i][int-1])
		return column

	def getFullColumn(self,spreadsheet,int): #same as ^ but does include empty spaces
		column = []
		for i in range(1,len(spreadsheet)):
			column.append(spreadsheet[i][int-1])
		return column
	
	def streak(self,array): #returns the highest number of "items in a row" that are not 0
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

	def perm(self,perm,nick,level): #returns True if nick is in the ops array
		"""perm: input variable called perms unless you know what you are doing
nick: input the username to check
level: input the lowest permission level required
returns bool depending on if nick has perms"""
		if perm.get(nick,0) >= level:
			return True
		return False

	def nyctime(self): #returns datetime object with nyc date and time
		nyc = json.loads(self.url("https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=America/New_York").read())
		return datetime(int(nyc.get("year")),int(nyc.get("month")),int(nyc.get("day")),int(nyc.get("hours")),int(nyc.get("minutes")),int(nyc.get("seconds")))

	def url(self,string): #returns whatever urlopen() would return retrying if gotten an error
		while True:
			try:
				return urlopen(string)
			except:
				pass

	def largest(self,array):
		num = 0
		for i in range(0,len(array)):
			if array[i] > num:
				num = array[i]
		return num
