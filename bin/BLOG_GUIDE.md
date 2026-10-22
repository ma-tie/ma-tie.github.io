# 当前版本博客使用说明

直接在 `_posts/YYYY-MM-DD-title.md` 写文章，保存后刷新本地预览。博客首页每页显示 5 篇文章，按日期倒序。

## 最小文章格式

```yaml
---
layout: post
title: 文章标题
date: 2026-10-22 12:00:00 +0800
description: 一句话简介，可省略；省略时列表使用正文摘要。
categories: [技术札记]
tags: [python, 网络]
---
```

下方写 Markdown 正文。分类和标签会自动进入归档，不必手动建页面；首页的常用入口可在 `_config.yml` 的 `display_categories` 和 `display_tags` 中调整。

## 文章可选功能（写在顶部 YAML 中）

```yaml
featured: true                    # 在博客顶部显示为精选卡片
thumbnail: /assets/img/example.jpg # 列表缩略图，替换为实际图片路径
related_posts: false              # 仅当想关闭这篇文章的相关推荐时添加
```

目录可二选一：

```yaml
toc:
  beginning: true                 # 正文开头显示目录
```

```yaml
toc:
  sidebar: right                  # 侧边目录，可改为 left
```

数学公式使用 Kramdown 的 `$$公式$$`，代码使用 Markdown 围栏代码块。图片缩放、阅读进度条和代码复制沿用当前主题。

## 站点入口

- 博客列表：`/blog/`
- 完整归档（年份、全部分类和标签及文章数量）：`/blog/archive/`
- RSS：`/feed.xml`
- 首页最近文章：将 `_pages/about.md` 的 `latest_posts` 改为 `true`；条数由 `_config.yml` 的 `latest_posts.limit` 控制。

## 需要自行填写服务信息的功能

- Giscus 评论：填写 `_config.yml` 的 `giscus` 仓库和分类信息后，在文章中设置 `giscus_comments: true`。
- Disqus 评论：填写自己的 `disqus_shortname` 后，在文章中设置 `disqus_comments: true`。已清除主题自带的 al-folio 示例账号。
- 外部博客 RSS 导入：在 `_config.yml` 的 `external_sources` 中填写名称和订阅地址。
- Distill、图表、Mermaid、Jupyter 等特殊文章能力保持当前版本已有实现，按需在文章中配置；恢复普通博客浏览功能不需要开启它们。

本次没有升级主题，也没有添加新版搜索插件。`bin/` 不参与网站发布。

## 分类与标签约定

分类仅使用 `生活随笔` 或 `技术札记`。算法、数据结构、C++、编程语言、计算机网络等主题均放入 `tags`，与原有标签一起保留。
