#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

import utils
from utils import get_module_logger
from hiveserver2_info import HiveServer2Collector

logger = get_module_logger(__name__)

def register_prometheus(cluster, args):
    if args.his is not None and len(args.his) > 0:
        REGISTRY.register(HiveServer2Collector(cluster, args.his))

def main():
    args = utils.parse_args()
    host = args.host
    port = int(args.port)
    start_http_server(port, host)
    print("Listen at %s:%s" % (host, port))
    register_prometheus(args.cluster, args)
    while True:
        time.sleep(300)


if __name__ == "__main__":
    main()
