import bpmn_python.bpmn_diagram_export as bpmn_exporter_internal
import bpmn_python.bpmn_diagram_layouter as bpmn_layouter
import os
import logging

def export_bpmn(bpmn_graph, file_path):
    """
    Export a BPMN 2.0 diagram from a BPMN graph object

    Parameters
    ----------
    bpmn_graph
        BPMN graph
    file_path
        Path where the diagram should be exported
    """
    directory = str(os.path.dirname(file_path))
    if len(directory) == 0:
        directory = os.getcwd()
    file_path = os.path.basename(file_path)
    try:
        bpmn_layouter.generate_layout(bpmn_graph)
    except:
        logging.info("bpmn_layouter terminated")
    directory = directory.replace("\\","\\\\")
    directory = directory + os.sep
    bpmn_exporter_internal.BpmnDiagramGraphExport.export_xml_file(directory, file_path, bpmn_graph)