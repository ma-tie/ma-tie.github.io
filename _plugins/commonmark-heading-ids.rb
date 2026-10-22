# frozen_string_literal: true

require "commonmarker"
require "jekyll-commonmark"
require "nokogiri"
require "set"
require "stringio"

# CommonMark supplies GFM parsing and Rouge highlighting, but no heading IDs.
# Preserve Unicode headings and disambiguate duplicates for article links/TOCs.
module BlogHeadingIds
  private

  def extract_code_lang(info)
    language = super
    return unless language

    language = language.downcase
    { "c++" => "cpp", "c#" => "csharp", "mysql" => "sql" }.fetch(language, language)
  end

  public

  def header(node)
    block do
      original_stream = @stream
      @stream = StringIO.new(String.new(encoding: Encoding::UTF_8))
      out(:children)
      content = @stream.string
      @stream = original_stream

      slug = Nokogiri::HTML.fragment(content).text.downcase
        .gsub(/[^\p{L}\p{M}\p{N}_\-\s]/u, "").gsub(/\s/, "-")
      @heading_ids ||= Set.new
      id = slug
      suffix = 0
      while @heading_ids.include?(id)
        suffix += 1
        id = "#{slug}-#{suffix}"
      end
      @heading_ids.add(id)
      out("<h#{node.header_level} id=\"#{escape_html(id)}\">", content, "</h#{node.header_level}>")
    end
  end
end

Jekyll::Converters::Markdown::CommonMark::HtmlRenderer.prepend(BlogHeadingIds)
