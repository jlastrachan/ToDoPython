import datetime
from datetime import date

class ToDoItem:
	## Do I want to add a completion date field?
	def __init__(self, item_text, repeat):
		self.item = item_text
		self.SetRepeat(repeat)
		self.visible = True
		
	def GetItem(self):
		return self.item
	def SetItem(self, item_text):
		self.item = item_text
	def GetRepeat(self):
		return self.repeat
	def SetRepeat(self, repeat):
		self.repeat = repeat
		self.AdjustDateList()
	def GetVisible(self):
		return self.visible
	def SetVisible(self, vis):
		self.visible = vis
	def AdjustDateList(self):
		'''Set list of dates to refresh visible based on Never/Daily/Weekly
		repeat setting. Monday = 0, Sunday = 6'''
		self.dateList = list()
		#print "repeat", self.repeat
		if self.repeat is 'Daily':
			self.dateList = [i for i in range(0,7)]
		elif self.repeat is 'Weekly':
			self.dateList = [date.today().weekday()]
	def SetSpecialInt(self, day_int):
		if day_int > -1:
			self.dateList = [day_int]
	def GetSpecialInt(self):
		if self.repeat is not 'Weekly':
			return -1
		return dateList[0]
	def GetDateList(self):
		return self.dateList
