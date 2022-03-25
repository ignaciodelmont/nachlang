import graphviz as gv
import uuid

g = gv.Graph(name="Program ast")

def resolve_terminal(terminal):
    return

def gen_node_name():
    return f"n{str(uuid.uuid4())}"

def graph(ast):
    def recur_graph(ast, parent_node_name=None):
        if type(ast) == dict:
            node_key = ast["name"]
            node_name = gen_node_name()

            # Parent node
            g.node(node_name, label=node_key)

            if parent_node_name:
                g.edge(parent_node_name, node_name)

            # Child nodes
            [recur_graph(node, node_name) for node in ast["value"]]
            
        else:
            terminal_name = ast.name
            terminal_value = ast.value

            terminal_name_node = gen_node_name()
            g.node(terminal_name_node, label=terminal_name)
            g.edge(parent_node_name, terminal_name_node)

            terminal_value_node = gen_node_name()
            g.node(terminal_value_node, label=terminal_value)
            g.edge(terminal_name_node, terminal_value_node)

    
    root_name = ast["name"]
    [recur_graph(v, root_name) for v in ast["value"]]
    g.render("output.gv", view=True)


