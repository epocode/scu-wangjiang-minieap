#!/bin/sh
# Renew the existing WAN DHCP client after EAP authentication.
# Default matches the tested installation; config may pass another logical WAN.
wan_interface=${1:-wan}
case "$wan_interface" in
    ''|*[!A-Za-z0-9_.:-]*) exit 1 ;;
esac
ubus call "network.interface.$wan_interface" renew '{}' >/dev/null 2>&1
