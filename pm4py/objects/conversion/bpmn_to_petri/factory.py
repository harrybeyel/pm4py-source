from pm4py.objects.conversion.bpmn_to_petri.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}

def apply(net, initial_marking, final_marking, parameters=None, variant="classic"):
    """
    Factory method to convert the Petri net to a BPMN graph

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking of the Petri net
    final_marking
        Final marking of the Petri net
    parameters
        Parameters of the algorithm

    Returns
    -----------
    bpmn_graph
        BPMN graph
    edges_correspondence
        Correspondence between meaningful edges of the Petri net and meaningful edges of the BPMN graph
    """
    return VERSIONS[variant](net, initial_marking, final_marking, parameters=parameters)