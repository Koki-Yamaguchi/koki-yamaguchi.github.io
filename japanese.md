---
layout: page
title: Japanese Words
---

<div class="posts">
  {% assign sorted = site.japanese | sort: 'title' | reverse %}
  {% for word in sorted %}
  <div class="post">
    <h3 class="post-title">
      <a href="{{ word.url | absolute_url }}">
        {{ word.title }}
      </a>
    </h3>

    <span class="post-date">{{ word.date | date_to_string }}</span>

    <!--{{ word.content }}-->
  </div>
  {% endfor %}
</div>

