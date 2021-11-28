(function(document) {
  fetch("https://api.github.com/repos/{{ site.github.owner_name }}/{{ site.github.repository_name }}/commits?path={{ page.path }}")
    .then((response) => {
      alert(response.json());
      return response.json();
    })
    .then((commits) => {
      var modified = commits[0]['commit']['committer']['date'].slice(0,10);
      alert(modified);
    });
})(document);
