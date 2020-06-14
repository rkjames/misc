#!/usr/bin/env python

# Prints route commands for current Amazon EC2 US networks.
# Squished into /11 space, so you don't need a bazillion routes. This picks up
# non-EC2 address as a result. Specifically, 54/2048=2.6% of IPv4 address range.

# See: https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html

import requests
import ipaddress

ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']

network = set()

for item in ip_ranges:
    # Only want EC2 in US
    if item["service"] == "EC2" and item["region"][0:2] == "us":
        ip = item["ip_prefix"]
        orig = ipaddress.ip_network(ip, strict = False)
        s = ip.split("/")[0]
        # We'll take the entire supernet/11 of this network
        supernet = ipaddress.ip_network(s + "/11", strict = False)
        if not supernet.supernet_of(orig):
            # sanity check, amazon owns some big masks
            print("error: supernet cannot contain: " + str(orig))
        network.add(supernet)

print(len(network))

for n in network:
    # route ADD 157.0.0.0 MASK 255.0.0.0  157.55.80.1
    print("route add", n.network_address, "mask", n.netmask, "192.168.1.1")

