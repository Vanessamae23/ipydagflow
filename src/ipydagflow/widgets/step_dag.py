"""StepDAG widget for building DAGs programmatically with Step objects."""

from typing import Dict, List, Optional, Set, Union

from ..models.step import Step, Subflow
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
        self._subflows: Dict[str, Subflow] = {}
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

    def add_subflow(self, subflow: Subflow) -> "StepDAG":
        """
        Add a subflow to the DAG.

        Args:
            subflow: Subflow to add

        Returns:
            Self for chaining
        """
        self._subflows[subflow.id] = subflow
        # Also add all steps within the subflow
        for step in subflow.steps:
            self._steps[step.id] = step
        return self

    def add_subflows(self, *subflows: Subflow) -> "StepDAG":
        """
        Add multiple subflows to the DAG.

        Args:
            *subflows: Variable number of subflows to add

        Returns:
            Self for chaining
        """
        for subflow in subflows:
            self.add_subflow(subflow)
        return self

    def get_subflow(self, subflow_id: str) -> Optional[Subflow]:
        """
        Get a subflow by ID.

        Args:
            subflow_id: ID of the subflow to retrieve

        Returns:
            Subflow if found, None otherwise
        """
        return self._subflows.get(subflow_id)

    def get_all_subflows(self) -> List[Subflow]:
        """Get all subflows in the DAG."""
        return list(self._subflows.values())

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

        # Check for disconnected components (considering subflows)
        if self._steps or self._subflows:
            visited_steps: Set[str] = set()
            visited_subflows: Set[str] = set()

            def visit_subflow(subflow: Subflow):
                if subflow.id in visited_subflows:
                    return
                visited_subflows.add(subflow.id)
                # All steps in a subflow are connected
                for step in subflow.steps:
                    visit_step(step)
                # Visit connected subflows/steps
                for child in subflow.children:
                    if isinstance(child, Subflow):
                        visit_subflow(child)
                    else:
                        visit_step(child)
                for parent in subflow.parents:
                    if isinstance(parent, Subflow):
                        visit_subflow(parent)
                    else:
                        visit_step(parent)

            def visit_step(step: Step):
                if step.id in visited_steps:
                    return
                visited_steps.add(step.id)
                # If step is in a subflow, visit the subflow
                if step.subflow is not None:
                    visit_subflow(step.subflow)
                for child in step.children:
                    if isinstance(child, Subflow):
                        visit_subflow(child)
                    else:
                        visit_step(child)
                for parent in step.parents:
                    if isinstance(parent, Subflow):
                        visit_subflow(parent)
                    else:
                        visit_step(parent)

            # Start from first subflow or step
            if self._subflows:
                first_subflow = next(iter(self._subflows.values()))
                visit_subflow(first_subflow)
            elif self._steps:
                first_step = next(iter(self._steps.values()))
                visit_step(first_step)

            # Check for disconnected steps
            disconnected = set(self._steps.keys()) - visited_steps
            if disconnected:
                errors.append(f"Disconnected steps: {', '.join(disconnected)}")

            # Check for disconnected subflows
            disconnected_subflows = set(self._subflows.keys()) - visited_subflows
            if disconnected_subflows:
                errors.append(f"Disconnected subflows: {', '.join(disconnected_subflows)}")

        return errors

    def to_nodes_edges(self) -> tuple[List[Dict], List[Dict]]:
        """
        Convert steps and subflows to nodes and edges format for DynamicDAG.

        Returns:
            Tuple of (nodes, edges) suitable for DynamicDAG
        """
        nodes = []

        # First, add subflow nodes (must come before their contained steps)
        for subflow in self._subflows.values():
            node = {
                "id": subflow.id,
                "type": "subflow",
                "data": {
                    "label": subflow.label,
                    **subflow.data
                },
                "style": {
                    "width": subflow.width,
                    "height": subflow.height,
                }
            }
            nodes.append(node)

        # Collect all steps (including those referenced as children/parents)
        # Filter out Subflows - only collect Step objects
        all_steps: Set[Step] = set(self._steps.values())
        for step in self._steps.values():
            all_steps.update(c for c in step.children if isinstance(c, Step))
            all_steps.update(p for p in step.parents if isinstance(p, Step))

        # Convert steps to nodes
        for step in all_steps:
            node = {
                "id": step.id,
                "type": step.step_type,
                "data": {
                    "label": step.label,
                    **step.data
                }
            }
            # If step belongs to a subflow, add parentId and extent
            if step.subflow is not None:
                node["parentId"] = step.subflow.id
                node["extent"] = "parent"
            nodes.append(node)

        # Convert relationships to edges
        edges = []
        edge_id = 0

        # Edges from steps
        for step in all_steps:
            for child in step.children:
                child_id = child.id if isinstance(child, Step) else child.id
                edge = {
                    "id": f"e{edge_id}",
                    "source": step.id,
                    "target": child_id
                }
                # Add label if present
                edge_label = step.get_edge_label(child_id)
                if edge_label:
                    edge["label"] = edge_label
                edges.append(edge)
                edge_id += 1

        # Edges from subflows
        for subflow in self._subflows.values():
            for child in subflow.children:
                child_id = child.id
                edge = {
                    "id": f"e{edge_id}",
                    "source": subflow.id,
                    "target": child_id
                }
                # Add label if present
                edge_label = subflow.get_edge_label(child_id)
                if edge_label:
                    edge["label"] = edge_label
                edges.append(edge)
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
        subflow_count = len(self._subflows)
        root_count = len(self.get_root_steps())
        leaf_count = len(self.get_leaf_steps())
        return f"StepDAG(steps={step_count}, subflows={subflow_count}, roots={root_count}, leaves={leaf_count})"
