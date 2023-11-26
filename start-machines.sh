#!/bin/bash

QEMU="/usr/bin/qemu-system-x86_64"

# Starting node1
# ${QEMU} \
#     -enable-kvm \
#     -m 2048 \
#     -machine q35,accel=kvm \
#     -cpu host,hv_relaxed,hv_vapic,hv_spinlocks=0x1000 \
#     -smp 4,sockets=1,cores=4,threads=1 \
#     -drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE.fd,readonly=on \
#     -drive if=pflash,format=raw,unit=1,file=/usr/share/OVMF/OVMF_VARS.fd \
#     -hda node1.qcow2 \
#     -netdev user,id=net0,hostfwd=tcp::2221-:22,hostfwd=tcp::5000-:5000,hostfwd=tcp::5001-:5001,hostfwd=tcp::54321-:5432 \
#     -device e1000,netdev=net0 \
#     -netdev tap,id=net1,ifname=ktap1,script=no,downscript=no \
#     -device e1000,netdev=net1,mac=de:ad:be:ef:00:02 \
#     -display none &

# Starting node2
${QEMU} \
    -enable-kvm \
    -m 2048 \
    -machine q35,accel=kvm \
    -cpu host,hv_relaxed,hv_vapic,hv_spinlocks=0x1000 \
    -smp 4,sockets=1,cores=4,threads=1 \
    -drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE.fd,readonly=on \
    -drive if=pflash,format=raw,unit=1,file=/usr/share/OVMF/OVMF_VARS.fd \
    -hda node2.qcow2 \
    -netdev user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::54322-:5432  \
    -device e1000,netdev=net0 \
    -netdev tap,id=net2,ifname=ktap2,script=no,downscript=no \
    -device e1000,netdev=net2,mac=de:ad:be:ef:00:04 \
    -display none &

# Starting node3
${QEMU} \
    -enable-kvm \
    -m 2048 \
    -machine q35,accel=kvm \
    -cpu host,hv_relaxed,hv_vapic,hv_spinlocks=0x1000 \
    -smp 4,sockets=1,cores=4,threads=1 \
    -drive if=pflash,format=raw,unit=0,file=/usr/share/OVMF/OVMF_CODE.fd,readonly=on \
    -drive if=pflash,format=raw,unit=1,file=/usr/share/OVMF/OVMF_VARS.fd \
    -hda node3.qcow2 \
    -netdev user,id=net0,hostfwd=tcp::2223-:22,hostfwd=tcp::54323-:5432 \
    -device e1000,netdev=net0 \
    -netdev tap,id=net3,ifname=ktap3,script=no,downscript=no \
    -device e1000,netdev=net3,mac=de:ad:be:ef:00:06 \
    -display none &
