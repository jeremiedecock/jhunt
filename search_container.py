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

from gi.repository import Gtk as gtk

import webbrowser

# {"url": {"label": "", "category": ""}, ...}
JOB_ADVERT_WEB_SITES = {
        "http://www.inria.fr/institut/recrutement-metiers/offres": {"label": "Inria", "category": "IR/IE"},
        "https://flowers.inria.fr/jobs/":          {"label": "Inria - Flowers team", "category": "IR/IE"},
        "http://www.ademe.fr/lademe-recrute":      {"label": "Ademe", "category": "IR/IE"},
        "http://moorea.cea.fr/Web/ListeDoss.aspx": {"label": "CEA",   "category": "IR/IE"},
        "https://jobs.github.com/positions":       {"label": "GitHub Jobs", "category": "Entrprise"},
        "http://careers.stackoverflow.com/jobs":   {"label": "Stackoverflow Careers", "category": "Entrprise"}
    }

JOB_SEARCH_TREE_VIEW_COLUMN_LABEL_LIST = ["Url", "Tooltip", "Name", "Category", "Last visit", "Today status"]

class SearchContainer(gtk.Box):

    def __init__(self):

        super(SearchContainer, self).__init__(orientation=gtk.Orientation.VERTICAL, spacing=6)

        self.set_border_width(18)

        # Creating the ListStore model

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
        job_search_treeview.connect("row-activated", treeview_double_click_cb)

        #select = job_search_treeview.get_selection()
        #select.connect("changed", self.treeview_selection_changed_cb)

        # Scrolled window
        adverts_src_scrolled_window = gtk.ScrolledWindow()
        adverts_src_scrolled_window.set_border_width(18)
        adverts_src_scrolled_window.set_shadow_type(gtk.ShadowType.IN)
        adverts_src_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        adverts_src_scrolled_window.add(job_search_treeview)

        self.pack_start(adverts_src_scrolled_window, expand=True, fill=True, padding=0)


def treeview_double_click_cb(tree_view, tree_path, tree_view_column):
    """Inspired from http://stackoverflow.com/questions/17109634/hyperlink-in-cellrenderertext-markup"""
    model = tree_view.get_model()
    url = model[tree_path][0]
    webbrowser.open(url)

