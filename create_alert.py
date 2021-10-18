import json
import copy
import logging

import requests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# TODO: pass in or read from config
api_base_url = 'https://localhost:9200/'

# TODO: handle secrets
auth = ('admin', 'admin')

# TODO: create config file
destination_config = {
    'destination_one': {'host': 'mockbin.org', 'path': 'bin/a2a8ac9e-6696-420b-9ad0-452a766a90c1'},
    'destination_two': {
        'host': 'mockbin.org', 'path': 'bin/a2a8ac9e-6696-420b-9ad0-452a766a90c1'
    }
}

# TODO: rename
monitor_config = [
    {
        'name': 'test_monitor_one',
        'destination_key': 'destination_one',
        'indices': [
            "opensearch_dashboards_sample_data_logs"
        ]
    }
]


def create_destinations():
    response = requests.get(f'{api_base_url}_plugins/_alerting/destinations',
                            auth=auth,
                            verify=False)
    monitor_destinations = []
    if response.status_code == 200:
        monitor_destinations = response.json()['destinations']
    for destination_key in destination_config.keys():
        exists = len(monitor_destinations) > 0 and any(x.get('name') == destination_key for x in monitor_destinations)
        if exists:
            logging.info(f'{destination_key} already exists as a destination')
        else:
            response = requests.post(f'{api_base_url}_plugins/_alerting/destinations',
                                     auth=auth,
                                     verify=False,
                                     json={
                                         'name': destination_key,
                                         'type': 'custom_webhook',
                                         'custom_webhook': {
                                             'path': destination_config[destination_key]['path'],
                                             'header_params': {
                                                 'Content-Type': 'application/json'
                                             },
                                             'scheme': 'HTTPS',
                                             'port': 443,
                                             'host': destination_config[destination_key]['host']
                                         }
                                     })
            logging.info('New destination created.')
            logging.info(response.json())
            monitor_destinations.append(response.json()['destination'])
    logging.info(f'Monitor destinations count: {len(monitor_destinations)}')
    logging.info(monitor_destinations)
    return monitor_destinations


def create_monitors(monitor_destinations):
    # TODO: clean up to get absolute file path
    with open('monitor_template.tpl.json') as monitor_template_file:
        monitor_template = json.load(monitor_template_file)
    _create_monitors(monitor_destinations, monitor_template)


def _create_monitors(monitor_destinations, monitor_template):
    for monitor in monitor_config:
        monitor_template_copy = copy.deepcopy(monitor_template)
        monitor_template_copy['name'] = monitor['name']

        _set_monitor_indices(monitor, monitor_template_copy)

        _set_destination(monitor_template_copy, monitor, monitor_destinations)

        response = requests.post(f'{api_base_url}_plugins/_alerting/monitors',
                                 auth=('admin', 'admin'),
                                 verify=False,
                                 json=monitor_template_copy)
        logging.info(response.json())


def _set_monitor_indices(monitor, monitor_template_copy):
    for monitor_input in monitor_template_copy['inputs']:
        monitor_input['search']['indices'] = monitor['indices']


def _set_destination(monitor_template_copy, monitor, monitor_destinations):
    # TODO: handle multiple trigger types
    for monitor_trigger in monitor_template_copy['triggers']:
        for action in monitor_trigger['query_level_trigger']['actions']:
            print(monitor_destinations)
            filtered_destinations = list(filter(lambda x: x.get('name') == monitor['destination_key'], monitor_destinations))
            print(filtered_destinations)
            destination = filtered_destinations[0]
            action['destination_id'] = destination['id']


destinations = create_destinations()
logging.info(destinations)
create_monitors(destinations)
