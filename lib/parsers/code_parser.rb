# lib/parsers/code_parser.rb
require 'parser/current'

module Parsers
  class CodeParser
    def initialize(file_path)
      @file_path = file_path
    end

    def parse
      buffer = Parser::Source::Buffer.new(@file_path)
      buffer.source = File.read(@file_path)

      # Create a new parser instance
      parser = Parser::CurrentRuby.new

      # Parse the source code into an AST
      ast = parser.parse(buffer)
      
      ast
    rescue Parser::SyntaxError => e
      puts "Syntax error in file #{@file_path}: #{e.message}"
      nil
    end
  end
end
