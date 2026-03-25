"""Step class for building DAGs programmatically."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union


@dataclass
class Step:
    """
    Represents a single step/node in a DAG workflow.

    Attributes:
        id: Unique identifier for the step
        label: Display label for the step
        step_type: Type of step (datasource, box, etc.)
        data: Additional metadata for the step
        children: List of child steps
        parents: List of parent steps
        subflow: Reference to the containing Subflow (if any)

    Example:
        >>> step1 = Step(id="extract", label="Extract Data", step_type="datasource")
        >>> step2 = Step(id="transform", label="Transform", step_type="box")
        >>> step1.add_child(step2)
    """

    id: str
    label: str
    step_type: str = "box"
    data: Dict[str, Any] = field(default_factory=dict)
    children: List["Step"] = field(default_factory=list, repr=False)
    parents: List["Step"] = field(default_factory=list, repr=False)
    subflow: Optional["Subflow"] = field(default=None, repr=False)

    def add_child(self, child: "Step") -> "Step":
        """
        Add a child step.

        Args:
            child: The child step to add

        Returns:
            The child step (for chaining)
        """
        if child not in self.children:
            self.children.append(child)
        if self not in child.parents:
            child.parents.append(self)
        return child

    def add_children(self, *children: "Step") -> List["Step"]:
        """
        Add multiple child steps.

        Args:
            *children: Variable number of child steps

        Returns:
            List of child steps
        """
        return [self.add_child(child) for child in children]

    def add_parent(self, parent: "Step") -> "Step":
        """
        Add a parent step.

        Args:
            parent: The parent step to add

        Returns:
            The parent step (for chaining)
        """
        if parent not in self.parents:
            self.parents.append(parent)
        if self not in parent.children:
            parent.children.append(self)
        return parent

    def get_all_descendants(self) -> Set["Step"]:
        """Get all descendant steps (children, grandchildren, etc.)."""
        descendants = set()
        to_visit = list(self.children)

        while to_visit:
            step = to_visit.pop()
            if step not in descendants:
                descendants.add(step)
                to_visit.extend(step.children)

        return descendants

    def get_all_ancestors(self) -> Set["Step"]:
        """Get all ancestor steps (parents, grandparents, etc.)."""
        ancestors = set()
        to_visit = list(self.parents)

        while to_visit:
            step = to_visit.pop()
            if step not in ancestors:
                ancestors.add(step)
                to_visit.extend(step.parents)

        return ancestors

    def __hash__(self) -> int:
        """Make Step hashable based on id."""
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on id."""
        if not isinstance(other, Step):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        """String representation."""
        return f"Step(id='{self.id}', label='{self.label}', type='{self.step_type}')"


@dataclass
class Subflow:
    """
    Represents a container/group that can hold multiple steps.

    Subflows are rendered as group nodes in React Flow, with contained
    steps rendered inside them.

    Attributes:
        id: Unique identifier for the subflow
        label: Display label for the subflow
        steps: List of steps contained in this subflow
        data: Additional metadata for the subflow
        width: Width of the subflow container
        height: Height of the subflow container
        children: List of child subflows/steps (DAG edges from this subflow)
        parents: List of parent subflows/steps (DAG edges to this subflow)

    Example:
        >>> from ipydagflow import StepDAG, Step, Subflow
        >>>
        >>> # Create a subflow container
        >>> subflow = Subflow(id="etl", label="ETL Pipeline", width=300, height=200)
        >>>
        >>> # Create steps and add them to the subflow
        >>> extract = Step(id="extract", label="Extract")
        >>> transform = Step(id="transform", label="Transform")
        >>> subflow.add_steps(extract, transform)
        >>>
        >>> # Connect steps within the subflow
        >>> extract.add_child(transform)
        >>>
        >>> # Create external step and connect to subflow
        >>> output = Step(id="output", label="Output")
        >>> subflow.add_child(output)
        >>>
        >>> # Render the DAG
        >>> dag = StepDAG()
        >>> dag.add_subflow(subflow)
        >>> dag.add_step(output)
        >>> dag.render()
    """

    id: str
    label: str
    steps: list[Step] = field(default_factory=list, repr=False)
    data: dict[str, Any] = field(default_factory=dict)
    width: int = 200
    height: int = 150
    children: list[Union["Subflow", Step]] = field(default_factory=list, repr=False)
    parents: list[Union["Subflow", Step]] = field(default_factory=list, repr=False)

    def add_step(self, step: Step) -> Step:
        """
        Add a step to this subflow.

        Args:
            step: The step to add to this subflow

        Returns:
            The step (for chaining)
        """
        if step not in self.steps:
            self.steps.append(step)
        step.subflow = self
        return step

    def add_steps(self, *steps: Step) -> list[Step]:
        """
        Add multiple steps to this subflow.

        Args:
            *steps: Variable number of steps to add

        Returns:
            List of added steps
        """
        return [self.add_step(step) for step in steps]

    def remove_step(self, step: Step) -> bool:
        """
        Remove a step from this subflow.

        Args:
            step: The step to remove

        Returns:
            True if step was removed, False if not found
        """
        if step in self.steps:
            self.steps.remove(step)
            step.subflow = None
            return True
        return False

    def add_child(self, child: Union["Subflow", Step]) -> Union["Subflow", Step]:
        """
        Add a child subflow or step (creates a DAG edge).

        Args:
            child: The child subflow or step to connect

        Returns:
            The child (for chaining)
        """
        if child not in self.children:
            self.children.append(child)
        if self not in child.parents:
            child.parents.append(self)
        return child

    def add_parent(self, parent: Union["Subflow", Step]) -> Union["Subflow", Step]:
        """
        Add a parent subflow or step (creates a DAG edge).

        Args:
            parent: The parent subflow or step to connect

        Returns:
            The parent (for chaining)
        """
        if parent not in self.parents:
            self.parents.append(parent)
        if self not in parent.children:
            parent.children.append(self)
        return parent

    def __hash__(self) -> int:
        """Make Subflow hashable based on id."""
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on id."""
        if not isinstance(other, Subflow):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        """String representation."""
        return f"Subflow(id='{self.id}', label='{self.label}', steps={len(self.steps)})"
