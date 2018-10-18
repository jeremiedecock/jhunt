#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel
from PyQt5.QtWidgets import QTableView, QWidget, QPushButton, QVBoxLayout, QAbstractItemView, \
    QAction, QHeaderView, QDataWidgetMapper, QPlainTextEdit, QSplitter, QLineEdit, QHBoxLayout

from jhunt.qt.delegates.adverts import AdvertsTableDelegate
from jhunt.qt.models.adverts import AdvertsTableModel

class AdvertsTab(QWidget):

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)

        self.tabs = parent

        url_column_index = data.headers.index("URL")
        pros_column_index = data.headers.index("Pros")
        cons_column_index = data.headers.index("Cons")
        description_column_index = data.headers.index("Description")

        # Make widgets ####################################

        self.splitter = QSplitter(orientation=Qt.Vertical, parent=self)

        self.table_view = QTableView(parent=self.splitter)
        self.edition_group = QWidget(parent=self.splitter)

        self.url_edit = QLineEdit(parent=self.edition_group)
        self.pros_edit = QPlainTextEdit(parent=self.edition_group)
        self.cons_edit = QPlainTextEdit(parent=self.edition_group)
        self.description_edit = QPlainTextEdit(parent=self.edition_group)
        self.btn_add_row = QPushButton("Add a row", parent=self.edition_group)

        self.url_edit.setPlaceholderText("URL")
        self.pros_edit.setPlaceholderText("Pros")
        self.cons_edit.setPlaceholderText("Cons")
        self.description_edit.setPlaceholderText("Description")

        # Splitter ########################################

        self.splitter.addWidget(self.table_view)
        self.splitter.addWidget(self.edition_group)

        # Set layouts #####################################

        vbox = QVBoxLayout()
        vbox.addWidget(self.splitter)
        self.setLayout(vbox)

        edition_group_vbox = QVBoxLayout()
        edition_group_hbox = QHBoxLayout()
        edition_group_vbox.addWidget(self.url_edit)
        edition_group_vbox.addLayout(edition_group_hbox)
        edition_group_hbox.addWidget(self.pros_edit)
        edition_group_hbox.addWidget(self.cons_edit)
        edition_group_vbox.addWidget(self.description_edit)
        edition_group_vbox.addWidget(self.btn_add_row)
        self.edition_group.setLayout(edition_group_vbox)

        # Set model #######################################

        adverts_model = AdvertsTableModel(data, parent=self)  # TODO: right use of "parent" ?

        # Proxy model #####################################

        proxy_model = QSortFilterProxyModel(parent=self)  # TODO: right use of "parent" ?
        proxy_model.setSourceModel(adverts_model)

        self.table_view.setModel(proxy_model)
        #self.table_view.setModel(adverts_model)

        # Set the view ####################################

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)    # Select the full row when a cell is selected (See http://doc.qt.io/qt-5/qabstractitemview.html#selectionBehavior-prop )
        #self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)  # Set selection mode. See http://doc.qt.io/qt-5/qabstractitemview.html#selectionMode-prop

        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)

        self.table_view.horizontalHeader().setStretchLastSection(True)  # http://doc.qt.io/qt-5/qheaderview.html#stretchLastSection-prop

        self.table_view.setColumnHidden(url_column_index, True)
        self.table_view.setColumnHidden(pros_column_index, True)
        self.table_view.setColumnHidden(cons_column_index, True)
        self.table_view.setColumnHidden(description_column_index, True)

        delegate = AdvertsTableDelegate(data)
        self.table_view.setItemDelegate(delegate)

        # Set QDataWidgetMapper ###########################

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(proxy_model)          # WARNING: do not use `adverts_model` here otherwise the index mapping will be wrong!
        self.mapper.addMapping(self.url_edit, url_column_index)
        self.mapper.addMapping(self.pros_edit, pros_column_index)
        self.mapper.addMapping(self.cons_edit, cons_column_index)
        self.mapper.addMapping(self.description_edit, description_column_index)
        self.mapper.toFirst()                      # TODO: is it a good idea ?

        self.table_view.selectionModel().selectionChanged.connect(self.update_selection)

        # TODO: http://doc.qt.io/qt-5/qdatawidgetmapper.html#setCurrentModelIndex
        #self.table_view.selectionModel().currentRowChanged.connect(self.mapper.setCurrentModelIndex())

        # TODO: https://doc-snapshots.qt.io/qtforpython/PySide2/QtWidgets/QDataWidgetMapper.html#PySide2.QtWidgets.PySide2.QtWidgets.QDataWidgetMapper.setCurrentModelIndex
        #connect(myTableView.selectionModel(), SIGNAL("currentRowChanged(QModelIndex,QModelIndex)"),
        #mapper, SLOT(setCurrentModelIndex(QModelIndex)))

        # Set key shortcut ################################

        # see https://stackoverflow.com/a/17631703  and  http://doc.qt.io/qt-5/qaction.html#details

        # Add row action

        add_action = QAction(self.table_view)
        add_action.setShortcut(Qt.CTRL | Qt.Key_N)

        add_action.triggered.connect(self.add_row_btn_callback)
        self.table_view.addAction(add_action)

        # Delete action

        del_action = QAction(self.table_view)
        del_action.setShortcut(Qt.Key_Delete)

        del_action.triggered.connect(self.remove_row_callback)
        self.table_view.addAction(del_action)

        # Set slots #######################################

        self.btn_add_row.clicked.connect(self.add_row_btn_callback)
        #self.btn_remove_row.clicked.connect(self.remove_row_callback)

        #self.table_view.setColumnHidden(1, True)


    def update_selection(self, selected, deselected):
        sm = self.table_view.selectionModel()
        index = sm.currentIndex()
        #has_selection = sm.hasSelection()                       # TODO

        self.mapper.setCurrentIndex(index.row())                 # TODO: and when nothing is selected ???


    def add_row_btn_callback(self):
        parent = QModelIndex()                                   # More useful with e.g. tree structures

        #row_index = 0                                           # Insert new rows to the begining
        row_index = self.table_view.model().rowCount(parent)     # Insert new rows to the end

        self.table_view.model().insertRows(row_index, 1, parent)

    def remove_row_callback(self):
        parent = QModelIndex()                                   # More useful with e.g. tree structures

        # See http://doc.qt.io/qt-5/model-view-programming.html#handling-selections-in-item-views
        #current_index = self.table_view.selectionModel().currentIndex()
        #print("Current index:", current_index.row(), current_index.column())

        selection_index_list = self.table_view.selectionModel().selectedRows()
        selected_row_list = [selection_index.row() for selection_index in selection_index_list]

        #row_index = 0                                           # Remove the first row
        #row_index = self.table_view.model().rowCount(parent) - 1 # Remove the last row

        # WARNING: the list of rows to remove MUST be sorted in reverse order
        # otherwise the index of rows to remove may change at each iteration of the for loop!

        # TODO: there should be a lock mechanism to avoid model modifications from external sources while iterating this loop...
        #       Or as a much simpler alternative, modify the ItemSelectionMode to forbid the non contiguous selection of rows and remove the following for loop
        for row_index in sorted(selected_row_list, reverse=True):
            # Remove rows one by one to allow the removql of non-contiguously selected rows (e.g. "rows 0, 2 and 3")
            success = self.table_view.model().removeRows(row_index, 1, parent)
            if not success:
                raise Exception("Unknown error...")   # TODO
