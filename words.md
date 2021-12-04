---
layout: page
title: Words
---

<div class="posts">
  {% for word in site.words %}
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

