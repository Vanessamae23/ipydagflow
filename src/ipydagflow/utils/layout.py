"""Layout and graph utilities."""

from typing import Dict, List, Set

from ..models.step import Step


def detect_cycles(steps: List[Step]) -> List[List[str]]:
    """
    Detect cycles in the DAG.

    Args:
        steps: List of steps to check

    Returns:
        List of cycles (each cycle is a list of step IDs)
    """
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    cycles: List[List[str]] = []

    def dfs(step: Step, path: List[str]) -> None:
        visited.add(step.id)
        rec_stack.add(step.id)
        path.append(step.id)

        for child in step.children:
            if child.id not in visited:
                dfs(child, path.copy())
            elif child.id in rec_stack:
                # Found a cycle
                cycle_start = path.index(child.id)
                cycles.append(path[cycle_start:] + [child.id])

        rec_stack.remove(step.id)

    # Visit ALL nodes, not just roots, to catch all cycles
    for step in steps:
        if step.id not in visited:
            dfs(step, [])

    return cycles


def topological_sort(steps: List[Step]) -> List[Step]:
    """
    Perform topological sort on steps.

    Args:
        steps: List of steps to sort

    Returns:
        Sorted list of steps (parents before children)

    Raises:
        ValueError: If the graph contains cycles
    """
    # Check for cycles first
    cycles = detect_cycles(steps)
    if cycles:
        cycle_str = " -> ".join(cycles[0])
        raise ValueError(f"DAG contains cycle: {cycle_str}")

    # Calculate in-degree for each step
    in_degree: Dict[str, int] = {step.id: len(step.parents) for step in steps}
    step_map: Dict[str, Step] = {step.id: step for step in steps}

    # Find all nodes with no incoming edges
    queue: List[Step] = [step for step in steps if in_degree[step.id] == 0]
    result: List[Step] = []

    while queue:
        # Remove a node from queue
        current = queue.pop(0)
        result.append(current)

        # For each child of current node
        for child in current.children:
            # Reduce in-degree by 1
            in_degree[child.id] -= 1

            # If in-degree becomes 0, add to queue
            if in_degree[child.id] == 0:
                queue.append(child)

    # Check if all nodes are processed
    if len(result) != len(steps):
        raise ValueError("DAG contains cycle (topological sort failed)")

    return result
