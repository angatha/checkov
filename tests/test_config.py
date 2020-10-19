import argparse
import io
import os
import unittest
from typing import Union

from checkov.config import CheckovConfig, CheckovConfigError, OUTPUT_CHOICES, FRAMEWORK_CHOICES, \
    MERGING_BEHAVIOR_CHOICES, FrozenUniqueList
from checkov.main import add_parser_args


class ConfigTestCase(unittest.TestCase):

    @staticmethod
    def get_config_file(filename):
        test_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(test_dir, 'configs', filename)

    def assertCheckSkipCheckIsValid(self, config: CheckovConfig, msg=None):
        if msg:
            msg = msg + ': '
        self.assertFalse(config.check and config.skip_check,
                         f'{msg}Expected non or only one of check and skip_check to have a value set')

    def assertCheckSkipCheckIsInvalid(self, config: CheckovConfig, msg=None):
        if msg:
            msg = msg + ': '
        self.assertTrue(config.check, f'{msg}Expected check to be set. bot was "{config.check}"')
        self.assertTrue(config.skip_check, f'{msg}Expected skip_check to be set. bot was "{config.skip_check}"')

    def assertConfig(self, expected: Union[dict, CheckovConfig], config: CheckovConfig, msg_prefix=''):
        if isinstance(expected, CheckovConfig):
            class Wrapper:
                __slots__ = ['config']

                def __init__(self, c):
                    self.config = c

                def __getitem__(self, item):
                    return getattr(self.config, item)

            expected = Wrapper(expected)
        if msg_prefix:
            msg_prefix = msg_prefix + ': '
        self.assertEqual(expected['source'], config.source,
                         f'{msg_prefix}Expect source to be "{expected["source"]}" but got "{config.source}"')
        self.assertIsInstance(config.directory, FrozenUniqueList,
                              f'{msg_prefix}Expect directory to be a FrozenUniqueList but got "{type(config.directory)}"')
        self.assertEqual(FrozenUniqueList(expected['directory']), config.directory,
                         f'{msg_prefix}Expect directory to be "{expected["directory"]}" but got '
                         f'"{config.directory}"')
        self.assertIsInstance(config.file, FrozenUniqueList,
                              f'{msg_prefix}Expect file to be a FrozenUniqueList but got "{type(config.file)}"')
        self.assertEqual(FrozenUniqueList(expected['file']), config.file,
                         f'{msg_prefix}Expect file to be "{expected["file"]}" but got "{config.file}"')
        self.assertIsInstance(config.external_checks_dir, FrozenUniqueList,
                              f'{msg_prefix}Expect external_checks_dir to be a FrozenUniqueList but got '
                              f'"{type(config.external_checks_dir)}"')
        self.assertEqual(FrozenUniqueList(expected['external_checks_dir']), config.external_checks_dir,
                         f'{msg_prefix}Expect external_checks_dir to be "{expected["external_checks_dir"]}" but '
                         f'got "{config.external_checks_dir}"')
        self.assertIsInstance(config.external_checks_git, FrozenUniqueList,
                              f'{msg_prefix}Expect external_checks_git to be a FrozenUniqueList but got '
                              f'"{type(config.external_checks_git)}"')
        self.assertEqual(FrozenUniqueList(expected['external_checks_git']), config.external_checks_git,
                         f'{msg_prefix}Expect external_checks_git to be "{expected["external_checks_git"]}" but '
                         f'got "{config.external_checks_git}"')
        self.assertEqual(expected['_output'], config._output,
                         f'{msg_prefix}Expect _output to be "{expected["_output"]}" but got "{config._output}"')
        self.assertEqual(expected['output'], config.output,
                         f'{msg_prefix}Expect output to be "{expected["output"]}" but got "{config.output}"')
        self.assertIn(config.output, OUTPUT_CHOICES,
                      f'{msg_prefix}Expect output to be one of "{",".join(OUTPUT_CHOICES)}" but '
                      f'got "{config.output}"')
        self.assertEqual(expected['_no_guide'], config._no_guide,
                         f'{msg_prefix}Expect _no_guide to be "{expected["_no_guide"]}" but got "{config._no_guide}"')
        self.assertEqual(expected['no_guide'], config.no_guide,
                         f'{msg_prefix}Expect no_guide to be "{expected["no_guide"]}" but got "{config.no_guide}"')
        self.assertEqual(expected['_quiet'], config._quiet,
                         f'{msg_prefix}Expect _quiet to be "{expected["_quiet"]}" but got "{config._quiet}"')
        self.assertEqual(expected['quiet'], config.quiet,
                         f'{msg_prefix}Expect quiet to be "{expected["quiet"]}" but got "{config.quiet}"')
        self.assertEqual(expected['_framework'], config._framework,
                         f'{msg_prefix}Expect _framework to be "{expected["_framework"]}" but got '
                         f'"{config._framework}"')
        self.assertEqual(expected['framework'], config.framework,
                         f'{msg_prefix}Expect framework to be "{expected["framework"]}" but got "{config.framework}"')
        self.assertIn(config.framework, FRAMEWORK_CHOICES,
                      f'{msg_prefix}Expect framework to be one of "{",".join(FRAMEWORK_CHOICES)}" but '
                      f'got "{config.framework}"')
        self.assertEqual(expected['check'], config.check,
                         f'{msg_prefix}Expect check to be "{expected["check"]}" but got "{config.check}"')
        self.assertEqual(expected['merging_behavior'], config.merging_behavior,
                         f'{msg_prefix}Expect merging_behavior to be "{expected["merging_behavior"]}" but got '
                         f'"{config.merging_behavior}"')
        self.assertIn(config.merging_behavior, MERGING_BEHAVIOR_CHOICES,
                      f'{msg_prefix}Expect merging_behavior to be one of "{",".join(MERGING_BEHAVIOR_CHOICES)}" but '
                      f'got "{config.merging_behavior}"')
        self.assertEqual(expected['skip_check'], config.skip_check,
                         f'{msg_prefix}Expect skip_check to be "{expected["skip_check"]}" but got '
                         f'"{config.skip_check}"')
        self.assertEqual(expected['_soft_fail'], config._soft_fail,
                         f'{msg_prefix}Expect _soft_fail to be "{expected["_soft_fail"]}" but got '
                         f'"{config._soft_fail}"')
        self.assertEqual(expected['soft_fail'], config.soft_fail,
                         f'{msg_prefix}Expect soft_fail to be "{expected["soft_fail"]}" but got "{config.soft_fail}"')
        self.assertEqual(expected['repo_id'], config.repo_id,
                         f'{msg_prefix}Expect repo_id to be "{expected["repo_id"]}" but got "{config.repo_id}"')
        self.assertEqual(expected['_branch'], config._branch,
                         f'{msg_prefix}Expect _branch to be "{expected["_branch"]}" but got "{config._branch}"')
        self.assertEqual(expected['branch'], config.branch,
                         f'{msg_prefix}Expect branch to be "{expected["branch"]}" but got "{config.branch}"')


