# -*- coding: utf-8 -*-

"""
Open the model overview documentation page.
"""

# Standard imports
import logging
import sys

# External imports
from cliff.command import Command

# Local imports
from ocd.utils import (  # pylint: disable=no-name-in-module
    BROWSER_EPILOG,
    open_browser,
)


logger = logging.getLogger(__name__)


class ModelsOverview(Command):
    """
    Open the models overview documentation page.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.epilog = BROWSER_EPILOG
        return parser

    def take_action(self, parsed_args):  # noqa
        page = f'{self.app.openai_docs_base}/models/overview'
        open_browser(
            page=page,
            browser=self.app_args.browser,
            force=self.app_args.force_browser,
            logger=logger,
        )
        sys.exit(0)


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :

