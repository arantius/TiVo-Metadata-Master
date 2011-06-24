#!/usr/bin/env python
"""A simple GUI to generate metadata files for pyTivo in batch."""

from Tkinter import *  # @UnusedWildImport
from thetvdbapi import TheTVDB


class App:
  def __init__(self, master):
    self.db = TheTVDB('D454AC0B0E1A24DE')

    top_frame = Frame(master)
    top_frame.pack()

    # Search "form" and results.
    search_frame = Frame(top_frame)
    search_frame.pack(side=LEFT)

    search_entry_frame = Frame(search_frame)
    search_entry_frame.pack()

    self.search_entry = Entry(search_entry_frame)
    self.search_entry.pack(side=LEFT)

    search_button = Button(search_entry_frame, text="Search Shows", command=self.searchShows)
    search_button.pack(side=LEFT)

    self.search_results_list = Listbox(search_frame)
    self.search_results_list.pack(side=TOP)

    # Show (seasons and) episodes.
    episodes_frame = Frame(top_frame)
    episodes_frame.pack(side=LEFT)

    episodes_list = Listbox(episodes_frame)
    episodes_list.pack()

    # Files.
    #...

  def searchShows(self):
    print ">>> searchShows() ..."
    query = self.search_entry.get()
    print self.db.get_matching_shows(query)


if __name__ == '__main__':
  root = Tk()
  app = App(root)
  root.mainloop()
