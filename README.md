# ipydagflow

Interactive DAG (Directed Acyclic Graph) visualization widgets for Jupyter notebooks using React Flow.

## Features

- 🎨 **Beautiful Interactive Visualizations** - Smooth, modern DAG rendering with React Flow
- 🔧 **Two APIs** - Low-level (DynamicDAG) and high-level (StepDAG) interfaces
- 🎯 **Automatic Layout** - No need to specify positions - nodes are laid out automatically
- 🎨 **Customizable Styles** - Full control over colors, borders, and appearance
- 📊 **Built for Data Pipelines** - Perfect for ETL workflows, ML pipelines, and task dependencies
- ✅ **Validation** - Automatic cycle detection and DAG validation
- 🔍 **Interactive** - Click nodes to see details, drag to rearrange

## Installation

```bash
pip install ipydagflow
```

For development:
```bash
git clone https://github.com/yourusername/ipydagflow
cd ipydagflow
pip install -e .
```

## Quick Start

### High-Level API (StepDAG)

Build DAGs programmatically using Step objects:

```python
from ipydagflow import StepDAG, Step

# Create steps
extract = Step(id="extract", label="Extract Data", step_type="datasource")
transform = Step(id="transform", label="Transform", step_type="box")
load = Step(id="load", label="Load to DB", step_type="datasource")

# Connect steps
extract.add_child(transform)
transform.add_child(load)

# Create and display DAG
dag = StepDAG()
dag.add_steps(extract, transform, load)
dag.render()  # Returns a widget to display in Jupyter
```

### Low-Level API (DynamicDAG)

For direct control over nodes and edges:

```python
from ipydagflow import DynamicDAG

nodes = [
    {"id": "1", "type": "datasource", "data": {"label": "Input"}},
    {"id": "2", "type": "box", "data": {"label": "Process"}},
    {"id": "3", "type": "datasource", "data": {"label": "Output"}},
]

edges = [
    {"id": "e1", "source": "1", "target": "2"},
    {"id": "e2", "source": "2", "target": "3"},
]

dag = DynamicDAG(nodes=nodes, edges=edges)
dag  # Display in Jupyter
```

## Examples

### Complex Pipeline

```python
from ipydagflow import StepDAG, Step

# Build a data processing pipeline
raw = Step(id="raw", label="Raw Data", step_type="datasource")
clean = Step(id="clean", label="Clean", step_type="box")
feature_a = Step(id="feat_a", label="Feature A", step_type="box")
feature_b = Step(id="feat_b", label="Feature B", step_type="box")
combine = Step(id="combine", label="Combine", step_type="box")
output = Step(id="output", label="Output", step_type="datasource")

# Connect: raw -> clean -> [feature_a, feature_b] -> combine -> output
raw.add_child(clean)
clean.add_children(feature_a, feature_b)
feature_a.add_child(combine)
feature_b.add_child(combine)
combine.add_child(output)

# Render
dag = StepDAG()
dag.add_steps(raw, clean, feature_a, feature_b, combine, output)
dag.render()
```

### Custom Styling

```python
custom_styles = {
    "datasource": {
        "background": "rgba(255, 99, 132, 0.8)",
        "color": "white",
        "borderColor": "#ff6384",
        "borderWidth": 3,
    },
    "box": {
        "background": "rgba(54, 162, 235, 0.8)",
        "color": "white",
        "borderColor": "#36a2eb",
        "borderWidth": 2,
    },
}

dag = StepDAG(styles=custom_styles)
dag.add_steps(step1, step2, step3)
dag.render()
```

### Adding Metadata

```python
step = Step(
    id="process",
    label="Calculate Metrics",
    step_type="box",
    data={
        "owner": "data-team",
        "schedule": "0 0 * * *",
        "retry": 3,
        "timeout": "1h"
    }
)
# Click the node in the widget to see the metadata!
```

## API Reference

### Step

```python
Step(
    id: str,              # Unique identifier
    label: str,           # Display label
    step_type: str,       # Node type: "datasource", "box", or custom
    data: dict            # Additional metadata
)
```

**Methods:**
- `add_child(step)` - Add a child step
- `add_children(*steps)` - Add multiple children
- `add_parent(step)` - Add a parent step
- `get_all_descendants()` - Get all descendant steps
- `get_all_ancestors()` - Get all ancestor steps

### StepDAG

```python
StepDAG(styles: dict = None)
```

**Methods:**
- `add_step(step)` - Add a step
- `add_steps(*steps)` - Add multiple steps
- `get_step(step_id)` - Get step by ID
- `get_all_steps()` - Get all steps
- `get_root_steps()` - Get steps with no parents
- `get_leaf_steps()` - Get steps with no children
- `validate()` - Validate DAG (returns list of errors)
- `render()` - Create and return DynamicDAG widget

### DynamicDAG

```python
DynamicDAG(
    nodes: list,          # List of node dicts
    edges: list,          # List of edge dicts
    styles: dict = None   # Custom styling
)
```

**Node format:**
```python
{
    "id": "unique_id",
    "type": "datasource",  # or "box"
    "data": {"label": "Display Name", ...},
    "position": {"x": 100, "y": 100}  # Optional - auto-layout if omitted
}
```

**Edge format:**
```python
{
    "id": "edge_id",
    "source": "source_node_id",
    "target": "target_node_id",
    "animated": True  # Optional
}
```

## Development

### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/ipydagflow
cd ipydagflow

# Install dependencies
npm install
pip install -e .

# Build JavaScript
npm run build

# Run in dev mode (auto-rebuild on changes)
npm run dev
```

### Project Structure

```
ipydagflow/
├── src/
│   └── ipydagflow/
│       ├── __init__.py           # Main exports
│       ├── widgets/              # Widget classes
│       │   ├── dynamic_dag.py    # Low-level widget
│       │   └── step_dag.py       # High-level builder
│       ├── models/               # Data models
│       │   └── step.py           # Step class
│       ├── utils/                # Utilities
│       │   └── layout.py         # Layout algorithms
│       └── static/               # Built JS/CSS
├── ui/                           # TypeScript/React source
│   ├── dynamic_dag.tsx          # React Flow component
│   └── dynamic_dag.css          # Styles
└── examples/                     # Example notebooks
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.
