import configparser
import csv
import os
from abc import ABC, abstractmethod

import argparse
import yaml
from typing import FrozenSet, Optional, Iterable, TextIO, Union, Any, List
from yaml import YAMLError

OUTPUT_CHOICES = ['cli', 'json', 'junitxml', 'github_failed_only']
FRAMEWORK_CHOICES = ['cloudformation', 'terraform', 'kubernetes', 'serverless', 'arm', 'all']

PROGRAM_NAME = 'checkov'


class CheckovConfigError(Exception):
    pass


class CheckovConfig:

    def __init__(self, source: str, *, directory: Optional[Iterable[str]] = None, file: Optional[Iterable[str]] = None,
                 external_checks_dir: Optional[Iterable[str]] = None,
                 external_checks_git: Optional[Iterable[str]] = None, output: Optional[str] = None,
                 no_guide: Optional[bool] = None, quiet: Optional[bool] = None, framework: Optional[str] = None,
                 check: Optional[str] = None, skip_check: Optional[str] = None, soft_fail: Optional[bool] = None,
                 repo_id: Optional[str] = None, branch: Optional[str] = None):
        self.source = source
        self.directory: FrozenSet = frozenset(directory or {})
        self.file: FrozenSet = frozenset(file or {})
        self.external_checks_dir: FrozenSet = frozenset(external_checks_dir or {})
        self.external_checks_git: FrozenSet = frozenset(external_checks_git or {})
        self._output = output
        self._no_guide = no_guide
        self._quiet = quiet
        self._framework = framework
        self.check = check
        self.skip_check = skip_check
        self._soft_fail = soft_fail
        self.repo_id = repo_id
        self._branch = branch

    @staticmethod
    def from_args(args: argparse.Namespace) -> 'CheckovConfig':
        # TODO there should be a way to clear this from a parent
        # Currently if a parent set this, there is no way for the cli to override that in a way, that every check
        # runs
        return CheckovConfig(
            source='args',
            directory=args.directory,
            file=args.file,
            external_checks_dir=args.external_checks_dir,
            external_checks_git=args.external_checks_git,
            output=args.output,
            no_guide=args.no_guide,
            quiet=args.quiet,
            framework=args.framework,
            check=args.check,
            skip_check=args.skip_check,
            soft_fail=args.soft_fail,
            repo_id=args.repo_id,
            branch=args.branch,
        )

    @staticmethod
    def from_file(file: Union[TextIO, str, os.PathLike]) -> 'CheckovConfig':
        if isinstance(file, (str, os.PathLike)):
            with open(file, 'r') as stream:
                return CheckovConfig._from_file(stream)
        else:
            return CheckovConfig._from_file(file)

    @staticmethod
    def _from_file(stream: TextIO) -> 'CheckovConfig':
        # TODO accept file name
        parsers = [
            _YAMLParser,
            # config must be last, because it will not fail in every case
            _ConfigParser,
        ]
        errors = []
        for parser in parsers:
            try:
                return parser(stream).parse()
            except Exception as e:
                errors.append(e)
                stream.seek(0)
        raise CheckovConfigError(errors)

    @property
    def output(self) -> str:
        return self._output or 'cli'

    @property
    def no_guide(self) -> bool:
        return self._no_guide if self._no_guide is not None else False

    @property
    def quiet(self) -> bool:
        return self._quiet if self._quiet is not None else False

    @property
    def framework(self) -> str:
        return self._framework or 'all'

    @property
    def soft_fail(self) -> bool:
        return self._soft_fail if self._soft_fail is not None else False

    @property
    def branch(self):
        return self._branch or 'master'

    def extend(self, parent: 'CheckovConfig'):
        self.directory = self.directory.union(parent.directory)
        self.file = self.file.union(parent.file)
        self.external_checks_dir = self.external_checks_dir.union(parent.external_checks_dir)
        self.external_checks_git = self.external_checks_git.union(parent.external_checks_git)
        # _output is never ''
        self._output = self._output or parent._output
        if self._no_guide is None:
            self._no_guide = parent._no_guide
        if self._quiet is None:
            self._quiet = parent._quiet
        # _framework is never ''
        self._framework = self._framework or parent._framework
        if self._soft_fail is None:
            self._soft_fail = parent._soft_fail
        # repo_id is never ''
        self.repo_id = self.repo_id or parent.repo_id
        # repo_id is never ''
        self._branch = self._branch or parent._branch

        if not self.check and not self.skip_check:
            # if nothing is set, copy from parent
            self.check = parent.check
            self.skip_check = parent.skip_check
        else:
            # At least one is set. Update the once, that are set. If it are both, it was invalid and will be invalid.
            if self.check and parent.check:
                # parent.check is a string but not an empty one
                self.check = f'{self.check},{parent.check}'
            if self.skip_check and parent.skip_check:
                # parent.skip_check is a string but not an empty one
                self.skip_check = f'{self.skip_check},{parent.skip_check}'


