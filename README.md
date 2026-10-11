# 川大望江：R3S 使用 MiniEAP 连接电信出口

2026-10-11 实测：NanoPi R3S LTS，FriendlyWrt 21.02.7，MiniEAP 0.93.7-1（Taiga 构建）。认证成功，IPv4 出口为电信 AS4134，服务重启后仍能连接。整机冷启动、拔线恢复和长期稳定性未测试。

校园网墙口接 R3S WAN，电脑接 LAN。实测 WAN 网卡为 `eth0`，OpenWrt 接口名为 `wan`。账号使用官方四川大学客户端登录电信出口时的学号和学校认证密码。

## 在 R3S 上改了什么

1. 将认证账号改为学号，保存学校认证密码。
2. 将服务名设为 GBK 编码的“电信出口”：`b5 e7 d0 c5 b3 f6 bf da`。
3. 修改 MiniEAP 固定版本字段：`01 1f 01 02` → `06 52 00 00`，安装为 `/usr/sbin/minieap-scu`。版本字符串保留 `RG-SU For Linux V1.30`。
4. 设置 `dhcp-type=2`，添加认证后 WAN DHCP 续租脚本。
5. 创建独立 procd 服务，配置开机启动、重新认证和进程退出重启。
6. 保留原 MiniEAP 程序和配置；WAN MAC 未修改。

服务名写入命令、二进制修改偏移和安装命令见 [具体修改记录](docs/diagnosis.md)。

## 复现步骤

以下步骤适用于与实测原程序 **SHA256 完全相同的 ARM64 构建**。`ROUTER_IP` 换成自己的路由器地址，先确认网卡名和接口名。

### 1. 在电脑导出并修改程序

需要 Python 3。在仓库目录运行：

```sh
mkdir local
scp root@ROUTER_IP:/usr/sbin/minieap local/minieap.original
python tools/patch_binary.py local/minieap.original local/minieap-scu
```

原 SHA256：

```text
a905f0db341e76557ae92f706fcfc5c1fdb1fa3201c971bf1342d9941101eafb
```

修改后 SHA256：

```text
459fe82e2d2aa2747967bcd13e048faabce327d018817361eb9505501bf1dc16
```

哈希不匹配时脚本会拒绝修改，其他构建参考 [源码修改方法](docs/build-from-source.md)。仓库提供补丁脚本，不附带 MiniEAP 可执行程序。

### 2. 在电脑生成认证配置

```sh
python tools/generate_config.py --nic eth0 --wan-interface wan
```

按提示输入学号和学校认证密码，生成 `local/minieap-scu.conf`，其中服务名已写成 GBK。该目录被 Git 忽略，不要上传私人配置。

### 3. 上传并在 R3S 安装

```sh
ssh root@ROUTER_IP "umask 077; mkdir -p /tmp/scu-minieap-share"
scp local/minieap-scu local/minieap-scu.conf openwrt/minieap-scu.init openwrt/scu-dhcp-renew.sh openwrt/install.sh root@ROUTER_IP:/tmp/scu-minieap-share/
ssh root@ROUTER_IP
```

在路由器先停止正在运行的其他 MiniEAP 认证，再运行：

```sh
sh /tmp/scu-minieap-share/install.sh
```

安装脚本会校验程序哈希、备份已存在的同名文件、设定配置权限为 `600`，然后启用并启动服务。原 `/usr/sbin/minieap` 和 `/etc/minieap.conf` 保留。

若上传提示找不到 `sftp-server`，在支持此参数的 OpenSSH 上将 `scp` 改为 `scp -O`。

### 4. 在 R3S 验证

```sh
logread | grep minieap-scu | tail -40
ubus call network.interface.wan status
curl --interface eth0 --connect-timeout 5 --max-time 15 -I https://www.baidu.com
curl --interface eth0 --connect-timeout 5 --max-time 15 'https://ipinfo.io/json'
```

检查认证成功、WAN 有效 IPv4、校外 HTTPS 可达及电信出口。出口查询和 HTTPS 检查需要 `curl`，也可使用已有检测工具。

## 管理与回滚

```sh
/etc/init.d/minieap-scu restart
/etc/init.d/minieap-scu stop
/etc/init.d/minieap-scu disable
```

回滚时先停止并禁用新服务，再使用保留的原客户端认证。

[脚本检查记录](docs/repository-validation.md) · [来源与许可](NOTICE.md) · [社区参考](docs/community.md)
