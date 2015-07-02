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

import datetime
import fcntl  # TODO: use GtkApplication instead
import json
import sys
import webbrowser

JSON_FILENAME = "job_adverts.json"

LOCK_FILENAME = ".lock"  # TODO: use GtkApplication instead

# CONFIG

TREE_VIEW_COLUMN_LABEL_LIST = ["Url", "Tooltip", "Category", "Organization", "Score", "Date", "Title"]
JOB_SEARCH_TREE_VIEW_COLUMN_LABEL_LIST = ["Url", "Tooltip", "Name", "Category", "Last visit", "Today status"]

CATEGORY_LIST = ["Entrprise", "IR/IE", "PostDoc"]

DEFAULT_SCORE = 5

# {"url": {"label": "", "category": ""}, ...}
JOB_ADVERT_WEB_SITES = {
        "http://www.inria.fr/institut/recrutement-metiers/offres": {"label": "Inria", "category": "IR/IE"},
        "https://flowers.inria.fr/jobs/":          {"label": "Inria - Flowers team", "category": "IR/IE"},
        "http://www.ademe.fr/lademe-recrute":      {"label": "Ademe", "category": "IR/IE"},
        "http://moorea.cea.fr/Web/ListeDoss.aspx": {"label": "CEA",   "category": "IR/IE"},
        "https://jobs.github.com/positions":       {"label": "GitHub Jobs", "category": "Entrprise"},
        "http://careers.stackoverflow.com/jobs":   {"label": "Stackoverflow Careers", "category": "Entrprise"}
    }


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

        # TODO
        # {"url": [{"date": "", "status": ""}, ...], ...}
        self.json_advert_src_database = {
                "url1": [
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"}
                    ],
                "url2": [
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"}
                    ],
                "url3": [
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"},
                        {"date": "", "status": "nc"}
                    ]
            }

        # Build the main window
        gtk.Window.__init__(self, title="Job advert logger")
        self.maximize()
        self.set_border_width(4)

        notebook_container = gtk.Notebook()
        self.add(notebook_container)

        # Add job advert container ############################################

        self.add_category_combobox = gtk.ComboBoxText()
        self.add_organization_entry = gtk.Entry()
        self.add_url_entry = gtk.Entry()
        self.add_title_entry = gtk.Entry()
        self.add_score_spin_button = gtk.SpinButton()
        self.add_pros_textview = gtk.TextView()
        self.add_cons_textview = gtk.TextView()
        self.add_desc_textview = gtk.TextView()

        add_widget_dict = {"category_widget": self.add_category_combobox,
                           "organization_widget": self.add_organization_entry,
                           "url_widget": self.add_url_entry,
                           "title_widget": self.add_title_entry,
                           "score_widget": self.add_score_spin_button,
                           "pros_widget": self.add_pros_textview,
                           "cons_widget": self.add_cons_textview,
                           "desc_widget": self.add_desc_textview}

        add_container = self.make_job_advert_add_and_edit_container(add_widget_dict, self.add_job_advert_cb, self.clear_job_adverts_add_form_cb)

        # Edit container ######################################################

        paned_container = gtk.Paned(orientation = gtk.Orientation.VERTICAL)

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
        select.connect("changed", self.treeview_selection_changed_cb)

        # Connect to the "row-activated" signal (double click)
        self.edit_job_advert_treeview.connect("row-activated", self.adverts_src_treeview_double_click_cb)

        # Scrolled window
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(18)
        scrolled_window.set_shadow_type(gtk.ShadowType.IN)
        scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        scrolled_window.add(self.edit_job_advert_treeview)

        # Edit box container
        self.edit_category_combobox = gtk.ComboBoxText()
        self.edit_organization_entry = gtk.Entry()
        self.edit_url_entry = gtk.Entry()
        self.edit_url_entry.set_editable(False)
        self.edit_title_entry = gtk.Entry()
        self.edit_score_spin_button = gtk.SpinButton()
        self.edit_pros_textview = gtk.TextView()
        self.edit_cons_textview = gtk.TextView()
        self.edit_desc_textview = gtk.TextView()

        edit_widget_dict = {"category_widget": self.edit_category_combobox,
                            "organization_widget": self.edit_organization_entry,
                            "url_widget": self.edit_url_entry,
                            "title_widget": self.edit_title_entry,
                            "score_widget": self.edit_score_spin_button,
                            "pros_widget": self.edit_pros_textview,
                            "cons_widget": self.edit_cons_textview,
                            "desc_widget": self.edit_desc_textview}

        edit_container = self.make_job_advert_add_and_edit_container(edit_widget_dict, self.edit_job_advert_cb, self.reset_job_adverts_edit_form_cb)

        # Add the widgets to the container
        paned_container.add1(scrolled_window)
        paned_container.add2(edit_container)

        # Job search container ################################################

        search_container = gtk.Box(orientation = gtk.Orientation.VERTICAL, spacing=6)
        search_container.set_border_width(18)

        # Creating the ListStore model
        self.job_search_liststore = gtk.ListStore(str, str, str, str, int, str)
        for url, web_site_dict in JOB_ADVERT_WEB_SITES.items():
            tooltip = url.replace('&', '&amp;')
            label = web_site_dict["label"]
            category = web_site_dict["category"]

            # self.json_advert_src_database.items()
            #status = int(self.json_advert_src_database[url].adverts_src_dict["status"])
            #today_status = self.json_advert_src_database[url][-1]["today_status"]
            num_days_since_last_visit = 0
            today_status = "nc"

            self.job_search_liststore.append([url, tooltip, label, category, num_days_since_last_visit, today_status])

        # Creating the treeview, making it use the filter as a model, and
        # adding the columns
        job_search_treeview = gtk.TreeView(self.job_search_liststore)
        for column_index, column_title in enumerate(JOB_SEARCH_TREE_VIEW_COLUMN_LABEL_LIST):
            renderer = gtk.CellRendererText()

            column = gtk.TreeViewColumn(column_title, renderer, text=column_index)

            column.set_resizable(True)       # Let the column be resizable

            if column_title in ("Url", "Tooltip"):
                column.set_visible(False) # Hide the "url" column (this column should not be displayed but is required for tooltip and webbrowser redirection)

            if column_title == "Name":
                column.set_sort_column_id(2)
            elif column_title == "Category":
                column.set_sort_column_id(3)
            elif column_title == "Last visit":
                column.set_sort_column_id(4)
            elif column_title == "Today status":
                column.set_sort_column_id(5)

            job_search_treeview.append_column(column)

        job_search_treeview.set_tooltip_column(1)  # set the tooltip

        # Connect to the "row-activated" signal (double click)
        job_search_treeview.connect("row-activated", self.adverts_src_treeview_double_click_cb)

        #select = job_search_treeview.get_selection()
        #select.connect("changed", self.treeview_selection_changed_cb)

        # Scrolled window
        adverts_src_scrolled_window = gtk.ScrolledWindow()
        adverts_src_scrolled_window.set_border_width(18)
        adverts_src_scrolled_window.set_shadow_type(gtk.ShadowType.IN)
        adverts_src_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        adverts_src_scrolled_window.add(job_search_treeview)

        search_container.pack_start(adverts_src_scrolled_window, expand=True, fill=True, padding=0)


        ###################################

        add_label = gtk.Label(label="Add")
        notebook_container.append_page(add_container, add_label)

        edit_label = gtk.Label(label="Edit")
        notebook_container.append_page(paned_container, edit_label)

        search_label = gtk.Label(label="Search")
        notebook_container.append_page(search_container, search_label)


    def make_job_advert_add_and_edit_container(self, widget_dict, save_function, clear_function):
        """
        ...
        """

        category_combobox = widget_dict["category_widget"]
        organization_entry = widget_dict["organization_widget"]
        url_entry = widget_dict["url_widget"]
        title_entry = widget_dict["title_widget"]
        score_spin_button = widget_dict["score_widget"]
        pros_textview = widget_dict["pros_widget"]
        cons_textview = widget_dict["cons_widget"]
        desc_textview = widget_dict["desc_widget"]

        # Category
        category_label = gtk.Label(label="Category")

        category_combobox.set_entry_text_column(0)
        for category in CATEGORY_LIST:
            category_combobox.append_text(category)
        category_combobox.set_active(-1)    # -1 = no active item selected

        # Organization
        organization_label = gtk.Label(label="Organization")

        # URL
        url_label = gtk.Label(label="Url")

        # Title
        title_label = gtk.Label(label="Title")

        # Score
        score_label = gtk.Label(label="Score")

        score_spin_button.set_increments(step=1, page=5)
        score_spin_button.set_range(min=0, max=5)
        score_spin_button.set_value(5)
        score_spin_button.set_numeric(True)
        score_spin_button.set_update_policy(gtk.SpinButtonUpdatePolicy.IF_VALID)

        # Pros
        pros_label = gtk.Label(label="Pros")

        pros_textview.set_wrap_mode(gtk.WrapMode.WORD)

        pros_scrolled_window = gtk.ScrolledWindow()
        pros_scrolled_window.set_border_width(3)
        pros_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        pros_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        pros_scrolled_window.add(pros_textview)

        # Cons
        cons_label = gtk.Label(label="Cons")

        cons_textview.set_wrap_mode(gtk.WrapMode.WORD)

        cons_scrolled_window = gtk.ScrolledWindow()
        cons_scrolled_window.set_border_width(3)
        cons_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        cons_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        cons_scrolled_window.add(cons_textview)

        # Description
        desc_label = gtk.Label(label="Description")

        desc_textview.set_wrap_mode(gtk.WrapMode.WORD)

        desc_scrolled_window = gtk.ScrolledWindow()
        desc_scrolled_window.set_border_width(3)
        desc_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        desc_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        desc_scrolled_window.add(desc_textview)

        # Buttons
        add_button = gtk.Button(label="Save")
        add_button.connect("clicked", save_function)

        cancel_button = gtk.Button(label="Cancel")
        cancel_button.connect("clicked", clear_function)

        # The grid container
        grid = gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(False)
        grid.set_column_spacing(12)
        grid.set_row_spacing(6)
        grid.set_border_width(18)

        # Set hexpand, vexpand, halign, valign
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        category_combobox.set_hexpand(True)

        organization_entry.set_hexpand(True)

        url_entry.set_hexpand(True)

        score_spin_button.set_hexpand(True)

        title_entry.set_hexpand(True)

        pros_scrolled_window.set_hexpand(True)
        pros_scrolled_window.set_vexpand(True)

        cons_scrolled_window.set_hexpand(True)
        cons_scrolled_window.set_vexpand(True)
        
        desc_scrolled_window.set_hexpand(True)
        desc_scrolled_window.set_vexpand(True)

        # Align labels to the right
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        category_label.set_halign(gtk.Align.END)
        organization_label.set_halign(gtk.Align.END)
        url_label.set_halign(gtk.Align.END)
        score_label.set_halign(gtk.Align.END)
        title_label.set_halign(gtk.Align.END)

        # Align labels to the left
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        pros_label.set_halign(gtk.Align.START)
        cons_label.set_halign(gtk.Align.START)
        desc_label.set_halign(gtk.Align.START)

        # Add the widgets to the container
        grid.attach(title_label,          left=0, top=0, width=1, height=1)
        grid.attach(title_entry,          left=1, top=0, width=3, height=1)

        grid.attach(category_label,       left=0, top=1, width=1, height=1)
        grid.attach(category_combobox,    left=1, top=1, width=1, height=1)
        grid.attach(organization_label,   left=2, top=1, width=1, height=1)
        grid.attach(organization_entry,   left=3, top=1, width=1, height=1)

        grid.attach(url_label,            left=0, top=2, width=1, height=1)
        grid.attach(url_entry,            left=1, top=2, width=1, height=1)
        grid.attach(score_label,          left=2, top=2, width=1, height=1)
        grid.attach(score_spin_button,    left=3, top=2, width=1, height=1)

        grid.attach(pros_label,           left=0, top=3, width=2, height=1)
        grid.attach(cons_label,           left=2, top=3, width=2, height=1)

        grid.attach(pros_scrolled_window, left=0, top=4, width=2, height=1)
        grid.attach(cons_scrolled_window, left=2, top=4, width=2, height=1)

        grid.attach(desc_label,           left=0, top=5, width=4, height=1)

        grid.attach(desc_scrolled_window, left=0, top=6, width=4, height=6)

        grid.attach(add_button,           left=0, top=13, width=2, height=1)
        grid.attach(cancel_button,        left=2, top=13, width=2, height=1)

        return grid


    def add_job_advert_cb(self, widget):
        """
        Save the "add job advert" form.
        """

        # Get data from entry widgets ###########

        category = self.add_category_combobox.get_active_text()

        organization = self.add_organization_entry.get_text()

        url = self.add_url_entry.get_text()
        tooltip = url.replace('&', '&amp;')

        title = self.add_title_entry.get_text()

        score = self.add_score_spin_button.get_value_as_int()

        pros_buffer = self.add_pros_textview.get_buffer()
        pros = pros_buffer.get_text(pros_buffer.get_start_iter(), pros_buffer.get_end_iter(), True)

        cons_buffer = self.add_cons_textview.get_buffer()
        cons = cons_buffer.get_text(cons_buffer.get_start_iter(), cons_buffer.get_end_iter(), True)

        desc_buffer = self.add_desc_textview.get_buffer()
        desc = desc_buffer.get_text(desc_buffer.get_start_iter(), desc_buffer.get_end_iter(), True)

        date = datetime.date.isoformat(datetime.date.today())

        # Check data ############################

        error_msg_list = []

        if category is None:
            error_msg_list.append("You must select a category.")

        if len(url) == 0:
            error_msg_list.append("You must enter an url.")
        elif url in self.json_database["job_adverts"]:
            error_msg_list.append("This job advert already exists in the database.")

        try:
            if score not in range(6):
                error_msg_list.append("The score must be a number between 0 and 5.")
        except:
            error_msg_list.append("The score must be a number between 0 and 5.")

        # Save data or display error ############

        if len(error_msg_list) == 0:
            job_advert_dict = {"date": date,
                               "category": category,
                               "organization": organization,
                               "title": title,
                               "score": score,
                               "pros": pros,
                               "cons": cons,
                               "desc": desc}

            # Save the job advert in the database
            self.json_database["job_adverts"][url] = job_advert_dict

            # Save the job advert in the JSON file
            with open(JSON_FILENAME, "w") as fd:
                json.dump(self.json_database, fd, sort_keys=True, indent=4)

            # Update the GtkListStore (TODO: redundant with the previous JSON data structure)
            self.liststore.append([url, tooltip, category, organization, score, date, title])

            # Clear all entries (except "category_entry")
            self.clear_job_adverts_add_form_cb()
        else:
            dialog = gtk.MessageDialog(self, 0, gtk.MessageType.ERROR, gtk.ButtonsType.OK, "Error")
            dialog.format_secondary_text("".join(error_msg_list))
            dialog.run()
            dialog.destroy()


    def clear_job_adverts_add_form_cb(self, widget=None):
        """
        Clear the current form: reset the entry widgets to their default value.
        """

        # Clear all entries except "add_category_combobox" and "add_organization_entry"
        self.add_url_entry.set_text("")
        #self.add_organization_entry.set_text("")
        self.add_title_entry.set_text("")
        self.add_score_spin_button.set_value(DEFAULT_SCORE)
        self.add_pros_textview.get_buffer().set_text("")
        self.add_cons_textview.get_buffer().set_text("")
        self.add_desc_textview.get_buffer().set_text("")


    def treeview_selection_changed_cb(self, selection):
        self.reset_job_adverts_edit_form_cb(widget=None)


    def edit_job_advert_cb(self, widget):
        """
        Save the current form.
        """

        model, treeiter = self.edit_job_advert_treeview.get_selection().get_selected()
        url = None
        if treeiter != None:
            url = self.liststore[treeiter][0]

        if url is not None:
            pass
            # TODO!!!


    def reset_job_adverts_edit_form_cb(self, widget=None, data=None):
        """
        Clear the current form: reset the entry widgets to their default value.
        """

        model, treeiter = self.edit_job_advert_treeview.get_selection().get_selected()
        url = None
        if treeiter != None:
            url = self.liststore[treeiter][0]

        if url is None:
            self.edit_url_entry.set_text("")
            self.edit_category_combobox.set_active(-1) # -1 = no active item selected
            self.edit_organization_entry.set_text("")
            self.edit_score_spin_button.set_value(0)
            self.edit_title_entry.set_text("")
            self.edit_pros_textview.get_buffer().set_text("")
            self.edit_cons_textview.get_buffer().set_text("")
            self.edit_desc_textview.get_buffer().set_text("")
        else:
            category = self.json_database["job_adverts"][url]["category"]
            organization = self.json_database["job_adverts"][url]["organization"]
            score = self.json_database["job_adverts"][url]["score"]
            title = self.json_database["job_adverts"][url]["title"]
            #date = self.json_database["job_adverts"][url]["date"]
            pros = self.json_database["job_adverts"][url]["pros"]
            cons = self.json_database["job_adverts"][url]["cons"]
            desc = self.json_database["job_adverts"][url]["desc"]

            self.edit_url_entry.set_text(url)
            self.edit_category_combobox.set_active(CATEGORY_LIST.index(category))
            self.edit_organization_entry.set_text(organization)
            self.edit_score_spin_button.set_value(score)
            self.edit_title_entry.set_text(title)
            self.edit_pros_textview.get_buffer().set_text(pros)
            self.edit_cons_textview.get_buffer().set_text(cons)
            self.edit_desc_textview.get_buffer().set_text(desc)

    def adverts_src_treeview_double_click_cb(self, tree_view, tree_path, tree_view_column):
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

