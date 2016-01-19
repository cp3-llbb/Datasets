#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description='Launch crab over multiple datasets.')

parser.add_argument('datasets', type=str, nargs='+', metavar='FILE',
                    help='JSON files listings datasets to run over.')

options = parser.parse_args()

datasets = {}
for dataset_file in options.datasets:
    with open(dataset_file) as f:
        datasets.update(json.load(f))

for dataset in datasets.keys():

    sys.stdout.write('%s ... ' % dataset)
    sys.stdout.flush()

    # Query das
    result = json.loads(subprocess.check_output(['das_client', '--query', 'dataset=%s' % dataset, '--format', 'json']))

    status = None
    for d in result['data'][0]['dataset']:
        if 'status' in d:
            status = d['status']
            break

    if status == 'VALID':
        print('\033[92m✓\033[0m')
    elif status is not None:
        print(u'\033[91m✗\033[0m (status: %s)' % status)
    else:
        print('\033[91m✗\033[0m')
