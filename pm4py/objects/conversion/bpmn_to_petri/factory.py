from pm4py.objects.conversion.bpmn_to_petri.versions import classic

CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}


def apply(bpmn_graph, parameters=None, variant="classic"):
    return VERSIONS[CLASSIC](bpmn_graph, parameters=parameters)