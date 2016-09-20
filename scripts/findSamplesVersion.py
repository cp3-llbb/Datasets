#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import subprocess
import sys
import re
import datetime

parser = argparse.ArgumentParser(description='Use DAS to find the correct version of samples.')

parser.add_argument('-i', '--in-place', action='store_true', help='Replace content of input files by new datasets')

parser.add_argument('datasets', type=str, nargs='+', metavar='JSON',
                    help='JSON files listings datasets to run over.')

options = parser.parse_args()

for dataset_file in options.datasets:

    grouped_datasets = {}
    with open(dataset_file) as f:
        grouped_datasets.update(json.load(f))

    new_grouped_datasets = {}

    version_regex = re.compile(r"^/(.*)/(.*)-v(\d+)/(.*)$")
    for group, datasets in grouped_datasets.items():

        new_datasets = {}
        for dataset, data in datasets.items():

            m = version_regex.search(dataset)
            if not m:
                print("Unsupported dataset format")
                continue

            test_dataset = version_regex.sub(r'/\g<1>/\g<2>-v*/\g<4>', dataset)
            sys.stdout.write('Working on %s ... ' % test_dataset)
            sys.stdout.flush()

            # Reset to v1
            new_dataset = version_regex.sub(r'/\g<1>/\g<2>-v1/\g<4>', dataset)

            # Query das
            result = json.loads(subprocess.check_output(['das_client', '--query', 'dataset=%s' % test_dataset, '--format', 'json']))

            if not result or result['status'] != 'ok':
                print(u'\033[91m✗\033[0m (DAS request failed: %s)' % result['reason'])
                data['comment'] = 'DAS request failed: %s' % result['reason']
                new_datasets[new_dataset] = data
                continue

            status = None
            name = None

            for d in result['data'][0]['dataset']:
                if 'status' in d:
                    status = d['status']
                    name = d['name']
                    break

            if status == 'VALID':
                m = version_regex.search(name)
                print('\033[92m✓\033[0m (version %s)' % str(m.group(3)))
                new_dataset = name
                if 'comment' in data:
                    del data['comment']
            elif status is not None:
                print(u'\033[91m✗\033[0m (status: %s)' % status)
                data['comment'] = 'Invalid status: %s' % status
            else:
                print('\033[91m✗\033[0m')
                data['comment'] = 'Dataset does not currently exist (%s)' % (datetime.date.today().strftime('%d, %b %Y'))

            print("")
            new_datasets[new_dataset] = data

        new_grouped_datasets[group] = new_datasets

    j = json.dumps(new_grouped_datasets, indent=2, separators=(',', ': '))
    if not options.in_place:
        print j
        print("")
    else:
        with open(dataset_file, 'w') as f:
            f.write(j)
