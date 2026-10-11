# 来源与修改说明

本项目是一次个人适配经验及配套脚本，不是四川大学或锐捷的官方产品，也不代表 MiniEAP 上游。

MiniEAP：https://github.com/updateing/minieap ，采用 GNU GPL v3。其 rjv3 算法源自 Hu Yunrui 的 MentoHUST 项目；MiniEAP 源码和贡献者署名应保留。Taiga / AutoCONFIG 历史构建信息见 `docs/community.md`。

2026-10-11 的本次适配，将 `rjv3_append_priv_header` 中固定版本数组从 `01 1f 01 02` 改为 `06 52 00 00`。本仓库提供源码修改工具和严格限制原始哈希的二进制修改工具、配置生成程序、独立 OpenWrt 管理脚本以及自行撰写的实测文档，按仓库中的 GPL-3.0 许可证分享。

仓库不包含第三方 MiniEAP 二进制，也未声称已取得实测 Taiga 构建的完整对应源码。用户在自己的设备上复制原程序并应用补丁用于本地复现；如再分发可执行程序，应同时提供该构建的完整对应源码、修改和构建资料。Windows 官方客户端、原始抓包、个人认证配置不在分享范围内。
