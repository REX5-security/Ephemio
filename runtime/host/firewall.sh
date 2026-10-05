#!/bin/bash
set -euo pipefail
# Rules apply solely to bridges created by the Ephemio worker.
iptables -N EPHEMIO-POC 2>/dev/null || true
iptables -F EPHEMIO-POC
iptables -A EPHEMIO-POC -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
for target in 0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 192.168.0.0/16 224.0.0.0/4 240.0.0.0/4 137.74.12.96/32; do
    iptables -A EPHEMIO-POC -d "$target" -j REJECT
 done
iptables -A EPHEMIO-POC -j RETURN
iptables -C DOCKER-USER -i eph+ -j EPHEMIO-POC 2>/dev/null || iptables -I DOCKER-USER 1 -i eph+ -j EPHEMIO-POC
iptables -C INPUT -i eph+ -m conntrack --ctstate NEW -j DROP 2>/dev/null || iptables -I INPUT 1 -i eph+ -m conntrack --ctstate NEW -j DROP
