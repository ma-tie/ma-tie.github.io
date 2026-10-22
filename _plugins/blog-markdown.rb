# frozen_string_literal: true

require "jekyll-commonmark"

module Jekyll
  module Converters
    # Selected explicitly for posts; never convert normal pages with this parser.
    class BlogMarkdown < Markdown
      def initialize(config)
        super(config.merge("markdown" => "CommonMark"))
      end

      def matches(_extension)
        false
      end

      def setup
        return if @setup

        super
        # The same Markdown can occur on pages and in posts. Separate caches
        # prevent one parser's HTML being reused by the other.
        @cache = Jekyll::Cache.new("Blog::CommonMark")
      end
    end
  end
end

module BlogMarkdownRendering
  def converters
    regular = super
    return regular unless document.is_a?(Jekyll::Document) && document.collection.label == "posts"

    @blog_converters ||= regular.map do |converter|
      if converter.instance_of?(Jekyll::Converters::Markdown)
        site.find_converter_instance(Jekyll::Converters::BlogMarkdown)
      else
        converter
      end
    end
  end
end

Jekyll::Renderer.prepend(BlogMarkdownRendering)
