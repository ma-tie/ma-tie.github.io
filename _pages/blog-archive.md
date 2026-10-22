---
layout: blog
title: 博客归档
description: 按年份、分类或标签浏览全部文章。
permalink: /blog/archive/
nav: false
---

<header class="blog-heading"><div><p class="blog-eyebrow">ARCHIVES</p><h1>全部归档</h1></div><span class="blog-total">{{ site.posts | size }} 篇文章</span></header>
<div class="blog-archive-card">
<p><a href="{{ '/blog/' | relative_url }}">← 返回博客</a> &nbsp; · &nbsp; 共 {{ site.posts | size }} 篇文章</p>

<h2 id="years">年份</h2>
{% assign years = site.posts | group_by_exp: 'post', "post.date | date: '%Y'" %}
<ul>
  {% for year in years %}
    <li><a href="{{ year.name | prepend: '/blog/' | append: '/' | relative_url }}">{{ year.name }}</a>（{{ year.items | size }}）</li>
  {% endfor %}
</ul>

<h2 id="categories">分类</h2>
{% assign categories = site.categories | sort %}
<ul>
  {% for category in categories %}
    <li><a href="{{ category[0] | slugify | prepend: '/blog/category/' | append: '/' | relative_url }}">{{ category[0] }}</a>（{{ category[1] | size }}）</li>
  {% endfor %}
</ul>

<h2 id="tags">标签</h2>
{% assign tags = site.tags | sort %}
<p>
  {% for tag in tags %}
    <a class="badge badge-light mr-2 mb-2" href="{{ tag[0] | slugify | prepend: '/blog/tag/' | append: '/' | relative_url }}">#{{ tag[0] }}（{{ tag[1] | size }}）</a>
  {% endfor %}
</p>

</div>
