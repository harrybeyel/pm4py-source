import bpmn_python.bpmn_diagram_rep as diagram
import uuid
from pm4py.objects.conversion.bpmn_to_petri.util import constants

def get_start_trans_petri_given_imarking(initial_marking):
    """
    Deduce the start activities given the initial marking of the Petri net

    Parameters
    ----------
    initial_marking
        Initial marking of the Petri net

    Returns
    ----------
    start_trans
        List of start transitions deduced from the Petri net
    """
    start_trans = []

    for place in initial_marking:
        for arc in place.out_arcs:
            trans = arc.target
            if trans.label is not None:
                if not trans in start_trans:
                    start_trans.append(trans)

    if len(start_trans) == 0:
        for place in initial_marking:
            for arc in place.out_arcs:
                trans = arc.target
                for arc2 in trans.out_arcs:
                    place2 = arc2.target
                    for arc3 in place2.out_arcs:
                        trans2 = arc3.target
                        if trans2.label is not None:
                            if not trans2 in start_trans:
                                start_trans.append(trans2)

    return start_trans

def get_final_trans_petri_given_fmarking(final_marking):
    """
    Deduce the end activities given the final marking of the Petri net

    Parameters
    -----------
    final_marking
        Final marking of the Petri net

    Returns
    -----------
    final_trans
        List of final transitions deduced from the Petri net
    """
    final_trans = []

    for place in final_marking:
        for arc in place.in_arcs:
            trans = arc.source
            if trans.label is not None:
                if not trans in final_trans:
                    final_trans.append(trans)

    if len(final_trans) == 0 or True:
        for place in final_marking:
            for arc in place.in_arcs:
                trans = arc.source
                for arc2 in trans.in_arcs:
                    place2 = arc2.source
                    for arc3 in place2.in_arcs:
                        trans2 = arc3.source
                        if trans2.label is not None:
                            if not trans in final_trans:
                                final_trans.append(trans2)

    return final_trans

def apply(net, initial_marking, final_marking, parameters=None):
    """
    Convert the Petri net to a BPMN graph

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
    if parameters is None:
        parameters = {}
    bpmn_transitions_map = {}
    bpmn_graph = diagram.BpmnDiagramGraph()
    edges_correspondence = {}
    bpmn_graph.create_new_diagram_graph(diagram_name="diagram")
    process_id = bpmn_graph.add_process_to_diagram("1")
    [start_id, _] = bpmn_graph.add_start_event_to_diagram(process_id, start_event_name="start", node_id=constants.START_EVENT_ID)
    [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end", node_id=constants.END_EVENT_ID)
    start_trans = get_start_trans_petri_given_imarking(initial_marking)
    final_trans = get_final_trans_petri_given_fmarking(final_marking)

    for trans in net.transitions:
        if trans.label is not None:
            if trans in start_trans and len(start_trans) == 1:
                [task_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                              node_id=constants.STARTACT_PREFIX + str(uuid.uuid4()))
            elif trans in final_trans and len(final_trans) == 1:
                [task_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                              node_id=constants.ENDACT_PREFIX + str(uuid.uuid4()))
            else:
                [task_id, _] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                              node_id=constants.INTERNAL_ACT_PREFIX + str(uuid.uuid4()))
            bpmn_transitions_map[trans] = task_id

    # add arcs from the start event to the start activities according to the Petri net
    if len(start_trans) == 1:
        bpmn_graph.add_sequence_flow_to_diagram(process_id, start_id, bpmn_transitions_map[start_trans[0]])
    elif len(start_trans) > 1:
        gateway_id = constants.STARTGATEWAY_PREFIX+str(uuid.uuid4())
        [gateway_entry, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id, gateway_name=gateway_id, node_id=gateway_id)
        bpmn_graph.add_sequence_flow_to_diagram(process_id, start_id, gateway_entry)
        for trans in start_trans:
            bpmn_graph.add_sequence_flow_to_diagram(process_id, gateway_entry, bpmn_transitions_map[trans])
    # add arcs from the end event to the end activities according to the Petri net
    if len(final_trans) == 1:
        bpmn_graph.add_sequence_flow_to_diagram(process_id, bpmn_transitions_map[final_trans[0]], end_id)
    elif len(final_trans) > 1:
        gateway_id = constants.ENDGATEWAY_PREFIX+str(uuid.uuid4())
        [gateway_exit, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id, gateway_name=gateway_id, node_id=gateway_id)
        bpmn_graph.add_sequence_flow_to_diagram(process_id, gateway_exit, end_id)
        for trans in final_trans:
            bpmn_graph.add_sequence_flow_to_diagram(process_id, bpmn_transitions_map[trans], gateway_exit)

    mapped_trans = {}
    mapped_arcs = {}
    mapped_places = {}

    for place in net.places:
        if len(place.in_arcs) == 1 and len(place.out_arcs) == 1:
            for arc in place.in_arcs:
                in_arc = arc
                in_trans = arc.source
            for arc in place.out_arcs:
                out_arc = arc
                out_trans = arc.target

            flow = None
            if in_trans.label is not None and out_trans.label is not None:
                sequence_flow_id, flow = bpmn_graph.add_sequence_flow_to_diagram(process_id, bpmn_transitions_map[in_trans], bpmn_transitions_map[out_trans])
            """elif in_trans.label is None and out_trans.label is not None:
                if not in_trans in mapped_trans:
                    gateway_id = constants.OTHERGATEWAY_PREFIX + str(uuid.uuid4())
                    [gateway, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                     gateway_name=gateway_id,
                                                                                     node_id=gateway_id)
                    mapped_trans[in_trans] = gateway
                else:
                    gateway = mapped_trans[in_trans]
                sequence_flow_id, flow = bpmn_graph.add_sequence_flow_to_diagram(process_id, gateway, bpmn_transitions_map[out_trans])
            elif in_trans.label is not None and out_trans.label is None:
                if not in_trans in mapped_trans:
                    gateway_id = constants.OTHERGATEWAY_PREFIX + str(uuid.uuid4())
                    [gateway, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                     gateway_name=gateway_id,
                                                                                     node_id=gateway_id)
                    mapped_trans[out_trans] = gateway
                else:
                    gateway = mapped_trans[out_trans]
                sequence_flow_id, flow = bpmn_graph.add_sequence_flow_to_diagram(process_id, bpmn_transitions_map[in_trans], gateway)"""
            if not in_trans in mapped_trans:
                mapped_trans[in_trans] = bpmn_transitions_map[in_trans]
            if not out_trans in mapped_trans:
                mapped_trans[out_trans] = bpmn_transitions_map[out_trans]

            if flow is not None:
                mapped_places[place] = flow
                mapped_arcs[in_arc] = flow
                mapped_arcs[out_arc] = flow


    return bpmn_graph, edges_correspondence