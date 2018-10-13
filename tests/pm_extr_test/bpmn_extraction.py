import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)
import time
from pm4py.objects.log.importer.xes import factory as xes_factory
from pm4py.algo.discovery.inductive import factory as inductive
from pm4py.algo.discovery.alpha import factory as alpha
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.simplicity import factory as simplicity_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.objects.log.util import insert_classifier
from pm4py.objects.petri.exporter import pnml as pnml_exporter
from pm4py.visualization.petrinet import factory as petri_vis_factory
from pm4py.visualization.common.save import save as vis_save
from pm4py import util as pmutil
from pm4py.visualization.bpmn import factory as bpmn_vis_factory
from pm4py.objects.bpmn.exporter import bpmn20 as bpmn_exporter
from pm4py.objects.conversion.petri_to_bpmn import factory as bpmn_converter

if __name__ == "__main__":
    bpmn_folder = "bpmn_folder"
    log_folder = "..\\compressed_input_data"

    for log_name in os.listdir(log_folder):
        if "." in log_name:
            log_name_prefix = log_name.split(".")[0]

            print("\nelaborating " + log_name)

            logPath = os.path.join(log_folder, log_name)
            log = xes_factory.import_log(logPath, variant="iterparse")

            log, classifier_key = insert_classifier.search_and_insert_activity_classifier_attribute(log)

            print("loaded log")

            activity_key = "concept:name"
            if not classifier_key is None:
                activity_key = classifier_key

            parameters_discovery = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key,
                                    pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: activity_key}

            net, initial_marking, final_marking = inductive.apply(log, parameters=parameters_discovery)

            parameters_visualization = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key,
                                    pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: activity_key,
                                        "format":"png"}

            frequency_figure = bpmn_vis_factory.apply_petri(net, initial_marking, final_marking, log=log, variant="frequency", parameters=parameters_visualization)
            performance_figure = bpmn_vis_factory.apply_petri(net, initial_marking, final_marking, log=log, variant="performance", parameters=parameters_visualization)

            frequency_path = os.path.join(bpmn_folder, log_name_prefix + "_bpmn_freq.png")
            performance_path = os.path.join(bpmn_folder, log_name_prefix + "_bpmn_perf.png")
            bpmn20_path = os.path.join(bpmn_folder, log_name_prefix + ".bpmn")

            bpmn_vis_factory.save(frequency_figure, frequency_path)
            bpmn_vis_factory.save(performance_figure, performance_path)

            bpmn_graph, elements_correspondence, inv_elements_correspondence, el_corr_keys_map = bpmn_converter.apply(
                net, initial_marking, final_marking)

            bpmn_exporter.export_bpmn(bpmn_graph, bpmn20_path)