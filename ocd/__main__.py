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

from pathlib import Path

# External imports
from cliff.app import App
from cliff.commandmanager import CommandManager
from psec.exceptions import SecretNotFoundError
from psec.secrets_environment import SecretsEnvironment
from psec.utils import (
    bell,
    get_default_environment,
    show_current_value,
    Timer,
)

# Internal imports
import openai

from ocd.defaults import Defaults
from ocd.utils import (
    BROWSER,
    BROWSER_EPILOG,
    open_browser,
)
from openai.version import VERSION


# Set up command line option defaults
defaults = Defaults()

def create_psec_environment(environment: SecretsEnvironment) -> Path:
    """
    Create a 'psec' environment by cloning from descriptions stored
    in a subdirectory within this Python module.

    This is a helper function intended for those who may not be
    familiar with 'psec'.
    """
    descriptions_path = Path(__file__).with_name('secrets.d')
    environment.environment_create(source=descriptions_path)
    location = environment.get_environment_path()
    if not location.exists():
        raise RuntimeError(
            f'[-] failed to create environment at {location}'
        )
    return location

# pyright: reportOptionalMemberAccess=false

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
        # Store defaults in app for use by commands.
        self.defaults = defaults
        self.defaults_original = str(self.defaults)
        self.timer = Timer()
        self.secrets = None
        self.openai_base = 'https://beta.openai.com'
        self.openai_docs_base = f'{self.openai_base}/docs'

    def build_option_parser(self, description, version):  # pylint: disable=arguments-differ, line-too-long
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
        # pylint: disable=import-outside-toplevel
        from psec.utils import CustomFormatter
        from cliff import _argparse
        _argparse.SmartHelpFormatter = CustomFormatter
        # pylint: enable=import-outside-toplevel
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
              BROWSER                Default browser for use by webbrowser.open().{show_current_value('BROWSER')}
              D2_ENVIRONMENT         Default environment identifier.{show_current_value('D2_ENVIRONMENT')}
              D2_SECRETS_BASEDIR     Default base directory for storing secrets.{show_current_value('D2_SECRETS_BASEDIR')}
              OPENAI_API_KEY         OpenAI API key.
              OPENAI_ORGANIZATION_ID OpenAI Organization identifier.
            """)  # noqa
        return parser

    def initialize_app(self, argv):
        if '--debug' not in argv:
            root_logger = logging.getLogger('')
            root_logger.setLevel(logging.INFO)
        self.LOG.debug('[*] initialize_app(%s)', self.__class__.NAME)
        if sys.version_info <= (3, 7):
            raise RuntimeError(
                "[-] this program requires Python 3.7 or higher"
            )
        self.timer.start()

    def prepare_to_run_command(self, cmd):
        self.LOG.debug("[*] prepare_to_run_command('%s')", cmd.cmd_name)
        #
        if cmd.cmd_name not in ['help', 'about']:
            self.secrets = SecretsEnvironment(
                environment=self.options.environment,
                export_env_vars=True,
                create_root=True
            )
            if not self.secrets.environment_exists():
                _ = create_psec_environment(environment=self.secrets)
            self.secrets.read_secrets_and_descriptions()
            try:
                # An API key is necessary for most commands to work.
                openai.api_key = os.environ.get(
                    "OPENAI_API_KEY",
                    self.secrets.get_secret("openai_api_key"),
                )
            except SecretNotFoundError:
                # Attempt to set the key for future use and continue on
                # with command.
                openai.api_key = self.handle_missing_api_key()
            # An organization ID is optional, so let that pass.
            try:
                openai.organization = os.environ.get(
                    "OPENAI_ORGANIZATION_ID",
                    self.secrets.get_secret("openai_organization_id"),
                )
            except SecretNotFoundError:
                if self.options.verbose_level > 1:
                    self.LOG.info(
                        "[+] no specific OpenAI organization will be used")

            self.LOG.debug(
                "[+] using environment '%s'", self.options.environment
            )
        if self.options.api_base is not None:
            openai.api_base = self.options.api_base
        self.LOG.debug("[*] running command '%s'", cmd.cmd_name)

    def clean_up(self, cmd, result, err):
        self.LOG.debug("[-] clean_up command '%s'", cmd.cmd_name)
        if str(self.defaults) != self.defaults_original:
            # One or more defaults were changed, so need to be saved.
            self.LOG.debug(
                "[+] updating saved command line option defaults"
            )
            self.defaults.save_to_db()
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
            self.stderr.write(f'[+] elapsed time {elapsed}\n')
            bell()

    def handle_missing_api_key(self):
        """
        Handle missing API key by prompting the user to create a new API key
        and save it to the current psec environment. If no environment exists,
        one will be created from descriptions stored in this module.
        """
        page = f'{self.openai_base}/account/api-keys'
        self.LOG.info("[-] OpenAPI API key not set")
        sys.stdout.flush()
        # pylint: disable=line-too-long
        explanation = textwrap.dedent(
            f"""
            The 'ocd' CLI needs an API key to access the OpenAI API. It expects to find it in a
            variable named 'openai_api_key' in a 'psec' environment directory located at the
            path '{self.secrets.get_environment_path()}'.

            To make things easy, I can try to open a web browser tab for you with the OpenAI API
            Account page at the URL: {page}

            On that page, create a new API key, copy it, and paste it below when prompted and it
            will be saved for for use in subsequent commands. If your browser does not open the page,
            or you prefer to do this step manually, visit the URL above and use the following command
            to store the API key: `psec secrets set openai_api_key="sk-ppV9ny...O1Y"`
            """
        )
        # pylint: enable=line-too-long
        sys.stdout.write(explanation)
        sys.stdout.write("\n\nOpen the OpenAI Account page now? y/n [y] ")
        sys.stdout.flush()
        response = input()
        if response not in ["n", "N"]:
            sys.stdout.write("\n")
            open_browser(
                page=page,
                browser=self.options.browser,
                force=self.options.force_browser,
                logger=self.LOG,
            )
        else:
            explanation = (
                "\nOK, but you will need to manually set the 'openai_api_key'"
                " in the 'psec' environment.\n"
            )
            sys.stdout.write(explanation)
            sys.exit(0)
        sys.stdout.write("\n\nEnter the OpenAI API key -> ")
        sys.stdout.flush()
        response = input()
        if not (
            response.startswith("sk-")
            and len(response) == 51
        ):
            raise RuntimeError(
                '[-] that does not appear to be a valid OpenAI API key'
            )
        self.secrets.set_secret('openai_api_key', response)
        self.secrets.write_secrets()
        return response


def main(argv=None):  # noqa
    """
    Command line interface entry point for the ``ocd`` program.
    """
    myapp = OCDApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(argv=sys.argv[1:]))

# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :

