#!/bin/bash
set -xe

DEV=${1:-"enp0s20f0u3"}
echo dev=${DEV}

CONN=$(nmcli -t --fields NAME,DEVICE con show | grep $DEV | cut -d ':' -f1)
nmcli connection modify "$CONN" ipv4.method manual ipv4.addr "192.168.7.1/24" 
nmcli dev disconnect $DEV
nmcli dev connect $DEV

sudo iptables -A FORWARD -i ${DEV} -j ACCEPT
sudo iptables -A FORWARD -o ${DEV} -j ACCEPT

sudo iptables -t nat -A POSTROUTING -o wlo1 -j MASQUERADE
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -p

