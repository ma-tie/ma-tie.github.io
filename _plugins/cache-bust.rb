# based on https://distresssignal.org/busting-css-cache-with-jekyll-md5-hash
# https://gist.github.com/BryanSchuetz/2ee8c115096d7dd98f294362f6a667db
module Jekyll
    module CacheBust
        class CacheDigester
            require 'digest/md5'
            require 'pathname'

            attr_accessor :file_name, :directory

            def initialize(file_name:, directory: nil, source: Dir.pwd)
                self.file_name = file_name
                self.directory = directory
                @source = source
            end

            def digest!
                [file_name, '?', Digest::MD5.hexdigest(file_contents)].join
            end

            private

            def directory_files_content
                target_path = File.join(@source, directory, '**', '*')
                files = Dir[target_path].select { |path| File.file?(path) }.sort
                # Include the Sass entry point and Liquid values used by it.
                entry_point = local_file_name.sub(/\.css\z/, '.scss')
                files += [entry_point, File.join(@source, '_config.yml')]
                files.select { |path| File.file?(path) }.map { |path| File.binread(path) }.join
            end

            def local_file_name
                File.join(@source, file_name.slice((file_name.index('assets/')..-1)))
            end

            def file_content
                File.binread(local_file_name)
            end

            def file_contents
                is_directory? ? file_content : directory_files_content
            end

            def is_directory?
                directory.nil?
            end
        end

        def bust_file_cache(file_name)
            CacheDigester.new(file_name: file_name, source: @context.registers[:site].source).digest!
        end

        def bust_css_cache(file_name)
            CacheDigester.new(file_name: file_name, directory: '_sass', source: @context.registers[:site].source).digest!
        end
    end
end

Liquid::Template.register_filter(Jekyll::CacheBust)
