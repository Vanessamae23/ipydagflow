"""Tests for layout utilities."""

import pytest

from ipydagflow.models.step import Step
from ipydagflow.utils.layout import detect_cycles, topological_sort


class TestDetectCycles:
    """Test cycle detection."""

    def test_no_cycles_linear(self):
        """Test that a linear chain has no cycles."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s1.add_child(s2).add_child(s3)

        cycles = detect_cycles([s1, s2, s3])

        assert len(cycles) == 0

    def test_no_cycles_branching(self):
        """Test that a branching DAG has no cycles."""
        root = Step(id="root", label="Root")
        b1 = Step(id="b1", label="Branch 1")
        b2 = Step(id="b2", label="Branch 2")
        leaf = Step(id="leaf", label="Leaf")

        root.add_children(b1, b2)
        b1.add_child(leaf)
        b2.add_child(leaf)

        cycles = detect_cycles([root, b1, b2, leaf])

        assert len(cycles) == 0

    def test_no_cycles_empty(self):
        """Test empty list has no cycles."""
        cycles = detect_cycles([])
        assert len(cycles) == 0

    def test_no_cycles_single_step(self):
        """Test single step has no cycles."""
        step = Step(id="s1", label="Step 1")
        cycles = detect_cycles([step])
        assert len(cycles) == 0

    def test_detects_simple_cycle(self):
        """Test detecting a simple 2-node cycle."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)
        s2.add_child(s1)

        cycles = detect_cycles([s1, s2])

        assert len(cycles) > 0
        cycle = cycles[0]
        assert "s1" in cycle
        assert "s2" in cycle

    def test_detects_self_loop(self):
        """Test detecting a self-loop."""
        s1 = Step(id="s1", label="Step 1")
        s1.add_child(s1)

        cycles = detect_cycles([s1])

        assert len(cycles) > 0

    def test_detects_longer_cycle(self):
        """Test detecting a cycle in a longer chain."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s4 = Step(id="s4", label="Step 4")

        s1.add_child(s2)
        s2.add_child(s3)
        s3.add_child(s4)
        s4.add_child(s2)  # Creates cycle s2 -> s3 -> s4 -> s2

        cycles = detect_cycles([s1, s2, s3, s4])

        assert len(cycles) > 0
        cycle = cycles[0]
        assert "s2" in cycle
        assert "s3" in cycle
        assert "s4" in cycle

    def test_detects_multiple_cycles(self):
        """Test detecting multiple cycles."""
        # Cycle 1: s1 -> s2 -> s1
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)
        s2.add_child(s1)

        # Cycle 2: s3 -> s4 -> s3
        s3 = Step(id="s3", label="Step 3")
        s4 = Step(id="s4", label="Step 4")
        s3.add_child(s4)
        s4.add_child(s3)

        cycles = detect_cycles([s1, s2, s3, s4])

        # Should detect at least one cycle (may detect multiple)
        assert len(cycles) > 0


class TestTopologicalSort:
    """Test topological sorting."""

    def test_sort_linear_chain(self):
        """Test sorting a linear chain."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s1.add_child(s2).add_child(s3)

        sorted_steps = topological_sort([s1, s2, s3])

        assert len(sorted_steps) == 3
        assert sorted_steps.index(s1) < sorted_steps.index(s2)
        assert sorted_steps.index(s2) < sorted_steps.index(s3)

    def test_sort_branching_dag(self):
        """Test sorting a branching DAG."""
        root = Step(id="root", label="Root")
        b1 = Step(id="b1", label="Branch 1")
        b2 = Step(id="b2", label="Branch 2")
        merge = Step(id="merge", label="Merge")

        root.add_children(b1, b2)
        b1.add_child(merge)
        b2.add_child(merge)

        sorted_steps = topological_sort([root, b1, b2, merge])

        assert len(sorted_steps) == 4
        # Root should come first
        assert sorted_steps[0] == root
        # Merge should come last
        assert sorted_steps[3] == merge
        # b1 and b2 should be in the middle
        assert sorted_steps.index(root) < sorted_steps.index(b1)
        assert sorted_steps.index(root) < sorted_steps.index(b2)
        assert sorted_steps.index(b1) < sorted_steps.index(merge)
        assert sorted_steps.index(b2) < sorted_steps.index(merge)

    def test_sort_complex_dag(self):
        """Test sorting a more complex DAG."""
        s1 = Step(id="s1", label="1")
        s2 = Step(id="s2", label="2")
        s3 = Step(id="s3", label="3")
        s4 = Step(id="s4", label="4")
        s5 = Step(id="s5", label="5")

        s1.add_children(s2, s3)
        s2.add_child(s4)
        s3.add_child(s4)
        s4.add_child(s5)

        sorted_steps = topological_sort([s1, s2, s3, s4, s5])

        assert len(sorted_steps) == 5
        assert sorted_steps.index(s1) < sorted_steps.index(s2)
        assert sorted_steps.index(s1) < sorted_steps.index(s3)
        assert sorted_steps.index(s2) < sorted_steps.index(s4)
        assert sorted_steps.index(s3) < sorted_steps.index(s4)
        assert sorted_steps.index(s4) < sorted_steps.index(s5)

    def test_sort_single_step(self):
        """Test sorting a single step."""
        step = Step(id="s1", label="Step 1")
        sorted_steps = topological_sort([step])

        assert len(sorted_steps) == 1
        assert sorted_steps[0] == step

    def test_sort_disconnected_components(self):
        """Test sorting with disconnected components."""
        # Component 1
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)

        # Component 2 (disconnected)
        s3 = Step(id="s3", label="Step 3")

        sorted_steps = topological_sort([s1, s2, s3])

        assert len(sorted_steps) == 3
        # s1 should come before s2
        assert sorted_steps.index(s1) < sorted_steps.index(s2)
        # s3 can be anywhere since it's disconnected

    def test_sort_with_cycle_raises_error(self):
        """Test that sorting a graph with cycles raises ValueError."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)
        s2.add_child(s1)

        with pytest.raises(ValueError) as exc_info:
            topological_sort([s1, s2])

        assert "cycle" in str(exc_info.value).lower()

    def test_sort_preserves_partial_order(self):
        """Test that sorting preserves the partial order of dependencies."""
        # Diamond pattern
        root = Step(id="root", label="Root")
        left = Step(id="left", label="Left")
        right = Step(id="right", label="Right")
        bottom = Step(id="bottom", label="Bottom")

        root.add_children(left, right)
        left.add_child(bottom)
        right.add_child(bottom)

        sorted_steps = topological_sort([root, left, right, bottom])

        # Verify dependencies are respected
        assert sorted_steps.index(root) < sorted_steps.index(left)
        assert sorted_steps.index(root) < sorted_steps.index(right)
        assert sorted_steps.index(left) < sorted_steps.index(bottom)
        assert sorted_steps.index(right) < sorted_steps.index(bottom)


class TestLayoutEdgeCases:
    """Test edge cases in layout utilities."""

    def test_empty_list(self):
        """Test that empty list works for both functions."""
        assert detect_cycles([]) == []
        assert topological_sort([]) == []

    def test_isolated_steps(self):
        """Test handling of completely isolated steps."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")

        # No connections
        cycles = detect_cycles([s1, s2, s3])
        assert len(cycles) == 0

        sorted_steps = topological_sort([s1, s2, s3])
        assert len(sorted_steps) == 3
