# ipydagflow

Interactive DAG visualization for Jupyter notebooks.

```{toctree}
:maxdepth: 2
:caption: Contents

getting-started
api
```

## Features

::::{grid} 2
:gutter: 3

:::{grid-item-card} Interactive DAGs
:link: getting-started
:link-type: doc

Build and visualize directed acyclic graphs directly in Jupyter.
:::

:::{grid-item-card} API Reference
:link: api
:link-type: doc

Complete API documentation with examples.
:::

::::

## Installation

```bash
pip install ipydagflow
```

## Quick Start

```python
from ipydagflow import DynamicDAG

dag = DynamicDAG()
dag
```
