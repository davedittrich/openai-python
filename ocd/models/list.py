# -*- coding: utf-8 -*-

"""
List models.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.lister import Lister

# Internal imports
import openai


class ModelsList(Lister):
    """
    List models.

    Attributes except `model_permission` are shown. To see permission
    values, use `model show

    """

    logger = logging.getLogger(__name__)

    # def get_parser(self, prog_name):
    #     parser = super().get_parser(prog_name)
    #     return parser

    def take_action(self, parsed_args):  # noqa
        model_list = openai.Model.list()
        models = model_list.data  # type: ignore
        if not models:
            raise RuntimeError("[-] no model data found")
        # Ignore the model_permission object when listing as it is complex
        columns = []
        for key, value in models[0].items():
            if not isinstance(value, list):
                columns.append(key)
        data = [
            [model.get(column) for column in columns]
            for model in models
        ]
        if len(data) == 0:
            sys.exit(1)
        return columns, data


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
