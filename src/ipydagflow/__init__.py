"""
ipydagflow - Interactive DAG visualization widgets for Jupyter.

This library provides tools for creating and visualizing directed acyclic graphs (DAGs)
in Jupyter notebooks using React Flow.

Main classes:
    - DynamicDAG: Low-level widget for rendering DAGs from nodes/edges
    - StepDAG: High-level DAG builder using Step objects
    - Step: Represents a single step/node in a workflow
    - Subflow: Container/group that can hold multiple steps

Example (Low-level):
    >>> from ipydagflow import DynamicDAG
    >>> nodes = [
    ...     {"id": "1", "type": "datasource", "data": {"label": "Input"}},
    ...     {"id": "2", "type": "box", "data": {"label": "Process"}},
    ... ]
    >>> edges = [{"id": "e1", "source": "1", "target": "2"}]
    >>> DynamicDAG(nodes=nodes, edges=edges)

Example (High-level):
    >>> from ipydagflow import StepDAG, Step
    >>> extract = Step(id="extract", label="Extract", step_type="datasource")
    >>> transform = Step(id="transform", label="Transform", step_type="box")
    >>> extract.add_child(transform)
    >>> dag = StepDAG()
    >>> dag.add_steps(extract, transform)
    >>> dag.render()

Example (With Subflow):
    >>> from ipydagflow import StepDAG, Step, Subflow
    >>> subflow = Subflow(id="etl", label="ETL Pipeline", width=300, height=200)
    >>> extract = Step(id="extract", label="Extract")
    >>> transform = Step(id="transform", label="Transform")
    >>> subflow.add_steps(extract, transform)
    >>> extract.add_child(transform)
    >>> dag = StepDAG()
    >>> dag.add_subflow(subflow)
    >>> dag.render()
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("ipydagflow")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

# Main exports
from .models import Step, Subflow
from .widgets import DynamicDAG, StepDAG

__all__ = [
    "DynamicDAG",
    "Step",
    "StepDAG",
    "Subflow",
    "__version__",
]
