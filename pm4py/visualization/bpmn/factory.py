from pm4py.visualization.bpmn.versions import wo_decoration
from pm4py.visualization.bpmn.util.save_view import *

WO_DECORATION = "wo_decoration"
FREQUENCY_DECORATION = "frequency"
PERFORMANCE_DECORATION = "performance"
FREQUENCY_GREEDY = "frequency_greedy"
PERFORMANCE_GREEDY = "performance_greedy"

VERSIONS = {WO_DECORATION: wo_decoration.apply, FREQUENCY_DECORATION: wo_decoration.apply,
            PERFORMANCE_DECORATION: wo_decoration.apply, FREQUENCY_GREEDY: wo_decoration.apply,
            PERFORMANCE_GREEDY: wo_decoration.apply}


def apply(bpmn_graph, parameters=None, variant="wo_decoration"):
    """
    Factory method to visualize a BPMN graph using the given parameters

    Parameters
    -----------
    bpmn_graph
        BPMN graph object
    parameters
        Possible parameters, of the algorithm, including:
            format -> Format of the image to render (pdf, png, svg)

    Returns
    ----------
    file_name
        Path of the figure in which the rendered BPMN has been saved
    """
    return VERSIONS[variant](bpmn_graph, parameters=parameters)
