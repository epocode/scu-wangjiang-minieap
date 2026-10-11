# R3S 具体修改记录

日期：2026-10-11。实测设备：NanoPi R3S LTS / FriendlyWrt 21.02.7 / ARM64。

## 1. 认证配置

创建 `/etc/minieap-scu.conf`，填写学号和学校认证密码，权限设为 `600`。其余主要参数：

```ini
nic=eth0
module=rjv3
if-impl=sockraw
eap-bcast-addr=1
version-str=RG-SU For Linux V1.30
heartbeat=60
dhcp-type=2
dhcp-script=/usr/libexec/scu-dhcp-renew.sh
stage-timeout=5
max-retries=4
max-fail=3
wait-after-fail=30
daemonize=0
pid-file=/var/run/minieap-scu.pid
```

## 2. 服务名改为 GBK 的“电信出口”

在 R3S 写入配置：

```sh
service_name=$(printf '\265\347\320\305\263\366\277\332')
sed -i '/^service=/d' /etc/minieap-scu.conf
printf 'service=%s\n' "$service_name" >> /etc/minieap-scu.conf
```

实际写入字节：`b5 e7 d0 c5 b3 f6 bf da`。

## 3. 修改 MiniEAP 固定版本字段

将 R3S 的 `/usr/sbin/minieap` 下载到电脑，在该 ARM64 程序中修改两条指令：

| 文件偏移 | 原字节 | 修改后 |
| --- | --- | --- |
| `0x31a4` | `20 e0 83 52` | `c0 40 8a 52` |
| `0x31ac` | `20 40 a0 72` | `00 00 a0 72` |

只适用于 [README](../README.md) 中列出的原 SHA256。仓库的 `tools/patch_binary.py` 会校验哈希后修改。

固定版本字段从 `01 1f 01 02` 改成 `06 52 00 00`。源码等效修改位于 `packet_plugin/rjv3/packet_plugin_rjv3_priv.c` 的 `rjv3_append_priv_header`：

```diff
- uint8_t _version[4] = {0x01, 0x1f, 0x01, 0x02};
+ uint8_t _version[4] = {0x06, 0x52, 0x00, 0x00};
```

当时将修改后的程序上传为 `/tmp/minieap-scu-682-test`，在 R3S 安装：

```sh
cp /tmp/minieap-scu-682-test /usr/sbin/minieap-scu
chmod 755 /usr/sbin/minieap-scu
```

原 `/usr/sbin/minieap` 保留。新启动服务使用 `/usr/sbin/minieap-scu`。

## 4. DHCP 与自动启动

创建 `/usr/libexec/scu-dhcp-renew.sh`，调用：

```sh
ubus call network.interface.wan renew '{}'
```

创建 `/etc/init.d/minieap-scu`，由 procd 管理前台进程，配置 `respawn 3600 30 0`，启用开机启动。

## 5. 验证结果

认证成功，WAN 校外 HTTPS 返回 HTTP 200，IPv4 出口为 Chinanet SC / AS4134。重启认证服务后再次验证成功。

WAN MAC 未修改；整台 R3S 未重启。冷启动、拔线恢复和长期稳定性尚未实测。