class _Parser(ABC):

    @abstractmethod
    def __init__(self, stream: TextIO):
        self.kwargs = {}

    @staticmethod
    def get_error_error(message: str, value: Any) -> CheckovConfigError:
        if isinstance(value, (bool, int, float)):
            message += f' You may just want to quote the value like this: "{value}"'
        return CheckovConfigError(message)

    @staticmethod
    def assert_choice(value: str, src: str, choices: Iterable[str]) -> None:
        if value not in choices:
            choices_str = ', '.join(map(lambda c: f'"{c}"', choices))
            message = f'{src} was "{value}" but has to be one of: {choices_str}'
            value_caseless = value.casefold()
            # I didn't know how hard string comparison could be. This is enough for case insensitive but
            # if you are interested in a deep dive:
            # https://stackoverflow.com/questions/319426/how-do-i-do-a-case-insensitive-string-comparison
            possible_choices = [f'"{choice}"' for choice in choices if value_caseless == choice.casefold()]
            if possible_choices:
                possible_choices = ', '.join(sorted(possible_choices))
                if len(possible_choices) == 1:
                    message = f'{message} You may want to use this value instead: {possible_choices}'
                else:
                    message = f'{message} You may want to use one of this values instead: {possible_choices}'
            raise CheckovConfigError(message)

    def parse(self):
        if self.has_content():
            self.handle_set('directories', 'directory')
            self.handle_set('files', 'file')
            self.handle_set('external_checks_dirs', 'external_checks_dir')
            self.handle_set('external_checks_gits', 'external_checks_git')
            self.handle_choice('output', 'output', OUTPUT_CHOICES)
            self.handle_type('no_guide', 'no_guide', bool)
            self.handle_type('quiet', 'quiet', bool)
            self.handle_choice('framework', 'framework', FRAMEWORK_CHOICES)
            self.handle_check('checks', 'check')
            self.handle_check('skip_checks', 'skip_check')
            self.handle_type('soft_fail', 'soft_fail', bool)
            self.handle_type('repo_id', 'repo_id', str)
            self.handle_type('branch', 'branch', str)
            self.after_parse_hook()

        return CheckovConfig('file', **self.kwargs)

    @abstractmethod
    def has_content(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def handle_set(self, src: str, dest: str):
        raise NotImplementedError

    @abstractmethod
    def handle_choice(self, src: str, dest: str, choices: Iterable[str]):
        raise NotImplementedError

    @abstractmethod
    def handle_type(self, src: str, dest: str, t: type):
        raise NotImplementedError

    @abstractmethod
    def handle_check(self, src: str, dest: str):
        raise NotImplementedError

    def after_parse_hook(self):
        pass


class _YAMLParser(_Parser):

    def __init__(self, stream: TextIO):
        super().__init__(stream)
        try:
            self.content = yaml.safe_load(stream)
        except YAMLError as e:
            raise CheckovConfigError('Failed to parse YAML') from e

    def has_content(self) -> bool:
        return self.content is not None

    def handle_set(self, src: str, dest: str):
        if src not in self.content:
            return
        values = self.content[src]
        if isinstance(values, str):
            values = [values]
        elif not isinstance(values, list):
            raise self.get_error_error(
                f'{src} has to be a list or if you use the short hand version for a single '
                f'value, just a str.', values)
        for value in values:
            if not isinstance(value, str):
                raise self.get_error_error(f'Elements of {src} have to be str.', value)
        self.kwargs[dest] = values
        del self.content[src]

    def handle_choice(self, src: str, dest: str, choices: Iterable[str]):
        if src not in self.content:
            return
        value = self.content[src]
        if not isinstance(value, str):
            message = f'{src} has to be a str.'
            raise self.get_error_error(message, value)
        self.assert_choice(value, src, choices)
        self.kwargs[dest] = value
        del self.content[src]

    def handle_type(self, src: str, dest: str, t: type):
        if src not in self.content:
            return
        value = self.content[src]
        if not isinstance(value, t):
            message = f'{src} has to be a {t.__name__}.'
            if t == str:
                raise self.get_error_error(message, value)
            raise CheckovConfigError(message)
        self.kwargs[dest] = value
        del self.content[src]

    def handle_check(self, src: str, dest: str):
        if src not in self.content:
            return
        values = self.content[src]

        if isinstance(values, list):
            for value in values:
                if not isinstance(value, str):
                    raise self.get_error_error(f'Elements of {src} have to be str.', values)
            values = ','.join(values)
        elif not isinstance(values, str):
            raise self.get_error_error(f'{src} has to be a string or a list of strings', values)
        self.kwargs[dest] = values
        del self.content[src]

    def after_parse_hook(self):
        if self.content:
            keys = map(lambda v: f'"{v}"', sorted(self.content))
            raise CheckovConfigError(f'File contained unexpected keys: {", ".join(keys)}')


class _ConfigParser(_Parser):
    def __init__(self, stream: TextIO):
        super().__init__(stream)
        try:
            content = configparser.ConfigParser(interpolation=None)
            content.read_file(stream)
        except configparser.ParsingError as e:
            raise CheckovConfigError('Failed to parse config') from e
        else:
            self.content = content
            self.section = content[PROGRAM_NAME]

    def has_content(self) -> bool:
        return PROGRAM_NAME in self.content

    def parse_list(self, src: str) -> List[str]:
        value = self.content.get(PROGRAM_NAME, src).replace('\n', '')
        return next(csv.reader([value], delimiter=',', quotechar='"'))

    def handle_set(self, src: str, dest: str):
        if src not in self.section:
            return
        values = self.parse_list(src)
        self.kwargs[dest] = values
        del self.section[src]

    def handle_choice(self, src: str, dest: str, choices: Iterable[str]):
        if src not in self.section:
            return
        value = self.content.get(PROGRAM_NAME, src)
        self.assert_choice(value, src, choices)
        self.kwargs[dest] = value
        del self.section[src]

    def handle_type(self, src: str, dest: str, t: type):
        if src not in self.section:
            return
        if t == bool:
            method = self.content.getboolean
        elif t == int:
            method = self.content.getint
        elif t == float:
            method = self.content.getfloat
        else:
            method = self.content.get
        try:
            value = method(PROGRAM_NAME, src)
        except ValueError as e:
            raise CheckovConfigError(f'{src} has to be a {t.__name__}.') from e
        self.kwargs[dest] = value
        del self.section[src]

    def handle_check(self, src: str, dest: str):
        if src not in self.section:
            return
        values = self.parse_list(src)
        self.kwargs[dest] = ','.join(values)
        del self.section[src]

    def after_parse_hook(self):
        if self.section:
            default_keys = self.content[self.content.default_section].keys()
            # remove keys from default section, because they are still allowed.
            # This can remove to much, if some value is declared in default and checkov section.
            unexpected_keys = filter(lambda k: k not in default_keys, self.section.keys())
            keys = map(lambda v: f'"{v}"', sorted(unexpected_keys))
            raise CheckovConfigError(f'File contained unexpected keys: {", ".join(keys)}')
