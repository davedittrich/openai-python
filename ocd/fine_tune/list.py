# -*- coding: utf-8 -*-

"""
List fine_tunes.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.lister import Lister

# Internal imports
import openai


class FineTuneList(Lister):
    """
    List fine_tunes.
    """

    logger = logging.getLogger(__name__)

    # def get_parser(self, prog_name):
    #     parser = super().get_parser(prog_name)
    #     return parser

    def take_action(self, parsed_args):  # noqa
        fine_tunes_list = openai.FineTune.list()
        fine_tunes = fine_tunes_list.data  # type: ignore
        if not fine_tunes:
            raise RuntimeError("[-] no fine_tune data found")
        columns = []
        for key, value in fine_tunes[0].items():
            if not isinstance(value, list):
                columns.append(key)
        data = [
            [fine_tunes.get(column) for column in columns]
            for fine_tunes in fine_tunes
        ]
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
