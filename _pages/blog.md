---
layout: blog
permalink: /blog/
title: Blog
nav: true
nav_order: 3
pagination:
  enabled: true
  collection: posts
  permalink: /page/:num/
  per_page: 100
  sort_field: date
  sort_reverse: true
  trail:
    before: 1
    after: 3
---

<header class="blog-heading">
  <div><p class="blog-eyebrow">NOTES & IDEAS</p><h1>{{ site.blog_name }}</h1><p>{{ site.blog_description }}</p></div>
</header>
<a class="blog-mobile-navigation" href="#blog-navigation">浏览分类与全部标签 ↓</a>
{% include blog_list_toggle.liquid %}
{% if paginator.page == 1 %}
  {% assign featured_posts = site.posts | where: 'featured', true %}
  {% if featured_posts.size > 0 %}
    <section aria-label="精选文章" class="blog-featured">
      {% for post in featured_posts %}{% include blog_card.liquid %}{% endfor %}
    </section>
  {% endif %}
{% endif %}
<div class="blog-card-list">
  {% for post in paginator.posts %}{% include blog_card.liquid %}{% endfor %}
</div>
{% include pagination.liquid %}
