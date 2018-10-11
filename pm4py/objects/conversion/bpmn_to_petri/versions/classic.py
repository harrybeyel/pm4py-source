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
    start_involved_places = set()
    start_involved_arcs = set()
    start_involved_trans = set()

    for place in initial_marking:
        start_involved_places.add(place)
        for arc in place.out_arcs:
            start_involved_arcs.add(arc)
            trans = arc.target
            start_involved_trans.add(trans)
            if trans.label is not None:
                if not trans in start_trans:
                    start_trans.append(trans)

    if len(start_trans) == 0:
        for place in initial_marking:
            for arc in place.out_arcs:
                trans = arc.target
                for arc2 in trans.out_arcs:
                    place2 = arc2.target
                    start_involved_places.add(place2)
                    start_involved_arcs.add(arc2)
                    for arc3 in place2.out_arcs:
                        start_involved_arcs.add(arc3)
                        trans2 = arc3.target
                        start_involved_trans.add(trans2)
                        if trans2.label is not None:
                            if not trans2 in start_trans:
                                start_trans.append(trans2)

    return start_trans, start_involved_places, start_involved_arcs, start_involved_trans


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
    final_involved_places = set()
    final_involved_arcs = set()
    final_involved_trans = set()

    for place in final_marking:
        final_involved_places.add(place)
        for arc in place.in_arcs:
            final_involved_arcs.add(arc)
            trans = arc.source
            final_involved_trans.add(trans)
            if trans.label is not None:
                if not trans in final_trans:
                    final_trans.append(trans)

    if len(final_trans) == 0 or True:
        for place in final_marking:
            for arc in place.in_arcs:
                trans = arc.source
                for arc2 in trans.in_arcs:
                    final_involved_arcs.add(arc2)
                    place2 = arc2.source
                    final_involved_places.add(place2)
                    for arc3 in place2.in_arcs:
                        final_involved_arcs.add(arc3)
                        trans2 = arc3.source
                        final_involved_trans.add(trans2)
                        if trans2.label is not None:
                            if not trans in final_trans:
                                final_trans.append(trans2)

    return final_trans, final_involved_places, final_involved_arcs, final_involved_trans


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
    elements_correspondence = {}
    bpmn_graph.create_new_diagram_graph(diagram_name="diagram")
    process_id = bpmn_graph.add_process_to_diagram("1")
    [start_id, _] = bpmn_graph.add_start_event_to_diagram(process_id, start_event_name="start",
                                                          node_id=constants.START_EVENT_ID)
    [end_id, _] = bpmn_graph.add_end_event_to_diagram(process_id, end_event_name="end", node_id=constants.END_EVENT_ID)
    start_trans, start_involved_places, start_involved_arcs, start_involved_trans = get_start_trans_petri_given_imarking(
        initial_marking)
    final_trans, final_involved_places, final_involved_arcs, final_involved_trans = get_final_trans_petri_given_fmarking(
        final_marking)

    for trans in net.transitions:
        if trans.label is not None:
            if trans in start_trans and len(start_trans) == 1:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=constants.STARTACT_PREFIX + str(uuid.uuid4()))
            elif trans in final_trans and len(final_trans) == 1:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=constants.ENDACT_PREFIX + str(uuid.uuid4()))
            else:
                [task_id, task] = bpmn_graph.add_task_to_diagram(process_id, task_name=trans.label,
                                                                 node_id=constants.INTERNAL_ACT_PREFIX + str(
                                                                     uuid.uuid4()))
            bpmn_transitions_map[trans] = task_id
            elements_correspondence[trans] = task

    mapped_trans = {}
    mapped_arcs = {}
    mapped_places = {}

    for place in initial_marking:
        mapped_places[place] = start_id
    for place in final_marking:
        mapped_places[place] = end_id

    for place in net.places:
        if len(place.in_arcs) == 1 and len(place.out_arcs) == 1:
            for arc in place.in_arcs:
                in_arc = arc
                in_trans = arc.source
            for arc in place.out_arcs:
                out_arc = arc
                out_trans = arc.target

            if len(in_trans.out_arcs) == 1:
                # sequential place between two activities, convert it into direct arc :)
                flow = None
                if in_trans.label is not None and out_trans.label is not None:
                    sequence_flow_id, flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                     bpmn_transitions_map[in_trans],
                                                                                     bpmn_transitions_map[out_trans])
                    if not in_trans in mapped_trans:
                        mapped_trans[in_trans] = bpmn_transitions_map[in_trans]
                    if not out_trans in mapped_trans:
                        mapped_trans[out_trans] = bpmn_transitions_map[out_trans]

                if flow is not None:
                    mapped_places[place] = flow
                    mapped_arcs[in_arc] = flow
                    mapped_arcs[out_arc] = flow

                    elements_correspondence[out_arc] = flow

    # add remaining elements of the Petri net as happen in a Petri net
    for trans in net.transitions:
        if len(trans.in_arcs) == 1 and len(trans.out_arcs) == 1 and trans.label is None and not \
        [arc.source for arc in trans.in_arcs][0] in initial_marking and not [arc.target for arc in trans.out_arcs][
                                                                                0] in final_marking:
            pass

        else:
            if not trans in mapped_trans:
                if trans.label is None:
                    gateway_name = trans.name
                    gateway_id_principal = trans.name
                    [gateway_principal, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                         gateway_name=gateway_name,
                                                                                         node_id=gateway_id_principal)
                    mapped_trans[trans] = gateway_principal
                else:
                    mapped_trans[trans] = bpmn_transitions_map[trans]

            if trans in mapped_trans:
                for arc in trans.in_arcs:
                    if not arc in mapped_arcs:
                        place = arc.source
                        if not place in mapped_places:
                            gateway_name_inplace = place.name
                            gateway_id_inplace = place.name
                            [gateway_inplace, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                               gateway_name=gateway_name_inplace,
                                                                                               node_id=gateway_id_inplace)
                            mapped_places[place] = gateway_inplace

                        sequence_flow_id, inplace_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                 mapped_places[place],
                                                                                                 mapped_trans[trans])
                        mapped_arcs[arc] = inplace_flow
                        elements_correspondence[arc] = inplace_flow

                for arc in trans.out_arcs:
                    if not arc in mapped_arcs:
                        place = arc.target
                        if not place in mapped_places:
                            gateway_name_outplace = place.name
                            gateway_id_outplace = place.name
                            [gateway_outplace, _] = bpmn_graph.add_exclusive_gateway_to_diagram(process_id,
                                                                                                gateway_name=gateway_name_outplace,
                                                                                                node_id=gateway_id_outplace)
                            mapped_places[place] = gateway_outplace

                        sequence_flow_id, outplace_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                                  mapped_trans[trans],
                                                                                                  mapped_places[place])
                        mapped_arcs[arc] = outplace_flow
                        elements_correspondence[arc] = outplace_flow

    for trans in net.transitions:
        if len(trans.in_arcs) == 1 and len(trans.out_arcs) == 1 and trans.label is None and not \
        [arc.source for arc in trans.in_arcs][0] in initial_marking and not [arc.target for arc in trans.out_arcs][
                                                                                0] in final_marking:
            arc_source = [arc for arc in trans.in_arcs][0]
            arc_target = [arc for arc in trans.out_arcs][0]
            place_source = arc_source.source
            place_target = arc_target.target

            if place_source in mapped_places and place_target in mapped_places:
                sequence_flow_id, place_flow = bpmn_graph.add_sequence_flow_to_diagram(process_id,
                                                                                         mapped_places[place_source],
                                                                                         mapped_places[place_target])

    return bpmn_graph, elements_correspondence
