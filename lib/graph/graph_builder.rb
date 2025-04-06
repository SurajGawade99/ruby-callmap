# lib/graph/graph_builder.rb
require 'rgl/adjacency'
require 'json'

module Graph
  class GraphBuilder
    def initialize
      @graph = RGL::DirectedAdjacencyGraph.new
      @nodes = []
      @edges = []
    end

    def add_node(name, file)
      @nodes << { id: name, label: name, file: file } unless @nodes.any? { |node| node[:id] == name }
    end

    def add_edge(from, to, relationship = 'calls')
      unless @edges.any? { |edge| edge[:from] == from && edge[:to] == to }
        @edges << { from: from, to: to, relationship: relationship }
      end
    end

    def build_from_ast(ast, file)
      traverse_ast(ast, nil ,file)
    end

    def output_to_file(output_path)
      graph_data = {
        nodes: @nodes,
        edges: @edges
      }
      
      File.open(output_path, 'w') do |f|
        f.write(JSON.pretty_generate(graph_data))
      end

      puts "Graph data saved to #{output_path}"
    end

    private

def traverse_ast(node, parent = nil, file = nil)
  return unless node.is_a?(Parser::AST::Node)

  case node.type
  when :module, :class
    name = node.children[0].children[1].to_s
    add_node(name, file) unless name.nil? || name.empty?
    traverse_ast(node.children[2], name, file) if node.children[2]
  when :def
    method_name = node.children[0].to_s
    qualified_name = parent ? "#{parent}::#{method_name}" : method_name
    add_node(qualified_name, file) unless qualified_name.nil? || qualified_name.empty?
    # Traverse the method body
    node.children[2..-1].each do |child|
      traverse_ast(child, qualified_name, file)
    end
  when :send
    caller = parent unless parent.nil? || parent.empty?
    method_name = node.children[1].to_s
    if caller && method_name
      add_edge(caller, method_name, 'calls')
    end
    # Traverse the arguments of the method call, if any
    node.children[2..-1].each do |child|
      traverse_ast(child, nil, file) if child.is_a?(Parser::AST::Node)
    end
  end

  # Recursively traverse all children
  node.children.each do |child|
    traverse_ast(child, parent, file) if child.is_a?(Parser::AST::Node)
  end
end 
    
    
  end
end
