from pm4py.objects.conversion.bpmn_to_petri.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(bpmn_graph, parameters=None, variant="classic"):
    """
    Apply conversion from a BPMN graph to a Petri net
    along with an initial and final marking

    Parameters
    -----------
    bpmn_graph
        BPMN graph
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use, possible values:
            classic

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    """
    return VERSIONS[variant](bpmn_graph, parameters=parameters)
