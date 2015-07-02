#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Jérémie DECOCK (http://www.jdhp.org)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
...
"""

from gi.repository import Gtk as gtk
from gi.repository import Pango as pango

import fcntl  # TODO: use GtkApplication instead
import json
import sys
import webbrowser

import add_and_edit_container
import search_container

JSON_FILENAME = "job_adverts.json"

LOCK_FILENAME = ".lock"  # TODO: use GtkApplication instead

# CONFIG

TREE_VIEW_COLUMN_LABEL_LIST = ["Url", "Tooltip", "Category", "Organization", "Score", "Date", "Title"]

class MainWindow(gtk.Window):

    def __init__(self):

        # Load the JSON database
        self.json_database = {"job_adverts": {}, "job_searchs": {}}
        try:
            fd = open(JSON_FILENAME, "r")
            self.json_database = json.load(fd)
            fd.close()
        except:
            pass

        # Build the main window
        gtk.Window.__init__(self, title="Job advert logger")
        self.maximize()
        self.set_border_width(4)

        notebook_container = gtk.Notebook()
        self.add(notebook_container)

        # Edit container ######################################################

        paned_container = gtk.Paned(orientation=gtk.Orientation.VERTICAL)

        # The position in pixels of the divider (i.e. the default size of the top pane)
        paned_container.set_position(400)

        # Creating the ListStore model
        self.liststore = gtk.ListStore(str, str, str, str, int, str, str)
        for url, job_advert_dict in self.json_database["job_adverts"].items():
            tooltip = url.replace('&', '&amp;')
            category = job_advert_dict["category"]
            organization = job_advert_dict["organization"]
            score = job_advert_dict["score"]
            title = job_advert_dict["title"]
            date = job_advert_dict["date"]

            self.liststore.append([url, tooltip, category, organization, score, date, title])

        # Creating the treeview, making it use the filter as a model, and
        # adding the columns
        self.edit_job_advert_treeview = gtk.TreeView(self.liststore)
        for column_index, column_title in enumerate(TREE_VIEW_COLUMN_LABEL_LIST):
            renderer = gtk.CellRendererText()

            column = gtk.TreeViewColumn(column_title, renderer, text=column_index)

            column.set_resizable(True)       # Let the column be resizable

            if column_title == "Title":
                renderer.set_property("ellipsize", pango.EllipsizeMode.END)
                renderer.set_property("ellipsize-set", True)

            if column_title in ("Url", "Tooltip"):
                column.set_visible(False) # Hide the "url" column (this column should not be displayed but is required for tooltip and webbrowser redirection)

            if column_title == "Category":
                column.set_sort_column_id(2)
            elif column_title == "Organization":
                column.set_sort_column_id(3)
            elif column_title == "Score":
                column.set_sort_column_id(4)
            elif column_title == "Date":
                column.set_sort_column_id(5)
            elif column_title == "Title":
                column.set_sort_column_id(6)

            self.edit_job_advert_treeview.append_column(column)

        self.edit_job_advert_treeview.set_tooltip_column(1)  # set the tooltip

        # Connect to the "changed" signal (simple click)
        select = self.edit_job_advert_treeview.get_selection()
        select.connect("changed", self.treeViewSelectionChangedCallBack)

        # Connect to the "row-activated" signal (double click)
        self.edit_job_advert_treeview.connect("row-activated", treeview_double_click_cb)

        # Scrolled window
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(18)
        scrolled_window.set_shadow_type(gtk.ShadowType.IN)
        scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        scrolled_window.add(self.edit_job_advert_treeview)

        # Edit box container
        self.edit_container = add_and_edit_container.AddAndEditContainer(self, self.json_database, JSON_FILENAME, liststore=self.liststore, edit_mode=True, treeview=self.edit_job_advert_treeview)

        # Add the widgets to the container
        paned_container.add1(scrolled_window)
        paned_container.add2(self.edit_container)

        # Add job advert container ############################################

        self.add_container = add_and_edit_container.AddAndEditContainer(self, self.json_database, JSON_FILENAME, liststore=self.liststore, edit_mode=False)

        # Job search container ################################################

        search_job_adverts_container = search_container.SearchContainer()

        ###################################

        add_label = gtk.Label(label="Add")
        notebook_container.append_page(self.add_container, add_label)

        edit_label = gtk.Label(label="Edit")
        notebook_container.append_page(paned_container, edit_label)

        search_label = gtk.Label(label="Search")
        notebook_container.append_page(search_job_adverts_container, search_label)


    def treeViewSelectionChangedCallBack(self, selection):
        self.edit_container.clearCallBack()


def treeview_double_click_cb(tree_view, tree_path, tree_view_column):
    """Inspired from http://stackoverflow.com/questions/17109634/hyperlink-in-cellrenderertext-markup"""
    model = tree_view.get_model()
    url = model[tree_path][0]
    webbrowser.open(url)


def main():

    # Acquire an exclusive lock on LOCK_FILENAME
    fd = open(LOCK_FILENAME, "w")  # TODO: use GtkApplication instead

    try:  # TODO: use GtkApplication instead
        # LOCK_EX = acquire an exclusive lock on fd
        # LOCK_NB = make a nonblocking request
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # TODO: use GtkApplication instead

        ###################################

        window = MainWindow()

        window.connect("delete-event", gtk.main_quit) # ask to quit the application when the close button is clicked
        window.show_all()                             # display the window
        gtk.main()                                    # GTK+ main loop

        ###################################

        # LOCK_UN = unlock fd
        fcntl.flock(fd, fcntl.LOCK_UN)  # TODO: use GtkApplication instead
    except IOError:  # TODO: use GtkApplication instead
        #print(LOCK_FILENAME + " is locked ; another instance is running. Exit.")
        dialog = gtk.MessageDialog(parent=None, flags=0, message_type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.OK, message_format="Another instance is running in the same directory")
        dialog.format_secondary_text("Exit.")
        dialog.run()
        dialog.destroy()

        sys.exit(1)


if __name__ == '__main__':
    main()

