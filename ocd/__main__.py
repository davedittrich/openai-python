# -*- coding: utf-8 -*-

"""
OCD: The OpenAI CLI by davedittrich.

This entry point script uses the ``cliff`` library to provide a
feature-rich CLI for accessing the OpenAI API. It has some overlap
with the OpenAI CLI ``openai``, but has additional capabilities
that don't require post-processing of output from API calls
using other programs, though also not precluding their use if
that is desired.

"""

# Standard imports
import os
import sys
import textwrap

# External imports
from cliff.app import App
from cliff.commandmanager import CommandManager
from psec.secrets_environment import SecretsEnvironment
from psec.utils import (
    bell,
    get_default_environment,
    show_current_value,
    Timer,
)

# Internal imports
import openai

from ocd.utils import (  # pylint: disable=no-name-in-module
    BROWSER,
    BROWSER_EPILOG,
    Defaults,  # pyright: reportGeneralTypeIssues=false
)
from openai.version import VERSION

defaults = Defaults()

class OCDApp(App):
    """Main CLI application class."""

    def __init__(self):
        super().__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=CommandManager(
                namespace='ocd'
            ),
            deferred_help=True,
            )
        self.timer = Timer()
        self.secrets = SecretsEnvironment(
            environment=DEFAULT_ENVIRONMENT,
            export_env_vars=True,
        )
        self.secrets.read_secrets_and_descriptions()
        openai.organization = os.environ.get(
            "OPENAI_ORGANIZATION_ID",
            self.secrets.get_secret("openai_organization_id"),
        )
        openai.api_key = os.environ.get(
            "OPENAI_API_KEY",
            self.secrets.get_secret("openai_api_key"),
        )
        self.openai_base = 'https://beta.openai.com'
        self.openai_docs_base = f'{self.openai_base}/docs'

    def build_option_parser(self, description, version):  # pylint: disable=arguments-differ noqa
        parser = super().build_option_parser(
            description,
            version
        )
        # TODO(dittrich): Migrate these formatter hacks somewhere else.
        #
        # OCD hack: Make ``help`` output report main program name,
        # even if run as ``python -m psec.main`` or such.
        if parser.prog.endswith('.py'):
            parser.prog = self.command_manager.namespace
        # Replace the cliff SmartHelpFormatter class before first use
        # by subcommand `--help`.
        # pylint: disable=wrong-import-order
        from psec.utils import CustomFormatter
        from cliff import _argparse
        _argparse.SmartHelpFormatter = CustomFormatter
        # pylint: enable=wrong-import-order
        # We also need to change app parser, which is separate.
        parser.formatter_class = CustomFormatter
        # Global options
        parser.add_argument(
            '--api-base',
            default=openai.api_base,
            help='API base URL'
        )
        parser.add_argument(
            '--browser',
            action='store',
            default=BROWSER,
            help='Browser to use'
        )
        parser.add_argument(
            '--force-browser',
            action='store_true',
            default=False,
            help='Open the browser even if process has no TTY'
        )
        parser.add_argument(
            '--elapsed',
            action='store_true',
            dest='elapsed',
            default=False,
            help='Print elapsed time on exit'
        )
        parser.add_argument(
            '-e', '--environment',
            metavar='<environment>',
            dest='environment',
            default=defaults.ENVIRONMENT,
            help='Deployment environment selector (Env: D2_ENVIRONMENT)'
        )
        parser.epilog = BROWSER_EPILOG + '\n' + textwrap.dedent(f"""
            Current working dir: {os.getcwd()}
            Python interpreter:  {sys.executable} (v{sys.version.split()[0]})

            Environment variables consumed:
              BROWSER             Default browser for use by webbrowser.open().{show_current_value('BROWSER')}
              D2_ENVIRONMENT      Default environment identifier.{show_current_value('D2_ENVIRONMENT')}
              D2_SECRETS_BASEDIR  Default base directory for storing secrets.{show_current_value('D2_SECRETS_BASEDIR')}
            """)  # noqa
        return parser

    def initialize_app(self, argv):
        self.LOG.debug('[*] initialize_app(%s)', self.__class__.NAME)
        if sys.version_info <= (3, 7):
            raise RuntimeError(
                "[-] this program requires Python 3.7 or higher"
            )
        self.timer.start()

    def prepare_to_run_command(self, cmd):
        self.LOG.debug("[*] prepare_to_run_command('%s')", cmd.cmd_name)
        #
        self.LOG.debug(
            "[+] using environment '%s'", self.options.environment
        )
        if self.options.api_base is not None:
            openai.api_base = self.options.api_base
        self.LOG.debug("[*] running command '%s'", cmd.cmd_name)

    def clean_up(self, cmd, result, err):
        self.LOG.debug("[-] clean_up command '%s'", cmd.cmd_name)
        if err:
            self.LOG.debug("[-] got an error: %s", str(err))
            sys.exit(result)
        if (
            self.options.elapsed
            or (
                self.options.verbose_level > 1
                and cmd.cmd_name != "complete"
            )
        ):
            self.timer.stop()
            elapsed = self.timer.elapsed()
            self.stderr.write('[+] elapsed time {}\n'.format(elapsed))
            bell()


def main(argv=None):  # noqa
    """
    Command line interface entry point for the ``ocd`` program.
    """
    myapp = OCDApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv[1:]))

# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
