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

    If a name is passed as an argument, the model whose ID matches that
    name is returned.

    Use the `--fuzzy` option to return all models that contain the string
    anywhere in their model ID. This is useful for finding fine-tuned or
    experimental models.

    Attributes except `model_permission` are shown. To see permission
    values, use `model show` instead with the exact model name.
    """

    logger = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--fuzzy",
            action="store_true",
            default=False,
            help="match if 'name' occurs anywhere in the model ID",
        )
        parser.add_argument(
            "name",
            metavar="NAME",
            nargs="?",
            default=None,
            help="Search model names for this string",
        )
        return parser

    def take_action(self, parsed_args):  # noqa
        model_list = openai.Model.list()
        if parsed_args.name is None:
            models = model_list.data  # type: ignore
        else:
            models = [
                model for model in model_list.data  # type: ignore
                if (
                    (not parsed_args.fuzzy and model.id == parsed_args.name)
                    or (parsed_args.fuzzy and parsed_args.name in model.id)
                )
            ]
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
