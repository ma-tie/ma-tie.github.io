// The modal, fuzzy matching and keyboard navigation are shipped by al_search.
import "../al_search/js/search/ninja-keys.min.js";
import "../al_search/js/search-setup.js";

const search = document.querySelector("ninja-keys");
const status = document.getElementById("search-status");
const shortcut = document.querySelector(".search-shortcut");
if (shortcut) shortcut.textContent = /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘ K" : "Ctrl K";

const syncTheme = () => search.classList.toggle("dark", document.documentElement.dataset.theme === "dark");
syncTheme();
new MutationObserver(syncTheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

// ninja-keys accepts HTML titles; encode site titles before handing them to it.
const escapeTitle = (text) => text.replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);

try {
  const response = await fetch(search.dataset.indexUrl);
  if (!response.ok) throw new Error(`Search index: HTTP ${response.status}`);
  const entries = await response.json();
  search.data = entries.map((entry) => ({
    id: entry.id,
    title: escapeTitle(entry.title),
    description: entry.text,
    section: entry.section,
    handler: () => { window.location.href = entry.url; },
  }));
  status.textContent = `${entries.length} 篇内容可搜索`;
  search.addEventListener("change", (event) => {
    if (!event.detail.actions) return;
    status.textContent = event.detail.search ? `${event.detail.actions.length} 条结果` : `${entries.length} 篇内容可搜索`;
  });
} catch (error) {
  status.textContent = "搜索索引加载失败，请刷新页面重试";
  console.error(error);
}
