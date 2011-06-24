#!/usr/bin/env python
"""A simple GUI to generate metadata files for pyTivo in batch."""

from Tkinter import *  # @UnusedWildImport
from thetvdbapi import TheTVDB


class App:
  def __init__(self, master):
    self.db = TheTVDB('D454AC0B0E1A24DE')

    master.bind('<Control-q>', lambda _: master.quit())

    # Search "form" and results.
    self.search_entry = Entry(master)
    self.search_entry.grid(row=0, column=0)
    self.search_entry.focus()
    self.search_entry.bind('<Return>', self.searchShows)

    search_button = Button(master, text="Search", command=self.searchShows)
    search_button.grid(row=0, column=1)

    self.search_results_list = Listbox(master)
    self.search_results_list.grid(row=10, column=0, columnspan=2)

    # Show (seasons and) episodes.
    Label(master, text="Episodes").grid(row=0, column=10)

    episodes_list = Listbox(master)
    episodes_list.grid(row=10, column=10)

    # Files.
    #...

  def searchShows(self, unused_event=None):
    print ">>> searchShows() ..."
    query = self.search_entry.get()
    print self.db.get_matching_shows(query)


if __name__ == '__main__':
  root = Tk()
  app = App(root)
  root.mainloop()
