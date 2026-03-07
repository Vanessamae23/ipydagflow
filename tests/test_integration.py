"""Integration tests for the complete ipydagflow workflow."""

import pytest

from ipydagflow import DynamicDAG, Step, StepDAG


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_simple_etl_workflow(self):
        """Test a simple ETL workflow from Step creation to rendering."""
        # Create steps
        extract = Step(id="extract", label="Extract Data", step_type="datasource")
        transform = Step(id="transform", label="Transform", step_type="box")
        load = Step(id="load", label="Load to DB", step_type="datasource")

        # Connect steps
        extract.add_child(transform).add_child(load)

        # Create DAG
        dag = StepDAG()
        dag.add_steps(extract, transform, load)

        # Render
        widget = dag.render()

        # Verify
        assert isinstance(widget, DynamicDAG)
        assert len(widget.nodes) == 3
        assert len(widget.edges) == 2

    def test_branching_workflow(self):
        """Test a branching workflow."""
        # Create steps
        source = Step(id="source", label="Data Source", step_type="datasource")
        branch1 = Step(id="branch1", label="Process A", step_type="box")
        branch2 = Step(id="branch2", label="Process B", step_type="box")
        merge = Step(id="merge", label="Merge", step_type="box")
        sink = Step(id="sink", label="Output", step_type="datasource")

        # Build structure
        source.add_children(branch1, branch2)
        branch1.add_child(merge)
        branch2.add_child(merge)
        merge.add_child(sink)

        # Create and render
        dag = StepDAG()
        dag.add_steps(source, branch1, branch2, merge, sink)
        widget = dag.render()

        # Verify structure
        assert len(widget.nodes) == 5
        assert len(widget.edges) == 5

        # Verify roots and leaves
        assert len(dag.get_root_steps()) == 1
        assert len(dag.get_leaf_steps()) == 1
        assert dag.get_root_steps()[0] == source
        assert dag.get_leaf_steps()[0] == sink

    def test_workflow_with_custom_data(self):
        """Test workflow with custom metadata."""
        # Create steps with custom data
        db_step = Step(
            id="database",
            label="PostgreSQL",
            step_type="datasource",
            data={
                "connection": "postgres://localhost:5432/mydb",
                "table": "orders",
                "query": "SELECT * FROM orders WHERE date > :date"
            }
        )

        process_step = Step(
            id="process",
            label="Calculate Metrics",
            step_type="box",
            data={
                "metrics": ["revenue", "avg_order_value"],
                "window": "7d"
            }
        )

        output_step = Step(
            id="output",
            label="S3 Bucket",
            step_type="datasource",
            data={
                "bucket": "s3://my-bucket/metrics",
                "format": "parquet",
                "partition": "date"
            }
        )

        db_step.add_child(process_step).add_child(output_step)

        dag = StepDAG()
        dag.add_steps(db_step, process_step, output_step)
        widget = dag.render()

        # Verify custom data is preserved
        db_node = next(n for n in widget.nodes if n["id"] == "database")
        assert db_node["data"]["connection"] == "postgres://localhost:5432/mydb"
        assert db_node["data"]["table"] == "orders"

        process_node = next(n for n in widget.nodes if n["id"] == "process")
        assert "revenue" in process_node["data"]["metrics"]

    def test_workflow_with_custom_styles(self):
        """Test workflow with custom styling."""
        custom_styles = {
            "datasource": {
                "background": "rgba(255, 99, 132, 0.8)",
                "color": "white",
                "borderColor": "#ff6384",
            },
            "box": {
                "background": "rgba(54, 162, 235, 0.8)",
                "color": "white",
                "borderColor": "#36a2eb",
            },
        }

        s1 = Step(id="s1", label="Source", step_type="datasource")
        s2 = Step(id="s2", label="Process", step_type="box")
        s1.add_child(s2)

        dag = StepDAG(styles=custom_styles)
        dag.add_steps(s1, s2)
        widget = dag.render()

        assert widget.styles == custom_styles

    def test_complex_ml_pipeline(self):
        """Test a complex ML pipeline workflow."""
        # Data sources
        raw_data = Step(id="raw", label="Raw Data", step_type="datasource")

        # Preprocessing
        clean = Step(id="clean", label="Clean Data", step_type="box")

        # Feature engineering
        feature_a = Step(id="feat_a", label="Feature A", step_type="box")
        feature_b = Step(id="feat_b", label="Feature B", step_type="box")
        feature_c = Step(id="feat_c", label="Feature C", step_type="box")

        # Merge features
        combine = Step(id="combine", label="Combine Features", step_type="box")

        # Model training
        train = Step(id="train", label="Train Model", step_type="box")

        # Evaluation
        evaluate = Step(id="eval", label="Evaluate", step_type="box")

        # Deployment
        deploy = Step(id="deploy", label="Deploy", step_type="datasource")

        # Build pipeline
        raw_data.add_child(clean)
        clean.add_children(feature_a, feature_b, feature_c)
        feature_a.add_child(combine)
        feature_b.add_child(combine)
        feature_c.add_child(combine)
        combine.add_child(train)
        train.add_child(evaluate)
        evaluate.add_child(deploy)

        # Create DAG
        dag = StepDAG()
        dag.add_steps(
            raw_data, clean, feature_a, feature_b, feature_c,
            combine, train, evaluate, deploy
        )

        # Verify structure
        assert len(dag.get_all_steps()) == 9
        assert len(dag.get_root_steps()) == 1
        assert len(dag.get_leaf_steps()) == 1

        # Verify no cycles
        errors = dag.validate()
        assert len(errors) == 0

        # Render
        widget = dag.render()
        assert len(widget.nodes) == 9


