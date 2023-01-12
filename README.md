# hive_exporter
Base on github open source exporters, I develop hive exporter, which has not been created by others yet. It's simple, but useful for me. Hope it can help others.
I will upload developed code soon.

Thanks to https://github.com/opsnull/hadoop_jmx_exporter.


➜  hive_exporter git:(master) ✗ python2 hive_exporter.py -h
usage: hive_exporter.py [-h] -cluster cluster_name
                              [-his [hive_jmx_url [hive_jmx_url ...]]]
                              [-host host] [-port port]

hive jmx metric prometheus exporter

optional arguments:
  -h, --help            show this help message and exit
  -cluster cluster_name
                        Hadoop cluster name (maybe HA name)
  -queue yarn_queue_regexp
                        Regular expression of queue name. default: root.*
  -his [hive_jmx_url [hive_jmx_url ...]]
                        Hive jmx metrics URL.
  -host host            Listen on this address. default: 0.0.0.0
  -port port            Listen to this port. default: 6688
➜  hadoop_exporter git:(master) ✗

➜  hadoop_exporter git:(master) ✗ python2 hadoop_jmx_exporter.py -cluster test -his http://192.168.10.102:10002/jmx
Listen at 0.0.0.0:6688