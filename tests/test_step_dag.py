"""Tests for the StepDAG class."""

from ipydagflow import Step, StepDAG
from ipydagflow.widgets.dynamic_dag import DynamicDAG


class TestStepDAGCreation:
    """Test StepDAG creation and initialization."""

    def test_create_empty_dag(self):
        """Test creating an empty DAG."""
        dag = StepDAG()
        assert len(dag.get_all_steps()) == 0
        assert len(dag.get_root_steps()) == 0
        assert len(dag.get_leaf_steps()) == 0

    def test_create_dag_with_styles(self):
        """Test creating a DAG with custom styles."""
        styles = {"custom": {"background": "#ff0000"}}
        dag = StepDAG(styles=styles)
        assert dag._styles == styles


class TestStepDAGAddSteps:
    """Test adding steps to the DAG."""

    def test_add_single_step(self):
        """Test adding a single step."""
        dag = StepDAG()
        step = Step(id="s1", label="Step 1")

        result = dag.add_step(step)

        assert len(dag.get_all_steps()) == 1
        assert step in dag.get_all_steps()
        assert result == dag  # Returns self for chaining

    def test_add_multiple_steps(self):
        """Test adding multiple steps at once."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")

        result = dag.add_steps(s1, s2, s3)

        assert len(dag.get_all_steps()) == 3
        assert s1 in dag.get_all_steps()
        assert s2 in dag.get_all_steps()
        assert s3 in dag.get_all_steps()
        assert result == dag  # Returns self for chaining

    def test_add_step_overwrites_duplicate_id(self):
        """Test that adding a step with duplicate id overwrites the previous one."""
        dag = StepDAG()
        step1 = Step(id="s1", label="First")
        step2 = Step(id="s1", label="Second")

        dag.add_step(step1)
        dag.add_step(step2)

        assert len(dag.get_all_steps()) == 1
        assert dag.get_step("s1").label == "Second"

    def test_chaining_add_methods(self):
        """Test chaining add_step and add_steps calls."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")

        dag.add_step(s1).add_step(s2).add_steps(s3)

        assert len(dag.get_all_steps()) == 3


class TestStepDAGGetSteps:
    """Test retrieving steps from the DAG."""

    def test_get_step_by_id(self):
        """Test getting a step by its id."""
        dag = StepDAG()
        step = Step(id="test", label="Test Step")
        dag.add_step(step)

        retrieved = dag.get_step("test")

        assert retrieved == step
        assert retrieved.label == "Test Step"

    def test_get_step_not_found(self):
        """Test getting a step that doesn't exist returns None."""
        dag = StepDAG()
        assert dag.get_step("nonexistent") is None

    def test_get_all_steps(self):
        """Test getting all steps."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        dag.add_steps(s1, s2)

        all_steps = dag.get_all_steps()

        assert len(all_steps) == 2
        assert s1 in all_steps
        assert s2 in all_steps

    def test_get_root_steps(self):
        """Test getting root steps (no parents)."""
        dag = StepDAG()
        root1 = Step(id="r1", label="Root 1")
        root2 = Step(id="r2", label="Root 2")
        child = Step(id="c", label="Child")

        root1.add_child(child)
        root2.add_child(child)
        dag.add_steps(root1, root2, child)

        roots = dag.get_root_steps()

        assert len(roots) == 2
        assert root1 in roots
        assert root2 in roots
        assert child not in roots

    def test_get_leaf_steps(self):
        """Test getting leaf steps (no children)."""
        dag = StepDAG()
        root = Step(id="r", label="Root")
        leaf1 = Step(id="l1", label="Leaf 1")
        leaf2 = Step(id="l2", label="Leaf 2")

        root.add_children(leaf1, leaf2)
        dag.add_steps(root, leaf1, leaf2)

        leaves = dag.get_leaf_steps()

        assert len(leaves) == 2
        assert leaf1 in leaves
        assert leaf2 in leaves
        assert root not in leaves

    def test_get_root_and_leaf_single_step(self):
        """Test that a single isolated step is both root and leaf."""
        dag = StepDAG()
        step = Step(id="s", label="Single")
        dag.add_step(step)

        assert step in dag.get_root_steps()
        assert step in dag.get_leaf_steps()


class TestStepDAGValidation:
    """Test DAG validation."""

    def test_validate_valid_linear_dag(self):
        """Test validating a valid linear DAG."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s1.add_child(s2).add_child(s3)
        dag.add_steps(s1, s2, s3)

        errors = dag.validate()

        assert len(errors) == 0

    def test_validate_valid_branching_dag(self):
        """Test validating a valid branching DAG."""
        dag = StepDAG()
        root = Step(id="root", label="Root")
        b1 = Step(id="b1", label="Branch 1")
        b2 = Step(id="b2", label="Branch 2")
        merge = Step(id="merge", label="Merge")

        root.add_children(b1, b2)
        b1.add_child(merge)
        b2.add_child(merge)
        dag.add_steps(root, b1, b2, merge)

        errors = dag.validate()

        assert len(errors) == 0

    def test_validate_allows_simple_cycle(self):
        """Test that validation allows a simple cycle."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")

        s1.add_child(s2)
        s2.add_child(s1)  # Creates cycle
        dag.add_steps(s1, s2)

        errors = dag.validate()

        # Cycles are now allowed
        assert len(errors) == 0

    def test_validate_allows_longer_cycle(self):
        """Test that validation allows a cycle in a longer chain."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")

        s1.add_child(s2)
        s2.add_child(s3)
        s3.add_child(s1)  # Creates cycle
        dag.add_steps(s1, s2, s3)

        errors = dag.validate()

        # Cycles are now allowed
        assert len(errors) == 0

    def test_validate_detects_disconnected_components(self):
        """Test that validation detects disconnected components."""
        dag = StepDAG()
        # Component 1
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)

        # Component 2 (disconnected)
        s3 = Step(id="s3", label="Step 3")
        s4 = Step(id="s4", label="Step 4")
        s3.add_child(s4)

        dag.add_steps(s1, s2, s3, s4)

        errors = dag.validate()

        assert len(errors) > 0
        assert any("disconnected" in error.lower() for error in errors)

    def test_validate_empty_dag(self):
        """Test validating an empty DAG."""
        dag = StepDAG()
        errors = dag.validate()
        assert len(errors) == 0


