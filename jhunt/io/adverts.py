#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import datetime
import json
import os

from jhunt.data.adverts import AdvertsTable
from jhunt.io.lock import lock_path, unlock_path

PY_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

FILE_NAME = ".jhunt_adverts"

class AdvertsDataBase:

    def __init__(self):
        lock_path(self.path)


    def __del__(self):
        unlock_path(self.path)


    def load(self):
        """Load the JSON database."""

        json_data_dict = {}

        try:
            with open(self.path, "r") as fd:
                json_data_dict = json.load(fd)
        except FileNotFoundError:
            pass

        data = AdvertsTable()

        date_index = data.headers.index("Date")

        for key, row in json_data_dict.items():
            row[date_index] = datetime.datetime.strptime(row[date_index], PY_DATE_TIME_FORMAT)
            data.append(row)

        return data


    def save(self, data):
        """Save the JSON database."""

        json_data_list = copy.deepcopy(data._data)          # TODO !!! get each row from it's public interface

        id_index = data.headers.index("ID")
        date_index = data.headers.index("Date")

        for row in json_data_list:
            row[date_index] = row[date_index].strftime(format=PY_DATE_TIME_FORMAT)

        # Use a dict structure to have items sorted by ID automatically by the JSON parser (for some strange reason, the first and the last items are switched when a list is used)
        json_data_dict = {row[id_index]: row for row in json_data_list}

        with open(self.path, "w") as fd:
            #json.dump(json_data, fd)                           # no pretty print
            json.dump(json_data_dict, fd, sort_keys=True, indent=4)  # pretty print format


    @property
    def path(self):
        home_path = os.path.expanduser("~")                 # TODO: works on Unix only ?
        file_path = os.path.join(home_path, FILE_NAME)
        return file_path
