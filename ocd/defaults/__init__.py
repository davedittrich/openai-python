# -*- coding: utf-8 -*-

"""
Command line options defaults dataclass.
"""

# Standard imports
import logging
import sqlite3

from collections import OrderedDict
from dataclasses import (
    asdict,
    field,
    fields,
    dataclass,
)
from pathlib import Path
from sqlite3 import OperationalError

# External imports
from psec.utils import get_default_environment


# pyright: reportOptionalMemberAccess=false


logger = logging.getLogger(__name__)

IGNORE_FIELDS = [
    'object',
]

@dataclass
class Defaults:
    """
    Dataclass for command line option defaults.

    Values are saved in a sqlite3 database in the 'psec' environment
    so they can be used across multiple CLI invocations.

    Values can be reset to initial defaults when necessary.
    """
    default_state = OrderedDict({
        'CODEX_TEMPERATURE': 0.9,
        'CODEX_MAX_TOKENS': 500,
        'CODEX_MODEL_ID': 'code-davinci-002',
        'EDIT_MODEL_ID': 'text-davinci-edit-001',
        'EMBEDDING_MODEL_ID': 'text-embedding-ada-002',
        'ENVIRONMENT': get_default_environment(),
        'IMAGES_MAX_N': 10,
        'IMAGES_MAX_PROMPT': 1000,
        'IMAGES_N': 1,
        'IMAGES_RESPONSE_FORMAT': 'b64_json',
        'IMAGES_SIZE': '512x512',
        'MAX_TOKENS': 16,
        'MODEL_ID': 'gpt-3.5-turbo',
        'N': 1,
        'TEMPERATURE': 0.9
    })

    # pylint: disable=invalid-name
    CODEX_TEMPERATURE: float = field(init=False)
    CODEX_MAX_TOKENS: int = field(init=False)
    CODEX_MODEL_ID: str = field(init=False)
    EDIT_MODEL_ID: str = field(init=False)
    EMBEDDING_MODEL_ID: str = field(init=False)
    ENVIRONMENT: str = field(init=False)
    IMAGES_MAX_N: int = field(init=False)
    IMAGES_MAX_PROMPT: int = field(init=False)
    IMAGES_N: int = field(init=False)
    IMAGES_RESPONSE_FORMAT: str = field(init=False)
    IMAGES_SIZE: str = field(init=False)
    MAX_TOKENS: int = field(init=False)
    MODEL_ID: str = field(init=False)
    N: int = field(init=False)
    TEMPERATURE: float = field(init=False)

    # Instance variables
    choices = {
        'IMAGES_SIZE': ['256x256', '512x512', '1024x1024'],
        'IMAGES_RESPONSE_FORMAT': ['b64_json', 'url'],
    }
    defaults_db_path = None
    environment_path = None
    conn = None
    cursor = None

    def __post_init__(self):
        if self.environment_path is None:
            self.environment_path = Path('.')
        self.defaults_db_path = self.environment_path / 'defaults.db'
        self.conn = sqlite3.connect(self.defaults_db_path)
        self.cursor = self.conn.cursor()
        try:
            self.retrieve_from_db()
        except OperationalError as exc:
            if 'no such table' in str(exc):
                self.reset_to_defaults()
                self.save_to_db()
            else:
                raise

    def save_to_db(self):
        """
        Saves state to the database.
        """
        # The items and their order in the table must match that
        # of self.default_state() in order for them to stay in sync.
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS defaults (
                codex_temperature REAL,
                codex_max_tokens INTEGER,
                codex_model_id TEXT,
                edit_model_id TEXT,
                embedding_model_id TEXT,
                environment TEXT,
                images_max_n INTEGER,
                images_max_prompt INTEGER,
                images_n INTEGER,
                images_response_format TEXT,
                images_size TEXT,
                max_tokens INTEGER,
                model_id TEXT,
                n INTEGER,
                temperature REAL
            )""")
        self.cursor.execute(
            "INSERT INTO defaults VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                self.CODEX_TEMPERATURE,
                self.CODEX_MAX_TOKENS,
                self.CODEX_MODEL_ID,
                self.EDIT_MODEL_ID,
                self.EMBEDDING_MODEL_ID,
                self.ENVIRONMENT,
                self.IMAGES_MAX_N,
                self.IMAGES_MAX_PROMPT,
                self.IMAGES_N,
                self.IMAGES_RESPONSE_FORMAT,
                self.IMAGES_SIZE,
                self.MAX_TOKENS,
                self.MODEL_ID,
                self.N,
                self.TEMPERATURE
            )
        )
        self.conn.commit()

    def index(self, variable):
        """
        Return the index of the specified variable.
        """
        return self.field_names().index(variable)

    def get_state(self, columns=False) -> list:
        """
        Return a list of tuples representing the current state
        in the form:

            default, type, value

        If columns is True, includes column titles in the first row.
        """
        data = [] if not columns else [['default', 'type', 'value']]
        fields_list = fields(self)
        for field_ in fields_list:
            data.append(
                [
                    field_.name,
                    field_.type.__name__,
                    str(getattr(self, field_.name))
                ]
            )
        return data

    def retrieve_from_db(self):
        """
        Loads saved state from the database.
        """
        self.cursor.execute("SELECT * FROM defaults")
        result = self.cursor.fetchone()
        if result is None:
            raise OperationalError("no such table: defaults")
        for i, attribute in enumerate(self.field_names()):
            setattr(self, attribute, result[i])

    def reset_to_defaults(self):
        """
        Resets variables to default values.
        """
        for attribute in self.field_names():
            setattr(self, attribute, self.default_state[attribute])

    def delete_db(self):
        """
        Deletes the saved command line option state file.
        """
        self.defaults_db_path.unlink(missing_ok=True)
        logger.info("[+] deleted %s", self.defaults_db_path)

    def asdict(self) -> dict:
        """
        Return a dictionary with current values.
        """
        return asdict(self)

    def field_names(self) -> list:
        """
        Return a list of field names.
        """
        if '_field_names' not in self.__dict__:
            setattr(
                self,
                '_field_names',
                [field.name for field in fields(self)]
            )
        return getattr(self, '_field_names')


__all__ = [
    'IGNORE_FIELDS',
    'Defaults',
]


# vim: set fileencoding=utf-8 ts=4 sw=4 tw=0 et :
