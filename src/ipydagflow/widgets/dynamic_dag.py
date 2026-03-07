"""DynamicDAG widget for rendering flow diagrams."""

import pathlib

import anywidget
import traitlets


class DynamicDAG(anywidget.AnyWidget):
    """
    Interactive DAG visualization widget using React Flow.

    Attributes:
        nodes: List of node dictionaries with id, type, data, and optional position
        edges: List of edge dictionaries connecting nodes
        selected_node: Currently selected node information
        styles: Style configuration for different node types

    Example:
        >>> nodes = [
        ...     {"id": "1", "type": "datasource", "data": {"label": "Input"}},
        ...     {"id": "2", "type": "box", "data": {"label": "Process"}},
        ... ]
        >>> edges = [{"id": "e1", "source": "1", "target": "2"}]
        >>> dag = DynamicDAG(nodes=nodes, edges=edges)
        >>> dag  # Display in Jupyter
    """

    _esm = pathlib.Path(__file__).parent.parent / "static" / "dynamic_dag.js"
    _css = pathlib.Path(__file__).parent.parent / "static" / "dynamic_dag.css"

    nodes = traitlets.List([]).tag(sync=True)
    edges = traitlets.List([]).tag(sync=True)
    selected_node = traitlets.Dict({}).tag(sync=True)

    # Style customization
    styles = traitlets.Dict({
        "datasource": {
            "background": "rgba(102, 126, 234, 0.8)",
            "color": "white",
            "borderColor": "#5a67d8",
            "borderWidth": 2,
        },
        "box": {
            "background": "rgba(72, 187, 120, 0.8)",
            "color": "white",
            "borderColor": "#38a169",
            "borderWidth": 2,
        },
        "default": {
            "background": "rgba(255, 255, 255, 0.8)",
            "color": "#333",
            "borderColor": "#2c3e50",
            "borderWidth": 2,
        }
    }).tag(sync=True)
