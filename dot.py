from string import Template
import subprocess
import os

def render_dot(graph):
    # Define templates as Template objects
    tmpl_graph = Template("""digraph {
        graph [
            rankdir = "LR"
            ranksep = 2.0
        ];
        node [
            fontsize = "16"
            fontname = "Arial"
            shape = "plaintext"
            style = "rounded, filled"
        ];

        $tables
        $edges
        $clusters
    }""")

    tmpl_table = Template("""$id [id="$table_id", label=<
        <TABLE BORDER="0" CELLBORDER="0">
        <TR><TD WIDTH="230" BORDER="0"><FONT POINT-SIZE="12">$title</FONT></TD></TR>
        $sections
        <TR><TD BORDER="0"></TD></TR>
        </TABLE>
    >];""")

    tmpl_cell = Template("""
        <TR><TD>                    
        <TABLE BORDER="0" CELLSPACING="0" CELLPADDING="4" CELLBORDER="1">
        <TR>
            <TD PORT="$id"
                ID="$table_id:$id"
                HREF="remove_me_url.cell$classes_str">
                $formatted_title
            </TD>
        </TR>
        </TABLE>
        </TD></TR>
    """)

    tmpl_edge = Template("""$from_table_id:$from_node_id -> $to_table_id:$to_node_id [id="$from_table_id:$from_node_id -> $to_table_id:$to_node_id"$attributes]""")

    tmpl_cluster = Template("""subgraph "cluster_$title" {
        label = "$title";

        $nodes

        $sub_clusters
    };""")

    # Render tables
    rendered_tables = []
    for table in graph.tables:
        sections = []
        for node in table.sections:
            sections.append(tmpl_cell.substitute(
                id=node.id,
                table_id=table.table_id,
                formatted_title=formatted_title(node),
                classes_str=".fn"
            ))
        rendered_tables.append(tmpl_table.substitute(
            id=table.table_id,
            table_id=table.table_id,
            title=table.title,
            sections='\n'.join(sections)
        ))

    # Render edges
    rendered_edges = []
    for edge in graph.edges:
        try:
            from_table_id = edge.from_node.table_id
            from_node_id = edge.from_node.node_id
            to_table_id = edge.to_node.table_id
            to_node_id = edge.to_node.node_id

            rendered_edges.append(tmpl_edge.substitute(
                from_table_id=from_table_id,
                from_node_id=from_node_id,
                to_table_id=to_table_id,
                to_node_id=to_node_id,
                attributes=attributes(edge)
            ))
        except AttributeError as e:
            print(f"Error accessing edge attributes: {e}")

    # Render clusters
    rendered_clusters = []
    for cluster in graph.clusters:
        nodes = [f"{node_id}" for node_id in cluster.nodes]
        sub_clusters = []
        for sub_cluster in cluster.sub_clusters:
            sub_clusters.append(tmpl_cluster.substitute(
                title=sub_cluster.title,
                nodes="\n".join([f"{node_id}" for node_id in sub_cluster.nodes]),
                sub_clusters=""
            ))
        rendered_clusters.append(tmpl_cluster.substitute(
            title=cluster.title,
            nodes="\n".join(nodes),
            sub_clusters='\n'.join(sub_clusters)
        ))

    # Combine all parts
    dot_code = tmpl_graph.substitute(
        tables='\n'.join(rendered_tables),
        edges='\n'.join(rendered_edges),
        clusters='\n'.join(rendered_clusters)
    )

    return dot_code


def formatted_title(node):
    title = node.title
    if "]" not in title:
        return title

    start = title.find('[')
    args = title[start:].split()
    return f"{title[:start]}<BR/>{'<BR/>'.join(args)}"


def attributes(edge):
    if edge.from_node.table_id == edge.to_node.table_id:
        return 'style="dashed" class="modify-me"'
    else:
        return 'style="solid" class="modify-me"'


def export_svg(dot_code):
    try:
        process = subprocess.Popen(
            ['dot', '-Tsvg'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        svg_output, error = process.communicate(input=dot_code.encode('utf-8'))

        if process.returncode != 0:
            raise Exception(f"Graphviz error: {error.decode('utf-8')}")

        svg_content = svg_output.decode('utf-8')
        return svg_content

    except Exception as e:
        return f"Error generating SVG: {str(e)}"
