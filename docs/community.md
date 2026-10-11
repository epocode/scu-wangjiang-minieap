# 社区资料核查

检索日期：2026-10-11。查看了 GitHub 项目及 issue、恩山公开帖子和川大学生教程。暂未找到明确确认“MiniEAP + 四川大学望江 + 电信出口成功”的独立公开案例；这不表示没有人成功过。

| 原始资料 | 支持什么 | 尚不能证明什么 |
| --- | --- | --- |
| [MiniEAP issue #95](https://github.com/updateing/minieap/issues/95) | 2025 年有人 `internet` 能连教育网，改“电信出口”报服务错误；转为 GBK 后变成“不允许使用的客户端类型”。与本次症状高度一致 | 未明确学校名称；issue 虽已关闭，公开评论未见电信成功反馈 |
| [MiniEAP issue #40](https://github.com/updateing/minieap/issues/40) | 中文服务字段需要 GBK，客户端字段可能需适配；有使用 gzhu 分支成功认证的反馈 | 不是川大电信的直接成功证据 |
| [SCU 网络避坑指北：电信／移动出口](https://github.com/syaoranwe/SCUNET/blob/master/6/移动宽带.md) | 明确讨论望江，用 MentoHUSTTool 抓包生成 telecom.mpf，在路由器输入学号密码选择对应出口 | 使用 MentoHUST，非 MiniEAP；作者说明望江测试资料不足，旧文不保证适用于现在 |
| [2016 年小米路由器加入川大锐捷认证](https://www.xiaoten.com/posts/2016/09/millet-router-automatically-log-sichuan-university-ruijie-client/) | 作者明确表示 MentoHUST 在川大验证成功 | 未说明电信出口；非 MiniEAP |
| [恩山 MiniEAP 多架构讨论](https://www.right.com.cn/forum/thread-4106567-1-1.html) | Taiga／AutoCONFIG 历史构建、ARM64 支持、已知兼容问题 | 首帖面向厦门理工，不能作为川大成功案例 |

上游代码与文档：

- [MiniEAP 项目](https://github.com/updateing/minieap)
- [属性定义：服务名为 GBK](https://github.com/updateing/minieap/blob/master/packet_plugin/rjv3/packet_plugin_rjv3_priv.h)
- [私有头部与服务名构造](https://github.com/updateing/minieap/blob/master/packet_plugin/rjv3/packet_plugin_rjv3_priv.c)
- [MiniEAP 使用手册](https://github.com/updateing/minieap/blob/master/minieap.1)

本文仅总结并链接原作者资料；未复制其完整教程。自己的成功证据见 [排查记录](diagnosis.md)，长期运行和冷启动验证仍待补充。
