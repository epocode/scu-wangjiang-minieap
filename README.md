# 川大望江：R3S / OpenWrt 使用 MiniEAP 连接电信出口

记录一次四川大学望江校区有线校园网的实际排查：让 NanoPi R3S 在路由器上完成锐捷认证，选择已绑定的电信出口，并由 OpenWrt 管理启动和重新认证。

**2026-10-11 已在一台 R3S 上验证认证成功、电信 IPv4 出口和认证服务重启恢复。整机冷启动、断线恢复与长期稳定性仍待验证。** 这是个人实测记录，适用性取决于校区、接入端口、账号业务和学校认证策略。

## 实测环境与接线

| 项目 | 实测环境 |
| --- | --- |
| 校区与方式 | 四川大学望江校区，有线校园网，锐捷客户端选择电信出口 |
| 路由器 | FriendlyELEC NanoPi R3S LTS，ARM64 / aarch64 |
| 固件 | FriendlyWrt 21.02.7，Linux 6.1.118 |
| 基础程序 | 本机已有 MiniEAP 0.93.7-1，Taiga 构建；具体构建以 SHA256 为准 |
| 上游 WAN | eth0，OpenWrt 网络接口名 wan，DHCP |
| 下游 LAN | 电脑接路由器 LAN；电脑自动获取 IPv4 和 DNS |
| 官方 Windows 客户端 | 6.82；读取到固定版本字段 `06 52 00 00` |

```text
校园网墙口 ── R3S WAN (eth0)
                  │
              R3S LAN ── 电脑
```

账号应已开通并绑定电信业务，并能用官方客户端选择电信出口登录。本文使用与该客户端一致的**学号和学校认证密码**。不在路由器上另拨 PPPoE；也不要直接把电信手机号密码当作本文的学校认证凭据。

## 为什么以前只连得上教育网

| 排查项 | 原配置／现象 | 本次有效修改 |
| --- | --- | --- |
| 账号 | 旧路由器配置是电信手机号 | 改用官方客户端实际使用的学号和学校认证密码 |
| 服务 | `internet` 能连校园网，但不能据此认定走电信出口 | `电信出口`，使用 GBK 原始字节 `b5 e7 d0 c5 b3 f6 bf da` |
| 客户端固定版本 | `01 1f 01 02`，服务端提示“不允许使用的客户端类型！” | 改成抓到的 `06 52 00 00` |
| 版本字符串 | 不能把退出包中的空字段直接搬到认证响应 | 保留 `RG-SU For Linux V1.30` |
| DHCP | 原配置用二次认证但没有对应 DHCP 脚本 | `dhcp-type=2`，认证后调用 OpenWrt WAN renew |
| 运行管理 | 原来没有有效的自动启动服务 | 独立 procd 服务，启用开机启动和进程退出重启 |

**中文服务名的编码和客户端版本是两件不同的事。** 把“电信出口”直接以 UTF-8 写进配置，或者仅调整可读的 `version-str`，都不等同于完成这次适配。

学校客户端在电脑没有有效 IPv4 地址时曾提示“IP地址信息获取错误”，只发送了退出包；本次从退出包读取公开的服务名与固定版本字段，没有把整个退出包作为认证模板。实测保留 Linux 版本字符串、仅修改固定版本常量后认证成功。更完整的记录见 [排查记录](docs/diagnosis.md)。

本次**没有修改 WAN MAC**。学校 MAC 绑定是否能让电信出口免认证尚未验证。本项目实现的是路由器自动认证。

## 仓库内容

- `tools/patch_binary.py`：只对 SHA256 完全相同的原 ARM64 程序打补丁；不匹配就退出。
- `tools/patch_source.py`：修改源码中的对应固定版本常量，供重新编译参考。
- `tools/generate_config.py`：交互填写凭据，生成包含 GBK 服务名的配置；密码输入不回显。
- `openwrt/`：procd 启动脚本、认证后 DHCP 脚本和安装脚本。
- `docs/`：排查、源码编译、社区资料和发布说明。

仓库提供补丁与脚本；不附带原始或修改后的 MiniEAP 可执行程序。实测程序的完整对应源码及构建来源尚未核实，因此没有将第三方二进制当作可发布附件。MiniEAP 上游采用 GPL-3.0，后续分发构建产物时应一并提供对应源码、修改和构建说明，见 [来源说明](NOTICE.md)。

## 复现路径 A：同一构建的 R3S

以下 Python 命令在电脑运行，需要 Python 3；路由器不需要 Python。`ROUTER_IP` 必须替换成自己路由器的 LAN 地址；`eth0` 和 `wan` 也必须先核对。不同架构不能使用此二进制补丁。

### 1. 导出自己的原 MiniEAP 并打补丁

在仓库目录运行：

```sh
mkdir local
scp root@ROUTER_IP:/usr/sbin/minieap local/minieap.original
python tools/patch_binary.py local/minieap.original local/minieap-scu
```

