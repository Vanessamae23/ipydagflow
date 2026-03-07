"""StepDAG widget for building DAGs programmatically with Step objects."""

from typing import Dict, List, Optional, Set

from ..models.step import Step
from .dynamic_dag import DynamicDAG


class StepDAG:
    """
    High-level graph builder using Step objects.

    Build directed graphs programmatically by creating Step objects and connecting them,
    then render as a visual widget. Cycles are allowed.

    Example:
        >>> from ipydagflow import StepDAG, Step
        >>>
        >>> # Create steps
        >>> extract = Step(id="extract", label="Extract Data", step_type="datasource")
        >>> transform = Step(id="transform", label="Transform", step_type="box")
        >>> load = Step(id="load", label="Load to DB", step_type="datasource")
        >>>
        >>> # Connect steps
        >>> extract.add_child(transform)
        >>> transform.add_child(load)
        >>>
        >>> # Create and display DAG
        >>> dag = StepDAG()
        >>> dag.add_steps(extract, transform, load)
        >>> dag.render()  # Returns DynamicDAG widget
    """

    def __init__(self, styles: Optional[Dict] = None):
        """
        Initialize StepDAG.

        Args:
            styles: Optional custom styles for node types
        """
        self._steps: Dict[str, Step] = {}
        self._styles = styles

    def add_step(self, step: Step) -> "StepDAG":
        """
        Add a step to the DAG.

        Args:
            step: Step to add

        Returns:
            Self for chaining
        """
        self._steps[step.id] = step
        return self

    def add_steps(self, *steps: Step) -> "StepDAG":
        """
        Add multiple steps to the DAG.

        Args:
            *steps: Variable number of steps to add

        Returns:
            Self for chaining
        """
        for step in steps:
            self.add_step(step)
        return self

    def get_step(self, step_id: str) -> Optional[Step]:
        """
        Get a step by ID.

        Args:
            step_id: ID of the step to retrieve

        Returns:
            Step if found, None otherwise
        """
        return self._steps.get(step_id)

    def get_all_steps(self) -> List[Step]:
        """Get all steps in the DAG."""
        return list(self._steps.values())

    def get_root_steps(self) -> List[Step]:
        """Get all root steps (steps with no parents)."""
        return [step for step in self._steps.values() if not step.parents]

    def get_leaf_steps(self) -> List[Step]:
        """Get all leaf steps (steps with no children)."""
        return [step for step in self._steps.values() if not step.children]

    def validate(self) -> List[str]:
        """
        Validate the graph structure.

        Note: Cycles are allowed in the graph.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Note: Cycles are allowed, so we don't check for them

        # Check for disconnected components
        if self._steps:
            visited: Set[str] = set()

            def visit(step: Step):
                if step.id in visited:
                    return
                visited.add(step.id)
                for child in step.children:
                    visit(child)
                for parent in step.parents:
                    visit(parent)

            # Start from first step
            first_step = next(iter(self._steps.values()))
            visit(first_step)

            disconnected = set(self._steps.keys()) - visited
            if disconnected:
                errors.append(f"Disconnected steps: {', '.join(disconnected)}")

        return errors

    def to_nodes_edges(self) -> tuple[List[Dict], List[Dict]]:
        """
        Convert steps to nodes and edges format for DynamicDAG.

        Returns:
            Tuple of (nodes, edges) suitable for DynamicDAG
        """
        # Collect all steps (including those referenced as children/parents)
        all_steps: Set[Step] = set(self._steps.values())
        for step in self._steps.values():
            all_steps.update(step.children)
            all_steps.update(step.parents)

        # Convert steps to nodes
        nodes = []
        for step in all_steps:
            node = {
                "id": step.id,
                "type": step.step_type,
                "data": {
                    "label": step.label,
                    **step.data
                }
            }
            nodes.append(node)

        # Convert relationships to edges
        edges = []
        edge_id = 0
        for step in all_steps:
            for child in step.children:
                edges.append({
                    "id": f"e{edge_id}",
                    "source": step.id,
                    "target": child.id
                })
                edge_id += 1

        return nodes, edges

    def render(self, **kwargs) -> DynamicDAG:
        """
        Render the graph as a DynamicDAG widget.

        Args:
            **kwargs: Additional arguments passed to DynamicDAG

        Returns:
            DynamicDAG widget ready to display

        Raises:
            ValueError: If the graph is invalid
        """
        # Validate first
        errors = self.validate()
        if errors:
            raise ValueError("Invalid graph:\n" + "\n".join(f"  - {e}" for e in errors))

        # Convert to nodes and edges
        nodes, edges = self.to_nodes_edges()

        # Create widget
        widget_kwargs = {"nodes": nodes, "edges": edges}
        if self._styles:
            widget_kwargs["styles"] = self._styles
        widget_kwargs.update(kwargs)

        return DynamicDAG(**widget_kwargs)

    def __repr__(self) -> str:
        """String representation."""
        step_count = len(self._steps)
        root_count = len(self.get_root_steps())
        leaf_count = len(self.get_leaf_steps())
        return f"StepDAG(steps={step_count}, roots={root_count}, leaves={leaf_count})"
