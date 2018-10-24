from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking


def apply(bpmn_graph, parameters=None):
    if parameters is None:
        parameters = {}

    net = PetriNet("converted_net")
    initial_marking = Marking()
    final_marking = Marking()

    nodes = bpmn_graph.get_nodes()

    places_count = 0
    trans_count = 0

    corresponding_in_nodes = {}
    corresponding_out_nodes = {}
    corresponding_arcs = {}

    # adds nodes
    for node in nodes:
        node_id = node[1]['id']
        node_name = node[1]['node_name'].replace("\r", " ").replace("\n", " ").strip() if 'node_name' in node[
            1] else None
        node_type = node[1]['type'].lower()
        node_process = node[1]['process'].lower()

        if "task" in node_type:
            trans_count = trans_count + 1
            trans = PetriNet.Transition('trans_' + str(trans_count), node_name)
            net.transitions.add(trans)
        else:
            print("node_id = ", node_id)
            print("node_name = ", node_name)
            print("node_type = ", node_type)
            print("node_process = ", node_process)

        if "task" in node_type:
            places_count = places_count + 1
            input_place = PetriNet.Place('p_' + str(places_count))
            net.places.add(input_place)
            places_count = places_count + 1
            output_place = PetriNet.Place('p_' + str(places_count))
            net.places.add(output_place)

            corresponding_in_nodes[node_id] = input_place
            corresponding_out_nodes[node_id] = output_place

            utils.add_arc_from_to(input_place, trans, net)
            utils.add_arc_from_to(trans, output_place, net)

    flows = bpmn_graph.get_flows()

    for flow in flows:
        source_ref = flow[2]['sourceRef']
        target_ref = flow[2]['targetRef']

        if source_ref in corresponding_out_nodes and target_ref in corresponding_in_nodes:
            trans_count = trans_count + 1
            trans = PetriNet.Transition('trans_' + str(trans_count), None)
            net.transitions.add(trans)

            utils.add_arc_from_to(corresponding_out_nodes[source_ref], trans, net)
            target_arc = utils.add_arc_from_to(trans, corresponding_in_nodes[target_ref], net)

            corresponding_arcs[target_arc] = flow

    return net, initial_marking, final_marking
