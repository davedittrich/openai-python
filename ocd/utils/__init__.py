# -*- coding: utf-8 -*-

"""
Initialization file for `ocd` command classes and utility functions.
"""

# Standard imports
import argparse
import os
import subprocess  # nosec
import sys
import textwrap
import webbrowser

from pathlib import Path

# External imports
import tiktoken

from psec.utils import get_default_environment

# Local imports
import openai

BROWSER = os.environ.get('BROWSER', None)
BROWSER_EPILOG = textwrap.dedent("""
    ABOUT THE BROWSER OPEN FEATURE

    This program uses the Python ``webbrowser`` module to open a browser.

        https://docs.python.org/3/library/webbrowser.html
        https://github.com/python/cpython/blob/3.8/Lib/webbrowser.py

    This module supports a large set of browsers for various operating system
    distributions. It will attempt to chose an appropriate browser from operating
    system defaults.  If it is not possible to open a graphical browser
    application, it may open the ``lynx`` text browser.

    You can choose which browser ``webbrowser`` will open using the identifier
    from the set in the ``webbrowser`` documentation.  Either specify the browser
    using the ``--browser`` option on the command line, or export the environment
    variable ``BROWSER`` set to the identifier (e.g., ``export BROWSER=firefox``).

    It is also possible to set the ``BROWSER`` environment variable to a full path
    to an executable to run. On Windows 10 with Windows Subsystem for Linux, you
    can use this feature to open a Windows executable outside of WSL. (E.g., using
    ``export BROWSER='/c/Program Files/Mozilla Firefox/firefox.exe'`` will open
    Firefox installed in that path).

    Also note that when this program attempts to open a browser, an exception may
    be thrown if the process has no TTY. If this happens, use the ``--force``
    option to bypass this behavior and attempt to open the browser anyway.
""")  # noqa


def get_text_from_completion(completion):
    """
    Return the text from the completion
    """
    return completion.choices[0].text


def get_model_ids(model_list=None):
    """
    Return a list of model ids from a list of models returned by the
    OpenAI API.
    """
    if model_list is None:
        model_list = openai.Model.list()
    return (model.id for model in model_list)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """
    Returns the number of tokens in a text string.

    Trailing whitespace is removed from the string as it impacts
    tokenization.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    # Strip trailing whitespace from the string
    num_tokens = len(encoding.encode(string.strip()))
    return num_tokens


def save_tokens_to_file(file_name: str, tokens: list) -> None:
    """Save the tokens."""
    raise NotImplementedError


def get_file_type(file_path: Path) -> str:
    """
    This function is a wrapper around the `file` command that is used
    to determine the file type of a file.

    Args:
        file_path: The path to the file to be checked.

    Returns:
        A string containing the file type of the file.
    """
    file_output = ""
    with subprocess.Popen(
        ['/usr/bin/file', '-b', file_path.name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False  # nosec
    ) as process:
        pout, perr = process.communicate()
        file_output = (
            pout.decode('utf-8').strip() if len(perr) == 0
            else str(file_path.suffix[1:]).upper()
        )
    return file_output


# Based on: https://stackoverflow.com/a/64259328
def ranged_type(value_type, min_value, max_value):
    """
    Return function handle of an argument type function for
    ArgumentParser checking a range:
        min_value <= arg <= max_value

    Parameters
    ----------
    value_type  - value-type to convert arg to
    min_value   - minimum acceptable argument
    max_value   - maximum acceptable argument

    Returns
    -------
    function handle of an argument type function for ArgumentParser


    Usage
    -----
        ranged_type(float, 0.0, 1.0)

    """

    def range_checker(arg: str):
        try:
            candidate = value_type(arg)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f'[-] must be a valid {value_type}'
            ) from exc
        if candidate < min_value or candidate > max_value:
            raise argparse.ArgumentTypeError(
                f'[-] must be within [{min_value}, {min_value}]'
            )
        return candidate

    # Return function handle to checking function
    return range_checker


def print_completion(string: str) -> None:
    """
    Output a completion string to stdout, replacing backslash-n
    with actual newline characters.
    """
    print(string.replace('\\n', '\n'))


def open_browser(
    page=None,
    browser=None,
    force=False,
    logger=None,
):
    """
    Open a browser window to the specified page.

    Parameters
    ----------
    page : str
        The URL to open.
    browser : str, optional
        The browser to use. If not specified, the system default will be used.
    force : bool, optional
        If True, open the browser even if stdin is not a TTY.
    logger : logging.Logger, optional
        If specified, log the action.

    Raises
    ------
    RuntimeError
        If no page is specified, or if stdin is not a TTY and force is not True.
    """
    if not sys.stdin.isatty() and not force:
        raise RuntimeError(
            "[-] use --force to open browser when stdin is not a TTY"
        )
    if page is None:
        raise RuntimeError("[-] not page specified")
    which = "system default" if browser is None else browser
    if logger is not None:
        logger.info("[+] opening browser '%s' for %s", which, page)
    if browser is not None:
        controller = webbrowser.get(using=browser)
        controller.open_new_tab(page)
    else:
        webbrowser.open(page, new=1)


class Defaults():
    """
    Object to hold command line option default settings.
    """

    CODE_TEMPERATURE = '0.0'
    CODEX_MODEL_ID = 'code-davinci-002'
    EDIT_MODEL_ID = 'text-davinci-edit-001'
    EMBEDDING_MODEL_ID = 'text-embedding-ada-002'
    ENVIRONMENT = get_default_environment()
    IMAGES_N = 1
    IMAGES_RESPONSE_FORMATS = [
        'b64_json',
        'url',
    ]
    IMAGES_SIZES = [
        "256x256",
        "512x512",
        "1024x1024"
    ]
    MAX_CODE_TOKENS = 500
    MAX_IMAGES_N = 10
    MAX_IMAGES_PROMPT = 1000
    MAX_TOKENS = 16
    MODEL_ID = 'curie-instruct-beta'
    TEMPERATURE = '0.9'


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :

