# Site search

Search uses the official [al_search](https://github.com/al-org-dev/al-search)
plugin, pinned to the published 1.0.3 release in `Gemfile`. Its generator ships the complete local
`ninja-keys` runtime, including modal, fuzzy matching and keyboard navigation.
No CDN or search service is required.

This older Bootstrap-based site uses `_includes/search.liquid` and
`assets/js/site-search.js` to mount that runtime instead of the plugin's
`al_search_assets` tag. The upstream tag embeds title/description-only data
in every page and assumes newer theme functions. The adapter loads one shared
JSON index, includes post text/tags, and follows this site's existing theme.
The plugin's runtime files are not copied or patched in this repository.

`_plugins/search-index.rb` generates `/assets/search-data.json` from navigation
pages, blog posts and output collections. `_internal.md`, `published: false`,
`private: true` and `search: false` documents are excluded. `posts_in_search`
controls blog indexing; `search_enabled` controls the whole feature. Existing
Jekyll rules still determine which future posts and drafts are read.

The navbar button and Ctrl/Cmd+K open search. Arrow keys select a result,
Enter opens it, and Escape closes the modal.

The workflow builds the index automatically with the rest of the site.
`jekyll-minifier.exclude` preserves the plugin's ES module graph.
