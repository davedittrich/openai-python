# -*- coding: utf-8 -*-

"""
List command line option defaults.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.lister import Lister


class DefaultsList(Lister):
    """
    List command line option defaults.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--fuzzy",
            action="store_true",
            default=False,
            help="match if 'name' occurs anywhere in the variable",
        )
        parser.add_argument(
            "name",
            metavar="NAME",
            nargs="?",
            default=None,
            help="Search variable names for this string",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        results = self.app.defaults.get_state(columns=True)
        columns = results[0]
        data = results[1:]
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
