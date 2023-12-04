#!/usr/bin/env python
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument
#
# All unit-test methods must be public
# Mock is
"""
unit test for create_manifests.py
"""
from __future__ import absolute_import
import unittest
import os
import os.path
import shutil
from mock import patch
import six
import hsp_cf.create_manifests as cm

FileError = IOError
if six.PY3:
    FileError = FileNotFoundError


class TestCreateManifest(unittest.TestCase):
    """
    Parse command line args.
    Simple function to parse and return command line args.

    """

    def setUp(self):
        """Parse command line args.

        Simple function to parse and return command line args.
        """

        my_path = os.path.abspath(os.path.dirname(__file__))
        self.config = os.path.join(my_path, "configurations/deployment-config.yaml")
        self.template_names = ['01_randomnumber.yml.j2', '02_greetuser.yml.j2']
        self.manifest_path = os.path.join(my_path, "manifests")
        self.template_path = os.path.join(my_path, "templates")

    def tearDown(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        file = open('deploy.log', 'r+')
        file.truncate(0)
        file.close()

        if os.path.isdir(self.manifest_path):
            shutil.rmtree(self.manifest_path)

    @patch('hsp_cf.create_manifests.logging.debug')
    def test_log(self, mock_log):
        """
        successful execution of log method.
        """
        cm.log("test_log")

    @patch('hsp_cf.create_manifests.logging.debug')
    def test_log_none(self, mock_log):
        """
        successful execution of log method.
        """
        cm.log(None)

    def test_render_manifest_successful_creation(self):
        """
        successful creation of manifest files in manifest folder
        """
        cm.render_manifests(self.config, self.template_names,
                            self.template_path, self.manifest_path)

    def test_render_manifest_invalid_config_path(self):
        """
        FileNotFoundError exception is thrown if invalid config file path is provided
        """
        config = 'invalid_path'
        self.assertRaises(FileError, cm.render_manifests, config, self.template_names,
                          self.template_path, self.manifest_path)

    def test_render_manifest_invalid_templates_name(self):
        """
        FileNotFoundError exception is thrown if invalid template names
        """
        config = 'invalid_path'
        invalid_template_names = ['01_random.yml.j2', '02_greet.yml.j2']
        self.assertRaises(FileError, cm.render_manifests,
                          config, invalid_template_names, self.template_path,
                          self.manifest_path)

    def test_merge_manifest_successful(self):
        """
        Successful merge of manifest files
        :returns true, indicating merge is successful
        """
        cm.render_manifests(self.config, self.template_names,
                            self.template_path, self.manifest_path)
        self.assertTrue(cm.merge_manifests(self.manifest_path))

    def test_merge_manifest_invalid_config(self):
        """
        Successful merge of manifest files
        :returns true, indicating merge is successful
        """
        config = '../invalid'
        self.assertRaises(FileError, cm.render_manifests,
                          config, self.template_names, self.template_path,
                          self.manifest_path)

    def test_merge_manifest_no_manifests(self):
        """
        No manifest files in manifest folder, merge operation is not performed
        :returns false, indicating merge is failed
        """
        os.mkdir(self.manifest_path)
        cm.purge(self.template_names, self.manifest_path)
        self.assertFalse(cm.merge_manifests(self.manifest_path))

    def test_merge_manifest_invalid_path(self):
        """
        Invalid file path, failed merge operation
        :returns false, indicating merge is failed
        """
        path = './invalid'
        cm.purge(self.template_names, self.manifest_path)
        self.assertRaises(Exception, cm.merge_manifests, path)

    def test_purge_successful(self):
        """
        Purge operation is successful
        """
        cm.render_manifests(self.config, self.template_names,
                            self.template_path, self.manifest_path)
        self.assertTrue(cm.purge(self.template_names, self.manifest_path))

    def test_purge_manifestdir_doesnot_exsits(self):
        """
        Purge operation fails if the path provied is invalid
        """
        invalid_manifest = 'invalid'
        self.assertFalse(cm.purge(self.template_path, invalid_manifest))

    def test_purge_invalid_template(self):
        """
        Purge operation fails if the path provied is invalid
        """
        invalid_template = 'invalid'
        self.assertFalse(cm.purge(invalid_template, self.manifest_path))

    def test_parse_args_successful(self):
        """
        Parse args is successful, expects -template and manifest path
        """
        parsed = cm.parse_args(['--create', 'test', '--template',
                                self.template_path, '--manifest', self.manifest_path])
        self.assertEqual(parsed.create, 'test')

    def test_parse_args_verify_template_manifest(self):
        """
        Parse args is successful, verify template and manifest names
        """
        parsed = cm.parse_args(['--create', 'test', '--template',
                                self.template_path, '--manifest', self.manifest_path])
        self.assertEqual(parsed.template, self.template_path)
        self.assertEqual(parsed.manifest, self.manifest_path)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestCreateManifest)
    runner.run(itersuite)