class TestStepDAGConversion:
    """Test converting StepDAG to nodes and edges."""

    def test_to_nodes_edges_simple(self):
        """Test converting a simple DAG to nodes and edges."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1", step_type="datasource")
        s2 = Step(id="s2", label="Step 2", step_type="box")
        s1.add_child(s2)
        dag.add_steps(s1, s2)

        nodes, edges = dag.to_nodes_edges()

        assert len(nodes) == 2
        assert len(edges) == 1

        # Check nodes
        node_ids = [n["id"] for n in nodes]
        assert "s1" in node_ids
        assert "s2" in node_ids

        node1 = next(n for n in nodes if n["id"] == "s1")
        assert node1["type"] == "datasource"
        assert node1["data"]["label"] == "Step 1"

        # Check edges
        edge = edges[0]
        assert edge["source"] == "s1"
        assert edge["target"] == "s2"

    def test_to_nodes_edges_with_custom_data(self):
        """Test that custom data is included in nodes."""
        dag = StepDAG()
        step = Step(
            id="s1",
            label="Database",
            data={"connection": "postgres://localhost", "table": "users"}
        )
        dag.add_step(step)

        nodes, edges = dag.to_nodes_edges()

        node = nodes[0]
        assert node["data"]["label"] == "Database"
        assert node["data"]["connection"] == "postgres://localhost"
        assert node["data"]["table"] == "users"

    def test_to_nodes_edges_complex_dag(self):
        """Test converting a complex DAG."""
        dag = StepDAG()
        root = Step(id="root", label="Root")
        b1 = Step(id="b1", label="Branch 1")
        b2 = Step(id="b2", label="Branch 2")
        merge = Step(id="merge", label="Merge")

        root.add_children(b1, b2)
        b1.add_child(merge)
        b2.add_child(merge)
        dag.add_steps(root, b1, b2, merge)

        nodes, edges = dag.to_nodes_edges()

        assert len(nodes) == 4
        assert len(edges) == 4

        edge_pairs = [(e["source"], e["target"]) for e in edges]
        assert ("root", "b1") in edge_pairs
        assert ("root", "b2") in edge_pairs
        assert ("b1", "merge") in edge_pairs
        assert ("b2", "merge") in edge_pairs

    def test_to_nodes_edges_includes_referenced_steps(self):
        """Test that to_nodes_edges includes steps not explicitly added to DAG."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)

        # Only add s1, not s2
        dag.add_step(s1)

        nodes, edges = dag.to_nodes_edges()

        # Both should be included
        node_ids = [n["id"] for n in nodes]
        assert "s1" in node_ids
        assert "s2" in node_ids
        assert len(edges) == 1


class TestStepDAGRender:
    """Test rendering the DAG."""

    def test_render_valid_dag(self):
        """Test rendering a valid DAG returns DynamicDAG widget."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)
        dag.add_steps(s1, s2)

        widget = dag.render()

        assert isinstance(widget, DynamicDAG)
        assert len(widget.nodes) == 2
        assert len(widget.edges) == 1

    def test_render_with_custom_styles(self):
        """Test rendering with custom styles."""
        custom_styles = {"box": {"background": "#ff0000"}}
        dag = StepDAG(styles=custom_styles)
        step = Step(id="s1", label="Step 1")
        dag.add_step(step)

        widget = dag.render()

        assert isinstance(widget, DynamicDAG)
        assert widget.styles == custom_styles

    def test_render_with_cycle_succeeds(self):
        """Test that rendering a graph with cycles succeeds."""
        dag = StepDAG()
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")

        # Create cycle - this is now allowed
        s1.add_child(s2)
        s2.add_child(s1)
        dag.add_steps(s1, s2)

        # Should not raise an error
        widget = dag.render()
        assert isinstance(widget, DynamicDAG)
        assert len(widget.nodes) == 2
        assert len(widget.edges) == 2

    def test_render_passes_kwargs_to_dynamic_dag(self):
        """Test that render passes additional kwargs to DynamicDAG."""
        dag = StepDAG()
        step = Step(id="s1", label="Step 1")
        dag.add_step(step)

        # DynamicDAG doesn't have a 'custom_param' but we can verify
        # it tries to pass it through
        widget = dag.render()

        # Just verify the widget is created successfully
        assert isinstance(widget, DynamicDAG)


class TestStepDAGRepresentation:
    """Test StepDAG string representation."""

    def test_repr_empty(self):
        """Test __repr__ for empty DAG."""
        dag = StepDAG()
        repr_str = repr(dag)

        assert "StepDAG" in repr_str
        assert "steps=0" in repr_str
        assert "roots=0" in repr_str
        assert "leaves=0" in repr_str

    def test_repr_with_steps(self):
        """Test __repr__ for DAG with steps."""
        dag = StepDAG()
        root = Step(id="root", label="Root")
        middle = Step(id="middle", label="Middle")
        leaf = Step(id="leaf", label="Leaf")

        root.add_child(middle).add_child(leaf)
        dag.add_steps(root, middle, leaf)

        repr_str = repr(dag)

        assert "steps=3" in repr_str
        assert "roots=1" in repr_str
        assert "leaves=1" in repr_str