class TestImports:
    """Test that all imports work correctly."""

    def test_import_from_main_module(self):
        """Test importing from main ipydagflow module."""
        from ipydagflow import DynamicDAG, Step, StepDAG

        assert DynamicDAG is not None
        assert StepDAG is not None
        assert Step is not None

    def test_import_from_submodules(self):
        """Test importing from submodules."""
        from ipydagflow.models import Step
        from ipydagflow.utils import detect_cycles, topological_sort
        from ipydagflow.widgets import DynamicDAG, StepDAG

        assert DynamicDAG is not None
        assert StepDAG is not None
        assert Step is not None
        assert topological_sort is not None
        assert detect_cycles is not None


class TestErrorHandling:
    """Test error handling across the system."""

    def test_cycles_are_allowed(self):
        """Test that cycles are allowed in the graph."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")

        s1.add_child(s2)
        s2.add_child(s3)
        s3.add_child(s1)  # Creates cycle

        dag = StepDAG()
        dag.add_steps(s1, s2, s3)

        # Should not raise an error
        widget = dag.render()
        assert isinstance(widget, DynamicDAG)
        assert len(widget.nodes) == 3
        assert len(widget.edges) == 3

    def test_validation_catches_disconnected_components(self):
        """Test that validation catches disconnected components."""
        # Component 1
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s1.add_child(s2)

        # Component 2 (disconnected)
        s3 = Step(id="s3", label="Step 3")
        s4 = Step(id="s4", label="Step 4")
        s3.add_child(s4)

        dag = StepDAG()
        dag.add_steps(s1, s2, s3, s4)

        with pytest.raises(ValueError) as exc_info:
            dag.render()

        assert "disconnected" in str(exc_info.value).lower()


class TestStepTraversalInDAG:
    """Test step traversal within a DAG context."""

    def test_descendants_in_dag(self):
        """Test getting all descendants of a step within a DAG."""
        root = Step(id="root", label="Root")
        child1 = Step(id="c1", label="Child 1")
        child2 = Step(id="c2", label="Child 2")
        grandchild = Step(id="gc", label="Grandchild")

        root.add_children(child1, child2)
        child1.add_child(grandchild)

        descendants = root.get_all_descendants()

        assert len(descendants) == 3
        assert child1 in descendants
        assert child2 in descendants
        assert grandchild in descendants

    def test_ancestors_in_dag(self):
        """Test getting all ancestors of a step within a DAG."""
        root = Step(id="root", label="Root")
        middle = Step(id="m", label="Middle")
        leaf = Step(id="leaf", label="Leaf")

        root.add_child(middle).add_child(leaf)

        ancestors = leaf.get_all_ancestors()

        assert len(ancestors) == 2
        assert root in ancestors
        assert middle in ancestors
