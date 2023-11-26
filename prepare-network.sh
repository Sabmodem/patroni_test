#!/bin/sh

set -x

# Create the tap devices
sudo ip tuntap add mode tap ktap1
sudo ip tuntap add mode tap ktap2
sudo ip tuntap add mode tap ktap3

# Bring up the tap devices
ip link set ktap1 up
ip link set ktap2 up
ip link set ktap3 up

# Create the bridge to link the tap devices
ip link add name kbr0 type bridge
ip link set dev ktap1 master kbr0
ip link set dev ktap2 master kbr0
ip link set dev ktap3 master kbr0

# Bring up the bridge
ip link set kbr0 up

# Set bridge ip address
# ip address add 192.168.1.254/24 dev kbr0

# Prepare iptables rules
iptables-save > ./rules.backup # backup current rules to restore it on down
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