部分旧版 OpenWrt 没有 SFTP 服务，如果 `scp` 提示找不到 `sftp-server`，在支持此参数的新 OpenSSH 上改用 `scp -O`。

脚本仅接受原 SHA256：

```text
a905f0db341e76557ae92f706fcfc5c1fdb1fa3201c971bf1342d9941101eafb
```

期望输出 SHA256：

```text
459fe82e2d2aa2747967bcd13e048faabce327d018817361eb9505501bf1dc16
```

如果不匹配，停止使用路径 A，参考 [源码编译路径 B](docs/build-from-source.md)。相同版本号并不保证二进制完全相同。

### 2. 在电脑生成私人配置

```sh
python tools/generate_config.py --nic eth0 --wan-interface wan
```

按提示输入学号、学校认证密码。输出为 `local/minieap-scu.conf`，服务名以 GBK 字节写入，其余固定字段使用 ASCII。`local/` 已被 Git 忽略。凭据不要写进 issue、截图或 README，也不要使用 `git add -f` 强行提交该目录。

### 3. 上传暂存文件并安装

```sh
ssh root@ROUTER_IP "umask 077; mkdir -p /tmp/scu-minieap-share"
scp local/minieap-scu local/minieap-scu.conf openwrt/minieap-scu.init openwrt/scu-dhcp-renew.sh openwrt/install.sh root@ROUTER_IP:/tmp/scu-minieap-share/
```

先在路由器查看并停止正在使用相同 WAN 网卡的认证客户端，避免并发认证。安装脚本发现 `minieap` 或 `minieap-scu` 进程时会拒绝继续。安装前核对脚本和目标路径：

```sh
ssh root@ROUTER_IP
sh /tmp/scu-minieap-share/install.sh
```

脚本仅安装经过哈希校验的实测二进制，备份已存在的同名文件到私有目录，保留原 `/usr/sbin/minieap` 和 `/etc/minieap.conf`，然后启动并启用新服务。安装成功不代表认证成功，需要继续验证。暂存目录中的凭据在成功安装后会删除。

### 4. 验证认证与出口

在路由器运行：

```sh
logread | grep minieap-scu | tail -40
ubus call service list '{"name":"minieap-scu"}'
ubus call network.interface.wan status
curl --interface eth0 --connect-timeout 5 --max-time 15 -I https://www.baidu.com
curl --interface eth0 --connect-timeout 5 --max-time 15 'https://ipinfo.io/json'
```

`curl` 需要自行安装或换用已有的检测工具。应同时看到认证成功、WAN 有效 IPv4、校外 HTTPS 可达，并用出口查询确认电信 ASN / ISP。本次验证为 Chinanet SC / AS4134 CHINANET BACKBONE。单凭“认证成功”或访问网页成功，不能证明选中了电信出口。

随后测试服务重启：

```sh
/etc/init.d/minieap-scu restart
logread | grep minieap-scu | tail -40
```

冷启动、拔插上游线缆、长时间运行需另外测试并记录；本文不承诺“秒连”。服务内的重新认证和 procd 的进程重启已配置，但链路变化恢复仍需实际验证。

## 日常管理与回滚

```sh
/etc/init.d/minieap-scu restart
/etc/init.d/minieap-scu stop
/etc/init.d/minieap-scu disable
```

要退回原客户端，先 stop、disable 新服务，再使用原 MiniEAP 或官方客户端重新认证。原程序和原配置不被安装脚本覆盖；如需恢复旧版同名 `minieap-scu` 文件，按安装时打印的备份目录手动恢复。备份可能包含凭据，不要上传到 GitHub。

## 常见错误

| 现象 | 优先检查 |
| --- | --- |
| 请选择 internet／用户不允许使用本服务 | GBK 服务名字节、账号电信业务绑定、所在端口是否支持该出口 |
| 不允许使用的客户端类型 | 是否使用已打补丁的程序；固定版本字段是否匹配当前官方客户端 |
| 一直停留在回应用户名 | 网卡、广播模式、是否照抄了退出包中的空版本字符串、并发认证 |
| 认证成功但没有外网 | WAN DHCP 状态、续租脚本、DNS 与默认路由 |
| 手机 USB 能上网，插入路由器后电脑失去外网 | 电脑可能优先使用尚未联网的有线默认路由；调试时有线管理地址可不填网关和 DNS |

## 交流与分享

欢迎反馈固件版本、MiniEAP 构建、校区、脱敏后的错误、服务重启／冷启动／断线恢复／长期运行结果。不同校区的 Web 认证、独立电信 PPPoE 及其他学校的成功案例不能直接算作本方案的验证。

[社区参考](docs/community.md) · [GitHub 发布方法](docs/publishing.md) · [GPL-3.0](LICENSE)

仓库脚本检查范围与尚未验证项目见 [检查记录](docs/repository-validation.md)。
