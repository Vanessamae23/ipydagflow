"""Step class for building DAGs programmatically."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


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
