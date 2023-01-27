# -*- coding: utf-8 -*-

"""
Analyze one or more text files.
"""

# Standard imports
import logging
import sys

from pathlib import Path

# External imports
from cliff.lister import Lister

# Local imports
from ocd.utils import (
    get_file_type,
    num_tokens_from_string,
)


class TextAnalyze(Lister):
    """
    Analyze one or more text files.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "file",
            nargs="+",
            metavar="FILE",
            help="text file to analyze",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        columns = ['name', 'type', 'bytes', 'lines', 'tokens']
        data = []
        for file_name in parsed_args.file:
            file_path = Path(file_name)
            file_type = get_file_type(file_path)
            string = file_path.read_text()
            tokens = num_tokens_from_string(string, "gpt2")
            data.append(
                [
                    file_name,
                    file_type,
                    len(string),
                    len(string.split('\n')),
                    tokens,
                ]
            )
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
