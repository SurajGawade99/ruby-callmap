from flask import Flask, render_template_string
from graph import gen_graph
from dot import render_dot, export_svg
from jsonpars import pars_Json

app = Flask(__name__)  # Fixed

# HTML template for rendering
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="/static/styles.css">
    <script type="text/javascript" src="/static/path-data-polyfill.min.js"></script>
    <script type="text/javascript" src="/static/svg-pan-zoom.min.js"></script>
</head>
<body>
    {{ svg_content|safe }}
    <script type="text/javascript" src="/static/preprocess.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    json_data = pars_Json()
    graph = gen_graph(json_data)
    dot = render_dot(graph)
    with open("graph.dot", 'w') as file:
        file.write(dot)
    svg = export_svg(dot)
    return render_template_string(HTML_TEMPLATE, svg_content=svg)

if __name__ == '__main__':  # Fixed
    app.run(debug=True)
