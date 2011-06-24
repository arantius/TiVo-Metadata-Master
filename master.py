#!/usr/bin/env python
"""A simple GUI to generate metadata files for pyTivo in batch."""

from Tkinter import *  # @UnusedWildImport
from thetvdbapi import TheTVDB


class App:
  def __init__(self, master):
    self.db = TheTVDB('D454AC0B0E1A24DE')

    master.bind('<Escape>', lambda _: master.quit())
    master.bind('<Control-q>', lambda _: master.quit())

    # Search 'form' and results.
    self.search_entry = Entry(master)
    self.search_entry.grid(row=0, column=0)
    self.search_entry.insert(0, 'alias')
    self.search_entry.focus()
    self.search_entry.bind('<Return>', self.searchShows)

    search_button = Button(master, text='Search', command=self.searchShows)
    search_button.grid(row=0, column=1)

    self.shows_listbox = Listbox(master)
    self.shows_listbox.grid(row=10, column=0, columnspan=2)
    self.shows_listbox.bind('<Return>', self.pickShow)

    self.select_show_button = Button(master, text='Pick Show',
        command=self.pickShow, state=DISABLED)
    self.select_show_button.grid(row=20, column=0, columnspan=2)

    # Show (seasons and) episodes.
    Label(master, text='Episodes').grid(row=0, column=10)

    episodes_list = Listbox(master, selectmode=MULTIPLE)
    episodes_list.grid(row=10, column=10)

    # Files.
    #...

  def pickShow(self, unused_event=None):
    print '>>> pickShow() ...'
    show_name = self.shows_listbox.selection_get()
    show, episodes = self.db.get_show_and_episodes(self.show_ids[show_name])  # @UnusedVariable
    print episodes

  def searchShows(self, unused_event=None):
    # Run the query.
    query = self.search_entry.get()
    shows = self.db.get_matching_shows(query)
    self.show_ids = dict((v, k) for k, v in shows)

    # Populate the results.
    self.shows_listbox.delete(0, END)
    for name, id in self.show_ids.iteritems():
      self.shows_listbox.insert(END, name)
    self.select_show_button.config(state=(self.show_ids and NORMAL or DISABLED))

    self.shows_listbox.selection_set(0, 0)
    self.shows_listbox.focus()

if __name__ == '__main__':
  root = Tk()
  app = App(root)
  root.mainloop()
