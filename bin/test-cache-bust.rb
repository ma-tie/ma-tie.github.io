# frozen_string_literal: true

require 'tmpdir'
require 'fileutils'
require 'liquid'
require_relative '../_plugins/cache-bust'

Dir.mktmpdir('css-cache-test') do |source|
  FileUtils.mkdir_p(File.join(source, '_sass'))
  FileUtils.mkdir_p(File.join(source, 'assets/css'))
  partial = File.join(source, '_sass/_search.scss')
  entry = File.join(source, 'assets/css/main.scss')
  config = File.join(source, '_config.yml')
  File.write(partial, 'ninja-keys { color: black; }')
  File.write(entry, '@import "search";')
  File.write(config, 'max_width: 800px')

  site = Struct.new(:source).new(source)
  template = Liquid::Template.parse('{{ "/preview/assets/css/main.css" | bust_css_cache }}')
  digest = -> { template.render!({}, registers: { site: site }) }
  before = digest.call
  raise 'CSS hash is empty' if before.end_with?('d41d8cd98f00b204e9800998ecf8427e')
  raise 'CSS hash is unstable' unless before == digest.call

  [partial, entry, config].each do |path|
    File.open(path, 'a') { |file| file.write("\n/* changed */") }
    after = digest.call
    raise "CSS cache was not invalidated for #{File.basename(path)}" if before == after
    before = after
  end

  # The hash must depend on the site source, regardless of the process cwd.
  Dir.chdir(File.dirname(source)) do
    raise 'CSS hash depends on cwd' unless digest.call == before
  end
end

puts 'CSS cache invalidation checks passed.'
