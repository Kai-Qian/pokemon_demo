#!/usr/bin/env python
"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import os
import sys
import json
import time
import pprint
import logging
import getpass
import argparse

# add directory of this file to PATH, so that the package will be found
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# import Pokemon Go API lib
from mock_pgoapi import mock_pgoapi as pgoapi
from pgoapi import utilities as util


log = logging.getLogger(__name__)

def init_config():
    parser = argparse.ArgumentParser()
    config_file = "config.json"

    # If config file exists, load variables from json
    load   = {}
    if os.path.isfile(config_file):
        with open(config_file) as data:
            load.update(json.load(data))

    # Read passed in Arguments
    required = lambda x: not x in load
    parser.add_argument("-a", "--auth_service", help="Auth Service ('ptc' or 'google')",
        required=required("auth_service"))
    parser.add_argument("-u", "--username", help="Username", required=required("username"))
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-l", "--location", help="Location", required=required("location"))
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-t", "--test", help="Only parse the specified location", action='store_true')
    parser.add_argument("-px", "--proxy", help="Specify a socks5 proxy url")
    parser.set_defaults(DEBUG=False, TEST=False)
    config = parser.parse_args()

    # Passed in arguments shoud trump
    for key in config.__dict__:
        if key in load and config.__dict__[key] == None:
            config.__dict__[key] = str(load[key])

    if config.__dict__["password"] is None:
        log.info("Secure Password Input (if there is no password prompt, use --password <pw>):")
        config.__dict__["password"] = getpass.getpass()

    if config.auth_service not in ['ptc', 'google']:
      log.error("Invalid Auth service specified! ('ptc' or 'google')")
      return None

    return config


def main():
    # log settings
    # log format
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(module)10s] [%(levelname)5s] %(message)s')
    # log level for http request class
    logging.getLogger("requests").setLevel(logging.WARNING)
    # log level for main pgoapi class
    logging.getLogger("pgoapi").setLevel(logging.INFO)
    # log level for internal pgoapi class
    logging.getLogger("rpc_api").setLevel(logging.INFO)

    config = init_config()
    if not config:
        return

    if config.debug:
        logging.getLogger("requests").setLevel(logging.DEBUG)
        logging.getLogger("pgoapi").setLevel(logging.DEBUG)
        logging.getLogger("rpc_api").setLevel(logging.DEBUG)


    # instantiate pgoapi
    api = pgoapi.PGoApi()
    if config.proxy:
        api.set_proxy({'http': config.proxy, 'https': config.proxy})

    # parse position
    position = util.get_pos_by_name(config.location)
    if not position:
        log.error('Your given location could not be found by name')
        return
    elif config.test:
        return

    # set player position on the earth
    api.set_position(*position)

    # new authentication initialitation
    if config.proxy:
        api.set_authentication(provider = config.auth_service, username = config.username, password =  config.password, proxy_config = {'http': config.proxy, 'https': config.proxy})
    else:
        api.set_authentication(provider = config.auth_service, username = config.username, password =  config.password)

    # provide the path for your encrypt dll
    api.activate_signature("/home/ubuntu/pgoapi/libencrypt.so")

    # print get maps object
    cell_ids = util.get_cell_ids(position[0], position[1])
    timestamps = [0,] * len(cell_ids)
    response_dict = api.get_map_objects(latitude =position[0], longitude = position[1], since_timestamp_ms = timestamps, cell_id = cell_ids)
    print('Response dictionary (get_player): \n\r{}'.format(json.dumps(response_dict, indent=2)))


if __name__ == '__main__':
    main()
