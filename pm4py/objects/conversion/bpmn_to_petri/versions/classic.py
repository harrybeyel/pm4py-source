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

    start_event_subprocess = {}
    end_event_subprocess = {}

    # adds nodes
    for node in nodes:
        node_id = node[1]['id']
        node_name = node[1]['node_name'].replace("\r", " ").replace("\n", " ").strip() if 'node_name' in node[
            1] else None
        node_type = node[1]['type'].lower()
        node_process = node[1]['process'].lower()

        if "task" in node_type:
            trans_count = trans_count + 1
            trans = PetriNet.Transition('tasktrans_' + str(trans_count), node_name)
            net.transitions.add(trans)
        elif "gateway" in node_type:
            if "exclusivegateway" in node_type:
                places_count = places_count + 1
                input_place = PetriNet.Place('exclgatinppl_' + str(places_count))
                net.places.add(input_place)

                places_count = places_count + 1
                output_place = PetriNet.Place('exclgatoutpl_' + str(places_count))
                net.places.add(output_place)

                trans_count = trans_count + 1
                trans = PetriNet.Transition(node_id, None)
                net.transitions.add(trans)

                utils.add_arc_from_to(input_place, trans, net)
                utils.add_arc_from_to(trans, output_place, net)

                corresponding_in_nodes[node_id] = [input_place] * len(node[1]['incoming'])
                corresponding_out_nodes[node_id] = [output_place] * len(node[1]['outgoing'])
            elif "parallelgateway" in node_type:
                if len(node[1]['incoming']) > len(node[1]['outgoing']):
                    print("PARALLEL SPLIT GATEWAY")
                else:
                    print("PARALLEL JOIN GATEWAY")
        elif node_type == "startevent":
            #places_count = places_count + 1
            if "subprocess" in node_name:
                print("SUBPROCESSSSSSSSS")
                source_place = PetriNet.Place('so_'+str(node_process))
                net.places.add(source_place)
            else:
                print("MAIN PROCESSSSSSS")
                source_place = PetriNet.Place('so_'+str(node_id))
                net.places.add(source_place)

            corresponding_in_nodes[node_id] = [source_place]
            corresponding_out_nodes[node_id] = [source_place]

            start_event_subprocess[node_process] = source_place

            print("AA ",node_process, node[1])
        elif node_type == "endevent":
            #places_count = places_count + 1
            if "subprocess" in node_name:
                sink_place = PetriNet.Place('si_'+str(node_process))
                net.places.add(sink_place)
            else:
                sink_place = PetriNet.Place('si_'+str(node_id))
                net.places.add(sink_place)

            corresponding_in_nodes[node_id] = [sink_place]
            corresponding_out_nodes[node_id] = [sink_place]

            end_event_subprocess[node_process] = sink_place

            print("BB ",node_process, node[1])

        elif "event" in node_type:
            places_count = places_count + 1

            input_place = PetriNet.Place('evp_' + str(places_count))
            net.places.add(input_place)

            places_count = places_count + 1

            output_place = PetriNet.Place('evp_' + str(places_count))
            net.places.add(output_place)

            trans_count = trans_count + 1
            trans = PetriNet.Transition(node_id, None)
            net.transitions.add(trans)

            corresponding_in_nodes[node_id] = [input_place]
            corresponding_in_nodes[node_id] = [output_place]

            utils.add_arc_from_to(input_place, trans, net)
            utils.add_arc_from_to(trans, output_place, net)

            print("CC ",node_process, node[1])
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

            corresponding_in_nodes[node_id] = [input_place]
            corresponding_out_nodes[node_id] = [output_place]

            utils.add_arc_from_to(input_place, trans, net)
            utils.add_arc_from_to(trans, output_place, net)

    # iterate again for subprocesses
    for node in nodes:
        node_id = node[1]['id']
        node_name = node[1]['node_name'].replace("\r", " ").replace("\n", " ").strip() if 'node_name' in node[
            1] else None
        node_type = node[1]['type'].lower()
        node_process = node[1]['process'].lower()

        if node_type == "subprocess":
            print(node_process)
            if node_process in start_event_subprocess and node_process in end_event_subprocess:
                corresponding_in_nodes[node_id] = [start_event_subprocess[node_process]]
                corresponding_out_nodes[node_id] = [end_event_subprocess[node_process]]

                print("SUBPROCESS",node_process)

    flows = bpmn_graph.get_flows()

    for flow in flows:
        source_ref = flow[2]['sourceRef']
        target_ref = flow[2]['targetRef']

        if source_ref in corresponding_out_nodes and target_ref in corresponding_in_nodes:
            trans_count = trans_count + 1
            trans = PetriNet.Transition('flowtrans_' + str(trans_count), None)
            net.transitions.add(trans)

            utils.add_arc_from_to(corresponding_out_nodes[source_ref].pop(0), trans, net)
            target_arc = utils.add_arc_from_to(trans, corresponding_in_nodes[target_ref].pop(0), net)

            corresponding_arcs[target_arc] = flow

    return net, initial_marking, final_marking
