# Getting Started

## Installation

Install ipydagflow using pip:

```bash
pip install ipydagflow
```

Or with uv:

```bash
uv add ipydagflow
```

## Basic Usage

```python
from ipydagflow import DynamicDAG

# Create a new DAG widget
dag = DynamicDAG()

# Display in Jupyter
dag
```

## Adding Nodes and Edges

```python
# Add nodes
dag.add_node("A", label="Start")
dag.add_node("B", label="Process")
dag.add_node("C", label="End")

# Add edges
dag.add_edge("A", "B")
dag.add_edge("B", "C")
```
