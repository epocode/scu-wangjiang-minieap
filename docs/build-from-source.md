# 路径 B：从源码修改并重新编译

这一途径适合原二进制 SHA256 不匹配或设备不是 ARM64 的读者。它提供与实测补丁等效的源码修改，但**仓库未完成该途径的交叉编译及上机验证**；不要将新编译结果直接当成实测二进制。

## 获取与修改源码

MiniEAP 上游为 https://github.com/updateing/minieap 。实测路由器原程序带 Taiga 构建标识，社区历史分支为 https://github.com/AutoCONFIG/minieap ，但本次没有确认该二进制的准确源码 commit；分支可用性也应重新检查。

将上游源码克隆到仓库忽略的 `local/` 目录，记录实际 commit：

```sh
git clone https://github.com/updateing/minieap local/upstream
git -C local/upstream rev-parse HEAD
python tools/patch_source.py local/upstream
git -C local/upstream diff
```

脚本只在 `rjv3_append_priv_header` 内发现一个符合预期的固定版本数组时写入修改，不会猜测陌生源码。此修改涉及固定版本字段；`version-str` 是另一项配置。

## 编译与移植

按所用固件、CPU 架构和 C 库选择 OpenWrt SDK／交叉编译工具链，参考上游 `config.mk`、`Makefile` 和 README。Linux 选择 raw socket 后端和 rjv3 模块。在该源码目录执行 `make` 之前，必须正确设置对应目标工具链；在电脑上直接 `make` 不会自动生成 R3S 可执行程序。

本仓库没有锁定 SDK、提供 IPK 配方或 CI 构建，避免把未验证的编译流程说成可直接安装的软件包。

编译成功后，先核对目标架构和动态库依赖，再在有恢复管理通道的路由器上作前台认证测试。重新编译的程序哈希通常与实测不同，`openwrt/install.sh` 会拒绝它。此时需要自行评审安装步骤，再手动部署程序和本仓库的管理脚本，并完成 README 中的认证与出口验证。

## 后续发布构建产物

如果发布 MiniEAP 可执行程序／IPK，请同时保存并提供实际使用的完整对应源码、commit、全部补丁、构建配置、工具链说明和许可证。仅链接一个不确定的上游分支，或仅附带二进制补丁脚本，不能作为已经提供该构建完整对应源码的证明。
