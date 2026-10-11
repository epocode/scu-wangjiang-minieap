# 发布到 GitHub

桌面文件夹已经是独立 Git 仓库，默认分支为 `main`，包含初始提交。将它导入 GitHub Desktop 并 Publish repository，或在 GitHub 网站创建空仓库后执行：

```sh
git remote add origin https://github.com/YOUR_USERNAME/scu-wangjiang-minieap.git
git push -u origin main
```

建议网站创建仓库时不要再勾选初始化 README 或许可证，以免与已有初始提交冲突。上述命令中的用户名请换成自己的；本地仓库没有预置远程地址，也没有自动上传。

推荐仓库介绍：四川大学望江有线校园网电信出口的 MiniEAP 实测排查、兼容补丁和 OpenWrt 自动认证脚本。

可用 topics：`openwrt`、`minieap`、`sichuan-university`、`ruijie`、`nanopi-r3s`。

## 提交前检查

```sh
git status --short
git ls-files
```

`local/`、`*.conf`、二进制、IPK、抓包和日志默认忽略；请勿用 `git add -f` 提交自己的私人文件。仓库中只有生成配置的程序，没有账号密码配置模板。不要把路由器 `/etc/minieap-scu.conf`、认证备份目录或原始日志复制进公共仓库。

后续反馈建议使用 issue 模板，只提供脱敏的必要字段。作者身份采用现有 Git 配置；可用 `git log -1 --format=fuller` 自行检查提交署名。
