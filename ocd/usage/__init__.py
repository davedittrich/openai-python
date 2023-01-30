# -*- coding: utf-8 -*-

"""
Open the OpenAI API Accounts page to show usage details.
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


class Usage(Command):
    """
    Open the OpenAI API Accounts page to see Usage details.
    """

    def get_parser(self, prog_name):  # noqa
        parser = super().get_parser(prog_name)
        parser.epilog = BROWSER_EPILOG
        return parser

    def take_action(self, _):
        page = f'{self.app.openai_base}/account/usage'
        open_browser(
            page=page,
            browser=self.app_args.browser,
            force=self.app_args.force_browser,
            logger=logger,
        )
        sys.exit(0)


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
