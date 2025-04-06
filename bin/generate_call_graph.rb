# bin/generate_call_graph.rb
require 'find'
require_relative '../lib/parsers/code_parser'
require_relative '../lib/graph/graph_builder'

# Specify the directory containing the Ruby files
directory_path = 'rb-code' # Replace with your target directory

# Initialize the graph builder
graph_builder = Graph::GraphBuilder.new

# Traverse and parse all Ruby files in the directory
Find.find(directory_path) do |file_path|
  next unless file_path.end_with?('.rb')
  
  puts "Parsing #{file_path}"
  parser = Parsers::CodeParser.new(file_path)
  ast = parser.parse
  file_name = File.basename(file_path)
  if ast
    graph_builder.build_from_ast(ast,file_path)
  else
    puts "Skipping #{file_path} due to errors"
  end
end

# Output the graph to a JSON file
output_path = 'data/call_graph.json'
graph_builder.output_to_file(output_path)

puts "Call graph data generated and saved to #{output_path}"
