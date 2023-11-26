#!/bin/sh

set -x

# Bring down the bridge
# ip link set kbr0 down

# Delete the bridge
ip link delete kbr0 type bridge

# Delete the tap devices
ip link delete ktap1
ip link delete ktap2
ip link delete ktap3

# Restore the iptables rules
iptables-restore < ./rules.backup
rm ./rules.backup
