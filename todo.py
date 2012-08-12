#!/usr/bin/env python

import sys
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
except:
	print "Could not import gtk and gtk.glade...Exiting"
	sys.exit(1)

import todoitem 
import csv
import threading
import datetime
from datetime import date
from datetime import time

class ToDoView:
	"""Handles the to do list gui"""
	
	def __init__(self):
		self.InitGlade()
		self.FileInit()
		self.UpdateGUI()
		self.UpdateItems()
		
		
	def InitGlade(self):
		'''Set up all widget pointers and connect action events'''
		#Set the Glade file
		self.gladefile = "todo.glade"  
	        self.wTree = gtk.glade.XML(self.gladefile) 
		
		#Get the Main Window, and connect events
		self.window = self.wTree.get_widget("main_window")
		
		dic = { "on_new_view_btn_clicked" : self.NewItem,
			"on_edit_view_btn_clicked" : self.EditItem,
			"on_delete_view_btn_clicked" : self.DeleteItem,
			"on_ok_button_clicked" : self.SaveItem,
			"on_cancel_btn_clicked" : self.Cancel,
			"on_keep_repeat_btn_clicked" : self.KeepRepeat,
			"on_save_list_btn_clicked": self.SaveAndExit,
			"on_dont_save_btn_clicked": self.JustExit,
			"on_delete_btn_clicked" : self.Delete,
			"on_main_window_delete_event" : self.SendExit,
			"on_row_activated" : self.HandleSelectionChange,
			"on_main_window_destroy" : self.Exit }
		
		self.wTree.signal_autoconnect(dic)
		
		#collect widget pointers
		self.WidgetPtrs = dict()
		self.WidgetPtrs["item_view"] 		= self.wTree.get_widget("item_view")
		self.WidgetPtrs["delete_view"] 		= self.wTree.get_widget("delete_view")
		self.WidgetPtrs["save_view"] 		= self.wTree.get_widget("save_view")
		
		self.WidgetPtrs["list_combo_box"] 	= self.wTree.get_widget("list_combo_box")
		self.WidgetPtrs["repeat_combo_box"] 	= self.wTree.get_widget("repeat_combo_box")
		self.WidgetPtrs["item_entry"] 		= self.wTree.get_widget("item_entry")
		
		#set defaults for new item view
		self.WidgetPtrs["list_combo_box"].set_active(0)
		self.WidgetPtrs["repeat_combo_box"].set_active(0)
		
		self.WidgetPtrs["item_view"].hide()
		self.WidgetPtrs["delete_view"].hide()
		self.WidgetPtrs["save_view"].hide()

		#set up internal lists for tree view
		self.lists = ["School Work", "Other Work", "Tests", "Other"]
		self.items_dict = dict()
		for list_name in self.lists:
			self.items_dict[list_name] = list()
		
		#organize treeviews, treestores
		self.tree_views = dict()
		self.tree_views["School Work"] 	= self.wTree.get_widget("school_work_view")
		self.tree_views["Other Work"] 	= self.wTree.get_widget("other_work_view")
		self.tree_views["Tests"]	= self.wTree.get_widget("tests_view")
		self.tree_views["Other"] 	= self.wTree.get_widget("other_view")
		
		for view in self.tree_views.keys():
			self.tree_views[view].set_model(gtk.ListStore(str, int))
			column = gtk.TreeViewColumn()
			cell_renderer = gtk.CellRendererText()
			column.pack_start(cell_renderer, False)
			column.add_attribute(cell_renderer, "text", 0)
			self.tree_views[view].append_column(column)
	def FileInit(self):
		'''Init from saved items'''
		f = open("init.txt", 'rb')
		reader = csv.reader(f)
		for row in reader:
			# format is [task, list_name, repeat, visible, int day of repeat for weekly]
			#print row
			task, list_name, repeat, visible, day_int = row
			visible = bool(visible)
			day_int = int(day_int)
			#print visible, day_int
			item = todoitem.ToDoItem(task, repeat)
			item.SetVisible(visible)
			item.SetSpecialInt(day_int)
			self.items_dict[list_name].append(item)

	def NewItem(self, widget):
		self.WidgetPtrs["item_view"].show()
		
	def EditItem(self, widget):	
		'''find selected item and set dialog values to this'''
		
		pass
	def DeleteItem(self, widget):
		self.WidgetPtrs["delete_view"].show()
	def SaveItem(self, widget):
		''' do you save a new item or modify existing one?'''
		list_name = self.WidgetPtrs["list_combo_box"].get_active_text()
		item_name = self.WidgetPtrs["item_entry"].get_text()
		repeat    = self.WidgetPtrs["repeat_combo_box"].get_active_text()
		
		if list_name is "" or item_name is "" or repeat is "":
			self.WidgetPtrs["item_view"].hide()
			return
		
		new_item = todoitem.ToDoItem(item_name, repeat)
		self.items_dict[list_name].append(new_item)
		self.UpdateGUI()
		
		#self.WidgetPtrs["item_view"].destroy()
		# clear out entries
		self.WidgetPtrs["list_combo_box"].set_active(0)
		self.WidgetPtrs["item_entry"].set_text("")
		self.WidgetPtrs["repeat_combo_box"].set_active(0)
		
		self.WidgetPtrs["item_view"].hide()
		self.SaveList()
		
	def UpdateGUI(self):
		#print self.items_dict
		for list_name in self.tree_views.keys():
			tree_view_widget = self.tree_views[list_name]
			tree_store = tree_view_widget.get_model()
			tree_store.clear()
			
			for i, item in enumerate(self.items_dict[list_name]):
				if item.GetVisible():
					tree_store.append([item.GetItem(), i])
			
			#print "updated", list_name
			
	def Cancel(self,widget):
		widget.get_toplevel().hide()
	def SendExit (self, widget, event):
		print "called send exit"
		self.WidgetPtrs["save_view"].show()
		self.window.show()
	def Exit(self,widget):
		print "called exit"
		self.WidgetPtrs["save_view"].show()
	def KeepRepeat(self,widget):
		list_name, model, it = self.GetSelection()
		item_str, index = model.get(it, 0, 1)
		self.items_dict[list_name][index].SetVisible(False)
		self.UpdateGUI()
		widget.get_toplevel().hide()
		self.SaveList()
		
	def Delete (self, widget):
		'''actually deletes item'''
		list_name, model, it = self.GetSelection()
		item_str, index = model.get(it, 0, 1)
		self.items_dict[list_name].pop(index)
		self.UpdateGUI()
		widget.get_toplevel().hide()
		self.SaveList()
		
	def SaveAndExit(self, widget):
		'''save list for next startup'''
		self.SaveList()
		#gtk.main_quit(self, widget)	
	def JustExit (self, widget):
		'''dont save changes'''
		pass
		#gtk.main_quit(self, widget)
	def SaveList (self):
		'''saves all items into csv file'''
		f = open("init.txt", 'wb')
		writer = csv.writer(f)
		for list_name in self.items_dict.keys():
			for item in self.items_dict[list_name]:
				writer.writerow([item.GetItem(), list_name, item.GetRepeat(), item.GetVisible(), item.GetSpecialInt()])
	def HandleSelectionChange(self, widget):
		#print "Row activated"
		for view in self.tree_views.items(): # items() returns [(key, value) ...]
			#print view
			if view[1] is not widget:
				# unselect so only one selected at a time
				selection = view[1].get_selection()
				selection.unselect_all()
	def GetSelection(self):
		'''Returns list name and index of currently selected node'''
		for list_name, view in self.tree_views.items():
			selection = view.get_selection()
			model, it = selection.get_selected()
			if it is not None:
				return list_name, model, it
		return None, None
	def UpdateItems(self):
		print "updating items"
		today = date.today().weekday()
		for list_name, item_list in self.items_dict.items():
			for item in item_list:
				if not item.GetVisible():
					dateList = item.GetDateList()
					if today in dateList:
						item.SetVisible(True)
		self.UpdateGUI()
if __name__ == "__main__":
	todo = ToDoView()
#	last_time_run = datetime.today()
	while (1):
		gtk.main_iteration(False)
		#if datetime.today()
	#gtk.main()

