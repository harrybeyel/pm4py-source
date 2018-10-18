import bpmn_python.bpmn_diagram_import as bpmn_importer_internal
import bpmn_python.bpmn_diagram_rep as diagram


def import_bpmn(file_path):
    """
    Import a BPMN 2.0 diagram from an XML file

    Parameters
    ----------
    file_path
        File where the XML file is saved

    Returns
    ----------
    bpmn_graph
        BPMN graph object
    """
    bpmn_graph = diagram.BpmnDiagramGraph()
    bpmn_importer_internal.BpmnDiagramGraphImport.load_diagram_from_xml(file_path, bpmn_graph)
    return bpmn_graph
