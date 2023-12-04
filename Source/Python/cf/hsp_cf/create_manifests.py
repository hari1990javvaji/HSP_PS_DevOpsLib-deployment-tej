#!/usr/bin/env python
# pylint: disable=invalid-name
#
# This is disabled due to the use of single character variable names
# within context managers and list comprehensions.  Single character
# variables are acceptable in these use cases where the intent is
# clear within a couple of lines of code.
"""This script will generate Cloud Foundry manifest files based on an
environment configuration stored in a yaml file in the local directory.  The
configuration filename should be passed in with --config option and must
adhere to the format specified in the README in this project.  All manifest
files can also be merged into a single master manifest for ease of deployment
on larger projects with the --merge argument.  All generated manifests can
also be removed by using the --clean argument.
"""
from __future__ import absolute_import, print_function
import re
import os
import argparse
import logging
import yaml
from jinja2 import Environment, FileSystemLoader
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='./deploy.log',
    filemode='a'
)


def log(msg):
    """Simple logging function.

    Simple function to print and log events during processing of manifest
    files.  The log file will be written to ./deploy.log.

    Args:
        msg (str): A log message.
    """

    print(msg)
    logging.debug(msg)


def purge(template_names, manifest_path):
    """Cleans all generated manifest files from the manifest directory.

    This will remove all generated manifest files from the MANIFEST_PATH.
    Only manifest files that have corresponding template files will be
    removed.  The one exception to this is the master manifest file since
    it is generated from other manifests and not from a template.

    Args:
        template_names (list[str]): A list of template names that is used
            to generate manifest names that should be removed.
            :param template_names:
            :param manifest_path:
    """
    if os.path.isdir(manifest_path):
        for template_name in template_names:
            manifest_name = '.'.join(template_name.split('.')[:2])
            manifest_file = os.path.join(manifest_path, manifest_name)
            try:
                os.remove(manifest_file)
            except OSError:
                pass
            log('Removing {0}'.format(manifest_file))
        master_manifest = os.path.join(manifest_path, 'master_manifest.yml')
        for manifest in master_manifest:
            if os.path.isfile(manifest):
                os.remove(manifest)
                log('Removing {0}'.format(manifest))
        log('All generated manifests have been removed.')
        return True
    else:
        log('Manifest directory does not exist.')
        return False


def render_manifests(config_file, template_names, infolder, outfolder):
    """Renders all template files into usable manifest files.

    This function will take the base config file and a list of template names
    to use for generating manifest files.  Templates must be valid jinja2
    templates and the config file must be a yaml file with the required data
    for the templates.  Templates are expected to exist in the TEMPLATE_PATH
    directory and generated manifests will be output to the MANIFEST_PATH
    directory.

    Args:
        config_file (str): The path to the yaml config file needed to render
            the manifest templates.
        template_names (list[str]): A list containing the names of the
            template files to render.
            :param outfolder:
            :param template_names:
            :param config_file:
            :param infolder:
    """

    if not os.path.isdir(outfolder):
        os.mkdir(outfolder)
    with open(config_file) as _f:
        config = yaml.safe_load(_f.read())
    j2 = Environment(loader=FileSystemLoader(infolder), trim_blocks=True, autoescape=True)
    applist_file = os.path.join(outfolder, "applist.txt")
    lstfile = open(applist_file, 'w')
    i = 0
    for template_name in template_names:
        template = j2.get_template(template_name)
        manifest_contents = template.render(**config)
        manifest_name = '.'.join(template_name.split('.')[:2])
        manifest_file = os.path.join(outfolder, manifest_name)
        with open(manifest_file, 'w') as f:
            log('Generating {0}'.format(manifest_file))
            f.write(manifest_contents)
        with open(manifest_file, 'r') as _file:
            mf_f = yaml.safe_load(_file.read())
            apps = mf_f['applications']
            print(apps[0]['name'])
            i = i + 1
            lstfile.write(apps[0]['name'] + ':' + manifest_name + '\n')
    log('Completed manifest generation.')


def merge_manifests(outfolder):
    """Merges all manifests into a single master manifest for easy deployment.

    When this option is used all generated manifests will be merged into
    a single manifest file called master_manifest.yml.  The contents of
    base_manifest will be used as the base manifest and the applications
    section of all other manifests will be merged into the applications
    section of the master_manifest file.
    """
    mastermanifestfile = os.path.join(outfolder, 'master_manifest.yml')

    manifests = [
        os.path.join(outfolder, f)
        for f in os.listdir(outfolder)
        if re.match(r'^[0-9]', f)
    ]
    applications = []
    for manifest in manifests:
        manifest_data = yaml.safe_load(open(manifest, 'r').read())
        for a in manifest_data['applications']:
            log('Merging {0} into master_manifest.yml.'.format(manifest))
            applications.append(a)
    if not applications:
        print("No manifest files present")
        return False
    with open(mastermanifestfile, 'w') as f:
        log('Writing master_master.yml.')
        f.write(yaml.safe_dump({'applications': applications}, default_flow_style=False, sort_keys=False))
    log('Successfully merged all manifest files into master_manifest.yml')
    return True


def parse_args(args=None):
    """Parse command line args.

    Simple function to parse and return command line args.

    Returns:
        argparse.Namespace: An argparse.Namespace object.
    """
    parser = argparse.ArgumentParser()
    required_arg = parser.add_argument_group(
        'Action', 'One of these args is required.')
    action = required_arg.add_mutually_exclusive_group(required=True)
    action.add_argument('-c',
                        '--create',
                        dest='create',
                        default=None,
                        required=False,
                        help='Create manifest files from a config file.')
    action.add_argument('-p',
                        '--purge',
                        dest='purge',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Purge all generated manifests')

    parser.add_argument('-m',
                        '--merge',
                        dest='merge',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Merge all generated manifests to create a master '
                             'deployment manifest.')
    parser.add_argument('-o',
                        '--out',
                        dest='out',
                        required=False,
                        default=None,
                        action='store',
                        help='Sub-folder under manifests folder, to generate all '
                             'deployment manifest files. If not provided will'
                             'generate all manifest files in manifests folder')
    parser.add_argument('-i',
                        '--input',
                        dest='input',
                        required=False,
                        default=None,
                        action='store',
                        help='Sub-folder under templates where environment'
                             'specific or deploy type specific app manifest'
                             'templates folder.')
    parser.add_argument('--template',
                        dest='template',
                        required=True,
                        default='../templates',
                        action='store',
                        help='templates path')

    parser.add_argument('--manifest',
                        dest='manifest',
                        required=True,
                        default='../manifests',
                        action='store',
                        help='manifest path')

    return parser.parse_args(args)

