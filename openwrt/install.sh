#!/bin/sh
# GPL-3.0. Install only the hash-verified 2026-10-11 ARM64 build.
set -eu
umask 077

stage=/tmp/scu-minieap-share
expected=459fe82e2d2aa2747967bcd13e048faabce327d018817361eb9505501bf1dc16
fail() { printf '%s\n' "$*" >&2; exit 1; }

[ "$(id -u)" = 0 ] || fail 'Run as root on the router.'
[ "$(uname -m)" = aarch64 ] || fail 'This installer accepts only the tested ARM64 build.'
[ -r /etc/openwrt_release ] || fail 'OpenWrt release information not found.'
for tool in sha256sum ubus pidof; do
    command -v "$tool" >/dev/null 2>&1 || fail "Missing command: $tool"
done
for file in minieap-scu minieap-scu.conf minieap-scu.init scu-dhcp-renew.sh; do
    [ -f "$stage/$file" ] || fail "Missing staged file: $file"
done
actual=$(sha256sum "$stage/minieap-scu" | awk '{print $1}')
[ "$actual" = "$expected" ] || fail 'Binary SHA256 differs. Refusing installation.'
grep -q '^username=.' "$stage/minieap-scu.conf" || fail 'Missing account.'
grep -q '^password=.' "$stage/minieap-scu.conf" || fail 'Missing password.'
sh -n "$stage/minieap-scu.init"
sh -n "$stage/scu-dhcp-renew.sh"
if pidof minieap minieap-scu >/dev/null 2>&1; then
    fail 'Stop existing MiniEAP authentication first to avoid duplicate sessions.'
fi

backup=/root/minieap-scu-backups/$(date +%Y%m%d-%H%M%S)-$$
mkdir -p "$backup"
chmod 700 /root/minieap-scu-backups "$backup"
for target in /usr/sbin/minieap-scu /etc/minieap-scu.conf /etc/init.d/minieap-scu /usr/libexec/scu-dhcp-renew.sh; do
    if [ -e "$target" ]; then
        mkdir -p "$backup$(dirname "$target")"
        cp -p "$target" "$backup$target"
    fi
done
mkdir -p /usr/sbin /usr/libexec /etc/init.d
cp "$stage/minieap-scu" /usr/sbin/minieap-scu
cp "$stage/minieap-scu.conf" /etc/minieap-scu.conf
cp "$stage/minieap-scu.init" /etc/init.d/minieap-scu
cp "$stage/scu-dhcp-renew.sh" /usr/libexec/scu-dhcp-renew.sh
chmod 755 /usr/sbin/minieap-scu /etc/init.d/minieap-scu /usr/libexec/scu-dhcp-renew.sh
chmod 600 /etc/minieap-scu.conf
/etc/init.d/minieap-scu enable
/etc/init.d/minieap-scu start
rm -f "$stage/minieap-scu.conf"
printf 'Installed. Previous files, if any: %s\n' "$backup"
printf '%s\n' 'Check logread for authentication and independently verify the Telecom IPv4 exit.'
