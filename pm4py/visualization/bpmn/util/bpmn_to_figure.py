import matplotlib.pyplot as plt
import networkx as nx
import pydotplus
import bpmn_python.bpmn_python_consts as consts
import tempfile
from pm4py.objects.conversion.bpmn_to_petri.util import constants

EXCLUSIVE_OPERATOR = ""
PARALLEL_OPERATOR = "+"

def bpmn_diagram_to_figure(bpmn_graph, format):
    """
    Render a BPMN graph into a figure of the given format

    Parameters
    ----------
    bpmn_graph
        BPMN graph to render
    format
        Render format

    Returns
    ----------
    file_name
        Path of the file containing the render
    """
    g = bpmn_graph.diagram_graph
    graph = pydotplus.Dot()
    for node in g.nodes(data=True):
        if node[1].get(consts.Consts.type) == consts.Consts.task:
            n = pydotplus.Node(name=node[0], shape="box", style="rounded", label=node[1].get(consts.Consts.node_name))
        elif node[1].get(consts.Consts.type) == consts.Consts.exclusive_gateway:
            n = pydotplus.Node(name=node[0], shape="diamond", label=EXCLUSIVE_OPERATOR)
        elif node[1].get(consts.Consts.type) == consts.Consts.parallel_gateway:
            n = pydotplus.Node(name=node[0], shape="diamond", label=PARALLEL_OPERATOR)
        else:
            n = pydotplus.Node(name=node[0], label=node[1].get(consts.Consts.node_name))
        graph.add_node(n)
    for edge in g.edges(data=True):
        if edge[0] == constants.END_EVENT_ID:
            e = pydotplus.Edge(src=edge[1], dst=edge[0], label=edge[2].get(consts.Consts.name))
        else:
            e = pydotplus.Edge(src=edge[0], dst=edge[1], label=edge[2].get(consts.Consts.name))
        graph.add_edge(e)
    file_name = tempfile.NamedTemporaryFile(suffix='.'+format)
    file_name.close()
    graph.write(file_name.name, format=format)
    return file_name