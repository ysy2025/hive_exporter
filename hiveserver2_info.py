#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import yaml
import re

from prometheus_client.core import GaugeMetricFamily

from utils import get_module_logger
from common import MetricCollector, CommonMetricCollector
from scraper import ScrapeMetrics

logger = get_module_logger(__name__)


class HiveServer2Collector(MetricCollector):
    def __init__(self, cluster, urls):
        MetricCollector.__init__(self, cluster, "hive", "hive_server2")
        self.target = "-"
        self.urls = urls
        self.dns = set()

        # print("cluster, urls, dns: ", cluster, self.urls, self.dns)

        self.hive_server2_metrics = {}
        for i in range(len(self.file_list)):
            self.hive_server2_metrics.setdefault(self.file_list[i], {})

        # print("hive_server2_metrics: ", self.hive_server2_metrics)

        self.common_metric_collector = CommonMetricCollector(cluster, "hive", "hive_server2")
        # print("common_metric_collector ", self.common_metric_collector.cluster,self.common_metric_collector.componet,self.common_metric_collector.service,self.common_metric_collector.prefix,self.common_metric_collector.common_metrics,self.common_metric_collector.tmp_metrics)

        self.scrape_metrics = ScrapeMetrics(urls)
        # print("scrape_metrics ", self.scrape_metrics.urls)



    def collect(self):
        isSetup = False
        beans_list = self.scrape_metrics.scrape()
        # print("beans_list is ", beans_list)
        # print("^" * 20)
        for beans in beans_list:
            if not isSetup:
                self.common_metric_collector.setup_labels(beans)
                # print("common_metric_collector is ", self.common_metric_collector.cluster,self.common_metric_collector.componet,self.common_metric_collector.service,self.common_metric_collector.prefix,self.common_metric_collector.common_metrics,self.common_metric_collector.tmp_metrics)
                # print("^" * 20)
                self.setup_metrics_labels(beans)
                # print("self.setup_metrics_labels is ", self.setup_metrics_labels)
                # print("/" * 20)
                isSetup = True
            for i in range(len(beans)):
                if 'tag.Hostname' in beans[i]:
                    self.target = beans[i]["tag.Hostname"]
                    break
            self.hive_server2_metrics.update(self.common_metric_collector.get_metrics(beans, self.target))
            # print("self.hive_server2_metrics is ", self.hive_server2_metrics)

            self.get_metrics(beans)

        for i in range(len(self.merge_list)):
            service = self.merge_list[i]
            print("service is ", service)
            print("+" * 20)
            if service in self.hive_server2_metrics:
                print("self.hive_server2_metrics[service] is ", self.hive_server2_metrics[service])
                print("#" * 20)
                for metric in self.hive_server2_metrics[service]:
                    yield self.hive_server2_metrics[service][metric]

    def setup_higc_labels(self):
        print(self.metrics)
        for metric in self.metrics['GarbageCollector']:
            if 'LastGcInfo' in metric:
                name = "_".join([self.prefix, "hs2_jvm_method_last_gc"])
                description = "last garbage clean in hive."
                self.hive_server2_metrics['GarbageCollector']["LastGcInfo"] = GaugeMetricFamily(name, description, labels=["cluster", "_target"])

    def setup_metrics_labels(self, beans):
        for i in range(len(beans)):
            if 'GarbageCollector' in beans[i]['name']:
                self.setup_higc_labels()


    def get_hs2_gc_metrics(self, bean):
        print("bean is ", bean)
        print("-" * 20)
        print("self.metrics is ", self.metrics)
        for metric in self.metrics['GarbageCollector']: # 这里说明,json里面的属性决定了输出多少指标
            print("metrics is ", metric)
            print("2" * 20)

            # for each in bean[metric]:
            #     print(each)
            #     print("&" * 20)
            if "LastGcInfo" in metric:
                for each in bean[metric]:
                    if "duration" in each:
                        method = "duration"
                        key = metric
                        label = [self.cluster, method, self.target]
                        self.hive_server2_metrics['GarbageCollector'][key].add_metric(label, bean[metric][
                                "duration"] if metric in bean else 0)
                    if "memoryUsageAfterGc" in each:
                        for each_part in bean[metric]["memoryUsageAfterGc"]:
                            method = each_part["key"]
                            key = metric
                            label = [self.cluster, method, self.target]
                            self.hive_server2_metrics['GarbageCollector'][key].add_metric(label, each_part['value']['used'] if metric in bean else 0)
                    if "memoryUsageBeforeGc" in each:
                        for each_part in bean[metric]["memoryUsageBeforeGc"]:
                            method = each_part["key"]
                            key = metric
                            label = [self.cluster, method, self.target]
                            self.hive_server2_metrics['GarbageCollector'][key].add_metric(label, each_part['value']['used'] if metric in bean else 0)
                print("self.hive_server2_metrics is ", self.hive_server2_metrics)
                print("6" * 20)

    def get_metrics(self, beans):
        for i in range(len(beans)):
            print("beans[i]['name'] is ", beans[i]['name'])
            print("1" * 20)
            print(('GarbageCollector' in beans[i]['name']) and ("Scavenge" not in beans[i]['name']))
            if ('GarbageCollector' in beans[i]['name']) and ("Scavenge" not in beans[i]['name']):  # 提高限制,只要年轻代
                self.get_hs2_gc_metrics(beans[i])