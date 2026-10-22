// Measure actual wrapped rows so four rows work at every sidebar width.
document.querySelectorAll("[data-collapsible-tags]").forEach((cloud) => {
  const button = document.querySelector(`[aria-controls="${cloud.id}"]`);
  const tags = Array.from(cloud.querySelectorAll("a"));
  let expanded = false;
  let observedWidth = -1;

  function update() {
    tags.forEach((tag) => { tag.hidden = false; });
    const rows = [];
    const overflow = tags.filter((tag) => {
      const top = tag.offsetTop;
      if (!rows.some((row) => Math.abs(row - top) < 2)) rows.push(top);
      return rows.findIndex((row) => Math.abs(row - top) < 2) >= 4;
    });
    if (!expanded) overflow.forEach((tag) => { tag.hidden = true; });
    button.hidden = overflow.length === 0;
    button.setAttribute("aria-expanded", String(expanded));
    button.textContent = expanded ? "收起 ↑" : "展开 ↓";
  }

  button.addEventListener("click", () => {
    expanded = !expanded;
    update();
  });
  // Observe width only: hiding rows changes height and must not create a loop.
  if (typeof ResizeObserver !== "undefined") {
    new ResizeObserver(([entry]) => {
      if (entry.contentRect.width === observedWidth) return;
      observedWidth = entry.contentRect.width;
      update();
    }).observe(cloud);
  } else {
    window.addEventListener("resize", update);
  }
  update();
  if (document.fonts) document.fonts.ready.then(update);
});

document.querySelectorAll("[data-article-list-toggle]").forEach((button) => {
  const list = document.getElementById(button.getAttribute("aria-controls"));
  function update() {
    const expanded = !list.classList.contains("blog-list-collapsed");
    button.setAttribute("aria-expanded", String(expanded));
    button.textContent = expanded ? "折叠全部文章 ↑" : "展开全部文章 ↓";
  }
  button.hidden = false;
  button.addEventListener("click", () => {
    list.classList.toggle("blog-list-collapsed");
    update();
  });
  update();
});