# noinspection DuplicatedCode
class TestCheckovConfig(ConfigTestCase):

    def test_repr_configured(self):
        kwargs = {
            'directory': ['/1/2', '/a/b'],
            'file': ['/1/2', '/a/b'],
            'external_checks_dir': ['/1/2', '/a/b'],
            'external_checks_git': ['/1/2', '/a/b'],
            'output': 'json',
            'no_guide': True,
            'quiet': True,
            'framework': 'all',
            'merging_behavior': 'union',
            'check': 'V_1',
            'soft_fail': False,
            'repo_id': 'ab/d',
            'branch': 'master'
        }

        config = CheckovConfig('name123', skip_check=None, **kwargs)
        config_repr = repr(config)

        self.assertIn(repr('name123'), config_repr, 'source should be in the representation')
        for k, v in kwargs.items():
            expected = f'{k}={repr(v)}'
            self.assertIn(expected, config_repr,
                          f'Expected "{expected}" to be present, because it is not the default value')
        self.assertNotIn('skip_check', config_repr,
                         'Expect "skip_check" to be absent, because it has its default value')

    def test_repr_empty(self):
        arguments = {
            'directory',
            'file',
            'external_checks_dir',
            'external_checks_git',
            'output',
            'no_guide',
            'quiet',
            'framework',
            'merging_behavior',
            'check',
            'skip_check',
            'soft_fail',
            'repo_id',
            'branch',
        }

        config = CheckovConfig('name123')
        config_repr = repr(config)

        self.assertIn(repr('name123'), config_repr, 'source should always be in the representation')
        for k in arguments:
            self.assertNotIn(k, config_repr,
                             'Expect "{k}" to be absent, because it has its default value')

    def test_config_creation_constructor(self):
        config = CheckovConfig('test')
        self.assertConfig({
            'source': 'test',
            'directory': FrozenUniqueList(),
            'file': FrozenUniqueList(),
            'external_checks_dir': FrozenUniqueList(),
            'external_checks_git': FrozenUniqueList(),
            '_output': None,
            'output': 'cli',
            '_no_guide': None,
            'no_guide': False,
            '_quiet': None,
            'quiet': False,
            '_framework': None,
            'framework': 'all',
            '_merging_behavior': 'union',
            'merging_behavior': 'union',
            'check': None,
            'skip_check': None,
            '_soft_fail': None,
            'soft_fail': False,
            'repo_id': None,
            '_branch': None,
            'branch': 'master',
        }, config)

    def test_config_creation_no_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': FrozenUniqueList(),
            'file': FrozenUniqueList(),
            'external_checks_dir': FrozenUniqueList(),
            'external_checks_git': FrozenUniqueList(),
            '_output': None,
            'output': 'cli',
            '_no_guide': None,
            'no_guide': False,
            '_quiet': None,
            'quiet': False,
            '_framework': None,
            'framework': 'all',
            '_merging_behavior': 'override_if_present',
            'merging_behavior': 'override_if_present',
            'check': None,
            'skip_check': None,
            '_soft_fail': None,
            'soft_fail': False,
            'repo_id': None,
            '_branch': None,
            'branch': 'master',
        }, config)

    def test_config_creation_short_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([
            '-d', '/a1',
            '-d', '/a1',
            '-d', '/b1',
            '--directory', '/a2',
            '--directory', '/a2',
            '--directory', '/b2',
            '-f', '/a3',
            '-f', '/a3',
            '-f', '/b3',
            '--file', '/a4',
            '--file', '/a4',
            '--file', '/b4',
            '--external-checks-dir', '/a5',
            '--external-checks-dir', '/a5',
            '--external-checks-dir', '/b5',
            '--external-checks-git', '/a6',
            '--external-checks-git', '/a6',
            '--external-checks-git', '/b6',
            '-o', 'json',
            '--no-guide',
            '--quiet',
            '--framework', 'kubernetes',
            '--merging-behavior', 'override',
            '-c', 'CKV_AWS_1,CKV_AWS_3',
            '--skip-check', 'CKV_AWS_2,CKV_AWS_4',
            '-s',
            '--repo-id', 'abc',
            '-b', 'b/123',
        ])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': ['/a1', '/b1', '/a2', '/b2'],
            'file': ['/a3', '/b3', '/a4', '/b4'],
            'external_checks_dir': ['/a5', '/b5'],
            'external_checks_git': ['/a6', '/b6'],
            '_output': 'json',
            'output': 'json',
            '_no_guide': True,
            'no_guide': True,
            '_quiet': True,
            'quiet': True,
            '_framework': 'kubernetes',
            'framework': 'kubernetes',
            '_merging_behavior': 'override',
            'merging_behavior': 'override',
            'check': 'CKV_AWS_1,CKV_AWS_3',
            'skip_check': 'CKV_AWS_2,CKV_AWS_4',
            '_soft_fail': True,
            'soft_fail': True,
            'repo_id': 'abc',
            '_branch': 'b/123',
            'branch': 'b/123',
        }, config)

    def test_config_creation_long_args(self):
        parser = argparse.ArgumentParser()
        add_parser_args(parser)
        args = parser.parse_args([
            '--output', 'json',
            '--check', 'CKV_AWS_1,CKV_AWS_3',
            '--soft-fail',
            '--branch', 'b/123',
        ])
        config = CheckovConfig.from_args(args)
        self.assertConfig({
            'source': 'args',
            'directory': FrozenUniqueList(),
            'file': FrozenUniqueList(),
            'external_checks_dir': FrozenUniqueList(),
            'external_checks_git': FrozenUniqueList(),
            '_output': 'json',
            'output': 'json',
            '_no_guide': None,
            'no_guide': False,
            '_quiet': None,
            'quiet': False,
            '_framework': None,
            'framework': 'all',
            '_merging_behavior': 'override_if_present',
            'merging_behavior': 'override_if_present',
            'check': 'CKV_AWS_1,CKV_AWS_3',
            'skip_check': None,
            '_soft_fail': True,
            'soft_fail': True,
            'repo_id': None,
            '_branch': 'b/123',
            'branch': 'b/123',
        }, config)

    def test_merge_with_none(self):
        config = CheckovConfig('test', directory=['1', '2'], check='CKV_AWS_1,CKV_AWS_10', soft_fail=True, quiet=False)
        expected = CheckovConfig('test', directory=['1', '2'], check='CKV_AWS_1,CKV_AWS_10', soft_fail=True,
                                 quiet=False)
        config.extend(None)
        self.assertConfig(expected, config)

    def test_merge_config_no_override_if_defined(self):
        config1 = CheckovConfig('test')
        parent1 = CheckovConfig('test', directory=['1', '2'], check='CKV_AWS_1,CKV_AWS_10', soft_fail=True, quiet=False)
        config1.extend(parent1)
        self.assertConfig(parent1, config1)

        config2 = CheckovConfig('test')
        parent2 = CheckovConfig('test', no_guide=True, framework='terraform', repo_id='123', branch='456', check='3,4')
        config2.extend(parent2)
        self.assertConfig(parent2, config2)

    def test_merge_does_not_change_parent(self):
        config = CheckovConfig('test')
        parent = CheckovConfig('p2', no_guide=True, framework='terraform', repo_id='123', branch='456', check='3,4')
        parent_clone = CheckovConfig('p2', no_guide=True, framework='terraform', repo_id='123', branch='456',
                                     check='3,4')
        config.extend(parent)
        self.assertConfig(parent_clone, parent, 'Parent should not be modified')

    def test_merge_sets_are_combined(self):
        child = CheckovConfig('test_child', directory=['a', 'b', 'c'], file=['g', 'h', 'i'],
                              external_checks_dir=['m', 'n', 'o'], external_checks_git=['s', 't', 'u'])
        parent = CheckovConfig('test_parent', directory=['c', 'd', 'e'], file=['i', 'j', 'k'],
                               external_checks_dir=['o', 'p', 'q'], external_checks_git=['u', 'v', 'w'])
        expected = CheckovConfig('test_child', directory=['a', 'b', 'c', 'd', 'e'], file=['g', 'h', 'i', 'j', 'k'],
                                 external_checks_dir=['m', 'n', 'o', 'p', 'q'],
                                 external_checks_git=['s', 't', 'u', 'v', 'w'])
        child.extend(parent)
        self.assertConfig(expected, child)

    def test_merge_set_boolean_not_overridden(self):
        child_true = CheckovConfig('test_child', no_guide=True, quiet=True, soft_fail=True)
        child_true_clone = CheckovConfig('test_child', no_guide=True, quiet=True, soft_fail=True)
        child_false = CheckovConfig('test_child', no_guide=False, quiet=False, soft_fail=False)
        child_false_clone = CheckovConfig('test_child', no_guide=False, quiet=False, soft_fail=False)

        parents = [
            CheckovConfig('', no_guide=True, quiet=False, soft_fail=False),
            CheckovConfig('', no_guide=False, quiet=True, soft_fail=True),
            CheckovConfig(''),
            CheckovConfig('', no_guide=False),
            CheckovConfig('', soft_fail=True),
        ]

        self.assertConfig(child_true_clone, child_true)
        self.assertConfig(child_false_clone, child_false)
        for parent in parents:
            child_true.extend(parent)
            child_false.extend(parent)
            self.assertConfig(child_true_clone, child_true)
            self.assertConfig(child_false_clone, child_false)

    def test_merge_check_skip_check_merging_check_set(self):
        child = CheckovConfig('test', check='1')
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1'), child)
        child.extend(CheckovConfig('test', check='D,9'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1,D,9'), child)
        child.extend(CheckovConfig('test', check='123,4,2', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', check='1,D,9,123,4,2'), child)

    def test_merge_check_skip_check_merging_skip_check_set(self):
        child = CheckovConfig('test', skip_check='2')
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test', check='KL,asd'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2'), child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2,D,5'), child)
        child.extend(CheckovConfig('test', check='123', skip_check='K'))
        self.assertCheckSkipCheckIsValid(child)
        self.assertConfig(CheckovConfig('test', skip_check='2,D,5,K'), child)

    def test_merge_invalid_check_skip_check_constellation(self):
        child = CheckovConfig('test', check='1', skip_check='2')
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', check='2'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', skip_check='D,5'))
        self.assertCheckSkipCheckIsInvalid(child)
        child.extend(CheckovConfig('test', check='123', skip_check='D,5'))
        self.assertCheckSkipCheckIsInvalid(child)

    def test_merge_copy_from_parent_if_not_set(self):
        child = CheckovConfig('t1')
        parent = CheckovConfig('t2', check='1', skip_check='2')
        child.extend(parent)
        expected = CheckovConfig('t1', check='1', skip_check='2')
        self.assertConfig(expected, child)

    def test_merge_union(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            config = CheckovConfig('test1', merging_behavior='union', no_guide=False, framework='all', check='1,2')
            parent = CheckovConfig('test2', merging_behavior=parent_merging_behavior, no_guide=True,
                                   framework='terraform', repo_id='123', branch='456', check='3,4')
            expected = CheckovConfig('test1', merging_behavior='union', no_guide=False, framework='all',
                                     check='1,2,3,4',
                                     repo_id='123', branch='456')
            config.extend(parent)
            self.assertConfig(expected, config,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')

    def test_merge_union_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', check='1', merging_behavior='union')
            child2 = CheckovConfig('t2', merging_behavior='union')
            parent = CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', check='1,2', merging_behavior='union'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with union')
            self.assertConfig(CheckovConfig('t2', check='2', merging_behavior='union'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with union')
            self.assertConfig(CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_union_skip_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', skip_check='1', merging_behavior='union')
            child2 = CheckovConfig('t2', merging_behavior='union')
            parent = CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', skip_check='1,2', merging_behavior='union'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with union')
            self.assertConfig(CheckovConfig('t2', skip_check='2', merging_behavior='union'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with union')
            self.assertConfig(CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_override(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            config = CheckovConfig('test1', merging_behavior='override', no_guide=False, framework='all', check='1,2')
            parent = CheckovConfig('test2', merging_behavior=parent_merging_behavior, no_guide=True,
                                   framework='terraform', repo_id='123', branch='456', check='3,4')
            expected = CheckovConfig('test1', merging_behavior='override', no_guide=False, framework='all', check='1,2')
            config.extend(parent)
            self.assertConfig(expected, config,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')

    def test_merge_override_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', check='1', merging_behavior='override')
            child2 = CheckovConfig('t2', merging_behavior='override')
            parent = CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', check='1', merging_behavior='override'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with override')
            self.assertConfig(CheckovConfig('t2', check=None, merging_behavior='override'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with override')
            self.assertConfig(CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_override_skip_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', skip_check='1', merging_behavior='override')
            child2 = CheckovConfig('t2', merging_behavior='override')
            parent = CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', skip_check='1', merging_behavior='override'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with override')
            self.assertConfig(CheckovConfig('t2', skip_check=None, merging_behavior='override'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with override')
            self.assertConfig(CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_override_if_present(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            config1 = CheckovConfig('test1', merging_behavior='override_if_present', no_guide=False, framework='all',
                                    check='1,2', directory=['a', 'b'])
            parent1 = CheckovConfig('test2', merging_behavior=parent_merging_behavior, no_guide=True,
                                    framework='terraform', repo_id='123', branch='456', check='3,4',
                                    directory=['c', 'd'], external_checks_dir=['x'])
            expected1 = CheckovConfig('test1', merging_behavior='override_if_present', no_guide=False, framework='all',
                                      check='1,2', directory=['a', 'b'], external_checks_dir=['x'], repo_id='123',
                                      branch='456')
            config1.extend(parent1)
            self.assertConfig(expected1, config1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')

            config2 = CheckovConfig('test1', merging_behavior='override_if_present', no_guide=False, framework='all',
                                    check='1,2', directory=['a', 'b'], external_checks_dir=['a'])
            parent2 = CheckovConfig('test2', merging_behavior=parent_merging_behavior, no_guide=True,
                                    framework='terraform', repo_id='123', branch='456', check='3,4',
                                    directory=['c', 'd'], external_checks_dir=['x'])
            expected2 = CheckovConfig('test1', merging_behavior='override_if_present', no_guide=False, framework='all',
                                      check='1,2', directory=['a', 'b'], external_checks_dir=['a'], repo_id='123',
                                      branch='456')
            config2.extend(parent2)
            self.assertConfig(expected2, config2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')

    def test_merge_override_if_present_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', check='1', merging_behavior='override_if_present')
            child2 = CheckovConfig('t2', merging_behavior='override_if_present')
            parent = CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', check='1', merging_behavior='override_if_present'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with '
                              f'override_if_present')
            self.assertConfig(CheckovConfig('t2', check='2', merging_behavior='override_if_present'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with '
                              f'override_if_present')
            self.assertConfig(CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_override_if_present_skip_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', skip_check='1', merging_behavior='override_if_present')
            child2 = CheckovConfig('t2', merging_behavior='override_if_present')
            parent = CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', skip_check='1', merging_behavior='override_if_present'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with '
                              f'override_if_present')
            self.assertConfig(CheckovConfig('t2', skip_check='2', merging_behavior='override_if_present'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with '
                              f'override_if_present')
            self.assertConfig(CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_copy_parent(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            config = CheckovConfig('test1', merging_behavior='copy_parent', no_guide=False, framework='all',
                                   check='1,2', directory=['a', 'b'])
            parent = CheckovConfig('test2', merging_behavior=parent_merging_behavior, no_guide=True,
                                   framework='terraform', repo_id='123', branch='456', check='3,4',
                                   directory=['c', 'd'], external_checks_dir=['x'])
            expected = CheckovConfig('test1', merging_behavior='copy_parent', no_guide=True, framework='terraform',
                                     repo_id='123', branch='456', check='3,4', directory=['c', 'd'],
                                     external_checks_dir=['x'])
            config.extend(parent)
            self.assertConfig(expected, config,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')

    def test_merge_copy_parent_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', check='1', merging_behavior='copy_parent')
            child2 = CheckovConfig('t2', merging_behavior='copy_parent')
            parent = CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', check='2', merging_behavior='copy_parent'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')
            self.assertConfig(CheckovConfig('t2', check='2', merging_behavior='copy_parent'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')
            self.assertConfig(CheckovConfig('t0', check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_merge_override_if_present_skip_check(self):
        for parent_merging_behavior in MERGING_BEHAVIOR_CHOICES:
            child1 = CheckovConfig('t1', skip_check='1', merging_behavior='copy_parent')
            child2 = CheckovConfig('t2', merging_behavior='copy_parent')
            parent = CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior)
            child1.extend(parent)
            child2.extend(parent)
            self.assertConfig(CheckovConfig('t1', skip_check='2', merging_behavior='copy_parent'), child1,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')
            self.assertConfig(CheckovConfig('t2', skip_check='2', merging_behavior='copy_parent'), child2,
                              f'Test that parent having the {parent_merging_behavior} behavior works with copy_parent')
            self.assertConfig(CheckovConfig('t0', skip_check='2', merging_behavior=parent_merging_behavior),
                              parent, 'Test that parent did not change')

    def test_yaml_load_empty_file_by_path(self):
        config = CheckovConfig.from_file(self.get_config_file('empty.yaml'))
        self.assertConfig(CheckovConfig('file'), config)

    def test_yaml_full_empty_file_by_path(self):
        config = CheckovConfig.from_file(self.get_config_file('full.yaml'))
        expected = CheckovConfig('file', directory=['/a', '/b', 'c', '1'], file=['/a/m.tf', 'd.tf'],
                                 external_checks_dir=['/x', 'y'], external_checks_git=['a/b', 'c/d'], output='json',
                                 no_guide=True, quiet=False, framework='kubernetes', merging_behavior='union',
                                 check='1, a ,d', skip_check='2, b ,d', soft_fail=True, repo_id='1 2',
                                 branch='feature/abc')
        self.assertConfig(expected, config)

    def test_yaml_file_with_additional_keys_by_path(self):
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(self.get_config_file('additional_keys.yaml'))
        self.assertIn('something', str(context.exception))
        self.assertIn('other', str(context.exception))
        self.assertIn('mm', str(context.exception))
        self.assertNotIn('asd', str(context.exception))
        self.assertNotIn('not_in_list', str(context.exception))

    def test_yaml_file_with_invalid_syntax_by_path(self):
        self.assertRaises(CheckovConfigError, CheckovConfig.from_file, self.get_config_file('invalid_syntax.yaml'))

    def test_yaml_file_checks_string_by_io(self):
        buffer = io.StringIO("""
checks: 1,2,3
skip_checks: "1"
""")
        config = CheckovConfig.from_file(buffer)
        self.assertConfig(CheckovConfig('file', check='1,2,3', skip_check='1'), config)

    def test_yaml_file_invalid_output_is_detected_by_io(self):
        buffer = io.StringIO("""
output: lorem123
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('output', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('lorem123', str(context.exception), 'Error should echo the incorrect value.')
        for choice in map(lambda c: f'"{c}"', OUTPUT_CHOICES):
            self.assertIn(choice, str(context.exception), 'Error should contain all valid choices.')

    def test_yaml_file_invalid_framework_is_detected_by_io(self):
        buffer = io.StringIO("""
framework: abc123
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('framework', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('abc123', str(context.exception), 'Error should echo the incorrect value.')
        for choice in map(lambda c: f'"{c}"', FRAMEWORK_CHOICES):
            self.assertIn(choice, str(context.exception), 'Error should contain all valid choices.')

    def test_yaml_file_wrong_case_error_in_output_is_detected_by_io(self):
        buffer = io.StringIO("""
output: JSON
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('output', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('json', str(context.exception), 'Error should echo the correct value.')

    def test_yaml_file_wrong_case_error_in_framework_is_detected_by_io(self):
        buffer = io.StringIO("""
framework: TERRafORM
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('framework', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('terraform', str(context.exception), 'Error should echo the correct value.')

    def test_yaml_file_set_can_be_set_to_single_value_by_string_by_io(self):
        buffer = io.StringIO("""
---

directories: a
files: b
external_checks_dirs: c
external_checks_gits: d
""")
        config = CheckovConfig.from_file(buffer)
        self.assertConfig(
            CheckovConfig('file', directory=['a'], file=['b'], external_checks_dir=['c'], external_checks_git=['d']),
            config)

    def test_config_load_empty_file_by_path(self):
        config = CheckovConfig.from_file(self.get_config_file('empty'))
        self.assertConfig(CheckovConfig('file'), config)

    def test_config_full_empty_file_by_path(self):
        config = CheckovConfig.from_file(self.get_config_file('full'))
        expected = CheckovConfig('file', directory=['/a', '/b', 'c', '1'], file=['/a/m.tf', 'd.tf'],
                                 external_checks_dir=['/x', 'y'], external_checks_git=['a/b', 'c/d'], output='json',
                                 no_guide=True, quiet=False, framework='kubernetes', merging_behavior='union',
                                 check='1, a ,d', skip_check='2, b ,d', soft_fail=True, repo_id='1 2',
                                 branch='feature/abc')
        self.assertConfig(expected, config)

    def test_config_file_with_additional_keys_by_path(self):
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(self.get_config_file('additional_keys'))
        self.assertIn('something', str(context.exception))
        self.assertIn('other', str(context.exception))
        self.assertIn('mm', str(context.exception))
        self.assertNotIn('asd', str(context.exception))
        self.assertNotIn('not_in_list', str(context.exception))
        self.assertNotIn('xxx123', str(context.exception))
        self.assertNotIn('abc123', str(context.exception))

    def test_config_file_with_invalid_syntax_by_path(self):
        self.assertRaises(CheckovConfigError, CheckovConfig.from_file, self.get_config_file('invalid_syntax'))

    def test_config_file_checks_string_by_io(self):
        buffer = io.StringIO("""
[checkov]
checks = 1,2,3
skip_checks = "1"
""")
        config = CheckovConfig.from_file(buffer)
        self.assertConfig(CheckovConfig('file', check='1,2,3', skip_check='1'), config)

    def test_config_file_invalid_output_is_detected_by_io(self):
        buffer = io.StringIO("""
[checkov]
output = lorem123
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('output', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('lorem123', str(context.exception), 'Error should echo the incorrect value.')
        for choice in map(lambda c: f'"{c}"', OUTPUT_CHOICES):
            self.assertIn(choice, str(context.exception), 'Error should contain all valid choices.')

    def test_config_file_invalid_framework_is_detected_by_io(self):
        buffer = io.StringIO("""
[checkov]
framework = abc123
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('framework', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('abc123', str(context.exception), 'Error should echo the incorrect value.')
        for choice in map(lambda c: f'"{c}"', FRAMEWORK_CHOICES):
            self.assertIn(choice, str(context.exception), 'Error should contain all valid choices.')

    def test_config_file_wrong_case_error_in_output_is_detected_by_io(self):
        buffer = io.StringIO("""
[checkov]
output = JSON
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('output', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('json', str(context.exception), 'Error should echo the correct value.')

    def test_config_file_wrong_case_error_in_framework_is_detected_by_io(self):
        buffer = io.StringIO("""
[checkov]
framework = TERRafORM
""")
        with self.assertRaises(CheckovConfigError) as context:
            CheckovConfig.from_file(buffer)
        self.assertIn('framework', str(context.exception), 'Error should contain the key whose choice was invalid.')
        self.assertIn('terraform', str(context.exception), 'Error should echo the correct value.')

    def test_config_file_set_can_be_set_to_single_value_by_string_by_io(self):
        buffer = io.StringIO("""
[checkov]

directories = a
files = b
external_checks_dirs = c
external_checks_gits = d
""")
        config = CheckovConfig.from_file(buffer)
        self.assertConfig(
            CheckovConfig('file', directory=['a'], file=['b'], external_checks_dir=['c'], external_checks_git=['d']),
            config)

    def test_is_check_selection_valid(self):
        self.assertTrue(CheckovConfig('test1').is_check_selection_valid)
        self.assertTrue(CheckovConfig('test2', check='1').is_check_selection_valid)
        self.assertTrue(CheckovConfig('test3', skip_check='1').is_check_selection_valid)
        self.assertFalse(CheckovConfig('test4', check='1', skip_check='1').is_check_selection_valid)


class FrozenUniqueListTestCase(unittest.TestCase):
    def test_frozen_unique_list_constructor(self):
        unique_list = FrozenUniqueList()
        self.assertEqual([], list(unique_list))
        unique_list = FrozenUniqueList([])
        self.assertEqual([], list(unique_list))
        unique_list = FrozenUniqueList([1, 2, 3, 1])
        self.assertEqual([1, 2, 3], list(unique_list))

    def test_frozen_unique_list_length(self):
        self.assertEqual(3, len(FrozenUniqueList([1, 2, 3])))
        self.assertEqual(0, len(FrozenUniqueList([])))
        self.assertEqual(5, len(FrozenUniqueList([1, 1, 2, 3, 3, 4, 5, 5, 3, 1, 3, 1])))

    def test_frozen_unique_list_get(self):
        unique_list = FrozenUniqueList([1, 2, 3, 1])
        self.assertEqual(1, unique_list[0])
        self.assertEqual(2, unique_list[1])
        self.assertEqual(3, unique_list[2])

    def test_frozen_unique_list_add(self):
        unique_list = FrozenUniqueList([1, 2, 3, 1]) + FrozenUniqueList([1, 2, 5, 3, 4])
        self.assertEqual([1, 2, 3, 5, 4], list(unique_list))

        unique_list = FrozenUniqueList([1, 2, 3, 1]) + [1, 2, 5, 3, 4]
        self.assertEqual([1, 2, 3, 5, 4], list(unique_list))

    def test_frozen_unique_list_equal(self):
        self.assertEqual(FrozenUniqueList([]), FrozenUniqueList([]))
        self.assertEqual(FrozenUniqueList([1, 2, 1]), FrozenUniqueList([1, 2]))
        self.assertEqual(FrozenUniqueList([1, 2, 3, 1]), FrozenUniqueList([1, 2, 3, 1]))
