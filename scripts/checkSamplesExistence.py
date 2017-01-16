#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
import sys

parser = argparse.ArgumentParser(description='Test if a sample exists or not in DBS')

parser.add_argument('datasets', type=str, nargs='+', metavar='FILE',
                    help='JSON files listings datasets to run over.')

options = parser.parse_args()

grouped_datasets = {}
for dataset_file in options.datasets:
    with open(dataset_file) as f:
        grouped_datasets.update(json.load(f))

for group, datasets in grouped_datasets.items():
    for dataset in datasets.keys():

        sys.stdout.write('%s ... ' % dataset)
        sys.stdout.flush()

        # Query das
        result = json.loads(subprocess.check_output(['das_client', '--query', 'dataset=%s' % dataset, '--format', 'json']))

        status = None
        if len(result['data']) == 0:
            print("DAS error:")
            import pprint
            pprint.pprint(result)
            continue

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
