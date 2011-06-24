#!/usr/bin/env python
"""A simple GUI to generate metadata files for pyTivo in batch."""

from Tkinter import * # @UnusedWildImport
from thetvdbapi import TheTVDB
from tkFileDialog import askopenfilenames
import math
import os

def ScrollingListbox(parent, **kwargs):
  frame = Frame(parent)
  scrollbar = Scrollbar(frame, orient=VERTICAL)
  listbox = Listbox(frame, yscrollcommand=scrollbar.set, **kwargs)
  scrollbar.config(command=listbox.yview)
  scrollbar.pack(side=RIGHT, fill=Y)
  listbox.pack(side=LEFT, fill=BOTH, expand=1)

  return frame, listbox

class App:
  def __init__(self, master):
    self.db = TheTVDB('D454AC0B0E1A24DE')
    self.path = ''
    self.filenames = []

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

    frame, self.shows_listbox = ScrollingListbox(master)
    frame.grid(row=10, column=0, columnspan=2)
    self.shows_listbox.bind('<Return>', self.pickShow)

    self.select_show_button = Button(master, text='Pick Show',
        command=self.pickShow, state=DISABLED)
    self.select_show_button.grid(row=20, column=0, columnspan=2)

    # Show (seasons and) episodes.
    Label(master, text='Episodes').grid(row=0, column=10)

    frame, self.episodes_listbox = ScrollingListbox(master, selectmode=EXTENDED)
    frame.grid(row=10, column=10)

    # Files.
    browse_button = Button(master, text='Browse', command=self.browse)
    browse_button.grid(row=0, column=20)

    frame, self.files_listbox = ScrollingListbox(master)
    frame.grid(row=10, column=20)

    # Go!
    self.go_button = Button(master, text='Write Metadata', command=self.write)
    self.go_button.grid(row=20, column=20)

    Message(master, text='Pick a set of episodes, and files.  Press go.'
        ).grid(row=20, column=10)

  def browse(self):
    filenames = askopenfilenames()

    self.go_button.config(state=(filenames and NORMAL or DISABLED))

    self.path = ''
    if filenames:
      self.path = os.path.dirname(filenames[0])
      path_len = len(self.path) + 1
      self.filenames = [x[path_len:] for x in filenames]

      print self.path
      print self.filenames

    self.files_listbox.delete(0, END)
    for filename in self.filenames:
      self.files_listbox.insert(END, filename)

  def pickShow(self, unused_event=None):
    show_name = self.shows_listbox.selection_get()
    show, episodes = self.db.get_show_and_episodes(self.show_ids[show_name])  # @UnusedVariable
    self.episodes = dict((ep.id, ep) for ep in episodes)

    max_season = max(int(x.season_number) for x in episodes)
    season_digits = math.log(float(max_season), 10) + 1
    max_episode = max(int(x.episode_number) for x in episodes)
    episode_digits = math.log(float(max_episode), 10) + 1

    pattern = 'S%%0%ddE%%0%dd %%s' % (season_digits, episode_digits)
    self.episodes_listbox.delete(0, END)
    for episode in episodes:
      self.episodes_listbox.insert(END, pattern % (
          int(episode.season_number), int(episode.episode_number),
          episode.name))

    self.episodes_listbox.selection_set(0, 0)
    self.episodes_listbox.focus()

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

  def write(self):
    pass

if __name__ == '__main__':
  root = Tk()
  app = App(root)
  root.mainloop()
