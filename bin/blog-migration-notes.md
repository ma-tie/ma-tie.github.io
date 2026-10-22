# 旧博客迁移记录

共迁移 54 篇：49 篇使用原始 Markdown，5 篇由网页恢复。

- 图片放在 `assets/img/blog/mtank/`。
- 保留原文标题、发布日期、分类、标签及其他原始文章字段。
- 适配了本地图片路径、旧站文章链接、Liquid 字面量和数学公式。
- 原文中的代码和文字未做编辑性修改。
- 模板示例移到 `bin/theme-examples/`，新文章模板为 `bin/post-template.md`。
- `bin/` 已在 Jekyll 配置中排除，不会随站点发布。

## 从网页恢复的文章

- python with语句里有raise， exit还会执行吗
- python signal OSError [Errno 22] Invalid argument错误
- 记一次很蠢的云服务器安全组错误
- 使用python的pyroute2在tc clsact在入口（ingress）和出口（egress）处添加bpf程序
- 【CCF-CSP】202203-2. 出行计划

## 验证

Jekyll 构建通过；逐篇验证了 54 个页面、25 处图片引用和 85 个代码块；博客内链与分类/标签归档链接均可解析。
