#!/usr/bin/env python
"""A simple GUI to generate metadata files for pyTivo in batch.

(c) 2011 Anthony Lieuallen (http://arantius.com/; arantius@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from Tkinter import * # @UnusedWildImport
from thetvdbapi import TheTVDB
from tkFileDialog import askopenfilenames
from tkMessageBox import showwarning
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

    for i in xrange(3):
      master.columnconfigure(index=i, weight=1)
    master.rowconfigure(index=1, weight=1)
    master.geometry('640x480')

    # Search 'form'.
    search_frame = Frame(master)
    search_frame.grid(row=0, column=0, sticky='ew')

    search_button = Button(search_frame, text='Search', command=self.searchShows)
    search_button.pack(side=RIGHT)

    self.search_entry = Entry(search_frame)
    self.search_entry.pack(fill=X, padx=3, pady=3)
    self.search_entry.focus()
    self.search_entry.bind('<Return>', self.searchShows)

    # Search 'results'.
    frame, self.shows_listbox = ScrollingListbox(master, exportselection=0)
    frame.grid(row=1, column=0, sticky='nesw')
    self.shows_listbox.bind('<Return>', self.pickShow)

    self.select_show_button = Button(master, text='Pick Show',
        command=self.pickShow, state=DISABLED)
    self.select_show_button.grid(row=2, column=0)

    # Show (seasons and) episodes.
    Label(master, text='Episodes').grid(row=0, column=1)

    frame, self.episodes_listbox = ScrollingListbox(
        master, exportselection=0, selectmode=EXTENDED)
    frame.grid(row=1, column=1, sticky='nesw')

    # Files.
    browse_button = Button(master, text='Browse', command=self.browse)
    browse_button.grid(row=0, column=2)

    frame, self.files_listbox = ScrollingListbox(
        master, exportselection=0, selectmode=EXTENDED)
    frame.grid(row=1, column=2, sticky='nesw')

    # Go!
    self.go_button = Button(master, text='Write Metadata', command=self.write)
    self.go_button.grid(row=2, column=2)

    Message(master, text='Pick a set of episodes, and files.  Press go.'
        ).grid(row=2, column=1)

  def browse(self):
    filenames = askopenfilenames()

    self.go_button.config(state=(filenames and NORMAL or DISABLED))

    self.path = ''
    if filenames:
      self.path = os.path.dirname(filenames[0])
      path_len = len(self.path) + 1
      self.filenames = [x[path_len:] for x in filenames]

    self.files_listbox.delete(0, END)
    for filename in self.filenames:
      self.files_listbox.insert(END, filename)

    self.files_listbox.selection_set(0, END)
    self.files_listbox.focus()

  def pickShow(self, unused_event=None):
    selection_index = self.shows_listbox.curselection()
    if not selection_index:
      return
    show_name = self.shows_listbox.get(selection_index)
    show, episodes = self.db.get_show_and_episodes(self.show_ids[show_name])  # @UnusedVariable
    self.show = show
    self.episodes = {}

    max_season = max(int(x.season_number) for x in episodes)
    season_digits = math.log(float(max_season), 10) + 1
    max_episode = max(int(x.episode_number) for x in episodes)
    episode_digits = math.log(float(max_episode), 10) + 1

    pattern = 'S%%0%ddE%%0%dd %%s' % (season_digits, episode_digits)
    self.episodes_listbox.delete(0, END)
    for episode in episodes:
      key = pattern % (
          int(episode.season_number), int(episode.episode_number),
          episode.name)
      self.episodes[key] = episode
      self.episodes_listbox.insert(END, key)

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
    selected_index = self.episodes_listbox.curselection()
    if not self.episodes_listbox.size() or not selected_index:
      return showwarning('Input error', 'Pick a show.')
    episodes = [self.episodes_listbox.get(x) for x in selected_index]
    if not episodes:
      return showwarning('Input error', 'Select at least one episode.')

    selected_index = self.files_listbox.curselection()
    if not self.files_listbox.size() or not selected_index:
      showwarning('Input error', 'Browse for files.')
    filenames = [self.files_listbox.get(x) for x in selected_index]
    if not filenames:
      return showwarning('Input error', 'Select at least one file.')

    if len(episodes) != len(filenames):
      return showwarning(
          'Input error', 'Select the same number of episodes and files.')

    for i, filename in enumerate(filenames):
      episode = self.episodes[episodes[i]]

      filename = os.path.join(self.path, filename) + '.txt'
      file = open(filename, 'w')
      data = [
          'title : ' + self.show.name,
          'seriesTitle : ' + self.show.name,
          'episodeTitle : ' + episode.name,
          'episodeNumber : ' + episode.episode_number,
          'originalAirDate : ' + episode.first_aired.isoformat() + 'T00:00:00Z',
          'description : ' + episode.overview,
          'isEpisode : true',
          'seriesId : ' + self.show.zap2it_id,
          ] + [
              'vDirector : ' + d for d in episode.director
          ] + [
              'vWriter : ' + w for w in episode.writer
          ] + [
              'vSeriesGenre : ' + g for g in self.show.genre
          ] + [
              'vSeriesActor : ' + a for a in self.show.actors
          ]
      file.write('\n'.join(data))
      file.close()

if __name__ == '__main__':
  root = Tk()
  app = App(root)
  root.mainloop()
