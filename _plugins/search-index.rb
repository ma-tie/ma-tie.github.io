# frozen_string_literal: true

require "json"
require "nokogiri"

module SiteSearch
  # Keep the official al_search runtime; adapt its index to this older theme.
  class IndexGenerator < Jekyll::Generator
    safe true
    priority :lowest

    def generate(site)
      return unless site.config["search_enabled"]

      documents = site.pages.select { |page| page.data["nav"] || page.url == "/" }
      documents += site.posts.docs.reverse if site.config["posts_in_search"]
      documents += site.collections.values.reject { |collection| collection.label == "posts" }.flat_map(&:docs)
      entries = documents.select { |doc| searchable?(doc) }.map do |doc|
        post = doc.respond_to?(:collection) && doc.collection.label == "posts"
        {
          id: doc.url,
          title: plain_text(doc.data["title"].to_s).strip.empty? ? "About" : plain_text(doc.data["title"].to_s),
          url: "#{site.config['baseurl'].to_s.sub(%r{/$}, '')}#{doc.url}",
          section: post ? "博客" : "页面",
          text: plain_text([doc.data["description"], doc.data["tags"], doc.data["categories"], doc.content].flatten.compact.join(" "))
        }
      end
      page = Jekyll::PageWithoutAFile.new(site, site.source, "assets", "search-data.json")
      page.data["layout"] = nil
      page.data["sitemap"] = false
      page.data["render_with_liquid"] = false
      page.content = JSON.generate(entries)
      site.pages << page
    end

    private

    def searchable?(doc)
      doc.data["published"] != false && doc.data["search"] != false && doc.data["private"] != true &&
        !doc.path.end_with?("_internal.md") && doc.data["redirect"].nil? &&
        (!doc.respond_to?(:collection) || doc.collection.metadata["output"] != false) &&
        doc.data["inline"] != true && doc.data["autogen"].nil?
    end

    def plain_text(content)
      fragment = Nokogiri::HTML.fragment(content)
      fragment.css("script, style").remove
      fragment.text.gsub(/\s+/, " ").strip
    end
  end
end
