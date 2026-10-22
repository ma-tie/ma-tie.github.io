module BlogTagFilters
  # Most-used tags first; ties use a stable alphabetical order.
  def tags_by_frequency(tags)
    tags.sort_by { |name, posts| [-posts.size, name.downcase, name] }
  end
end

Liquid::Template.register_filter(BlogTagFilters)
