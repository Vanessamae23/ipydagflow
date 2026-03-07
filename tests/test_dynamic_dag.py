"""Tests for the DynamicDAG widget."""

from ipydagflow.widgets.dynamic_dag import DynamicDAG


class TestDynamicDAGCreation:
    """Test DynamicDAG widget creation."""

    def test_create_empty_widget(self):
        """Test creating an empty widget."""
        widget = DynamicDAG()

        assert widget.nodes == []
        assert widget.edges == []
        assert widget.selected_node == {}

    def test_create_with_nodes_and_edges(self):
        """Test creating widget with nodes and edges."""
        nodes = [
            {"id": "1", "type": "datasource", "data": {"label": "Node 1"}},
            {"id": "2", "type": "box", "data": {"label": "Node 2"}},
        ]
        edges = [
            {"id": "e1", "source": "1", "target": "2"}
        ]

        widget = DynamicDAG(nodes=nodes, edges=edges)

        assert len(widget.nodes) == 2
        assert len(widget.edges) == 1
        assert widget.nodes[0]["id"] == "1"
        assert widget.edges[0]["source"] == "1"
        assert widget.edges[0]["target"] == "2"

    def test_create_with_custom_styles(self):
        """Test creating widget with custom styles."""
        custom_styles = {
            "datasource": {
                "background": "#ff0000",
                "color": "white",
            }
        }

        widget = DynamicDAG(styles=custom_styles)

        assert widget.styles == custom_styles

    def test_default_styles(self):
        """Test that default styles are set."""
        widget = DynamicDAG()

        assert "datasource" in widget.styles
        assert "box" in widget.styles
        assert "default" in widget.styles
        assert "background" in widget.styles["datasource"]
        assert "borderColor" in widget.styles["box"]


class TestDynamicDAGNodes:
    """Test node operations."""

    def test_modify_nodes(self):
        """Test modifying nodes after creation."""
        widget = DynamicDAG()

        new_nodes = [
            {"id": "1", "type": "box", "data": {"label": "Test"}},
        ]
        widget.nodes = new_nodes

        assert len(widget.nodes) == 1
        assert widget.nodes[0]["id"] == "1"

    def test_add_nodes_incrementally(self):
        """Test adding nodes one by one."""
        widget = DynamicDAG()

        widget.nodes = [{"id": "1", "type": "box", "data": {"label": "Node 1"}}]
        widget.nodes = widget.nodes + [{"id": "2", "type": "box", "data": {"label": "Node 2"}}]

        assert len(widget.nodes) == 2

    def test_node_with_custom_data(self):
        """Test nodes with custom data fields."""
        nodes = [
            {
                "id": "db",
                "type": "datasource",
                "data": {
                    "label": "Database",
                    "connection": "postgres://localhost",
                    "table": "users",
                }
            }
        ]

        widget = DynamicDAG(nodes=nodes)

        node = widget.nodes[0]
        assert node["data"]["connection"] == "postgres://localhost"
        assert node["data"]["table"] == "users"


class TestDynamicDAGEdges:
    """Test edge operations."""

    def test_modify_edges(self):
        """Test modifying edges after creation."""
        nodes = [
            {"id": "1", "data": {"label": "A"}},
            {"id": "2", "data": {"label": "B"}},
        ]
        widget = DynamicDAG(nodes=nodes)

        widget.edges = [{"id": "e1", "source": "1", "target": "2"}]

        assert len(widget.edges) == 1
        assert widget.edges[0]["source"] == "1"
        assert widget.edges[0]["target"] == "2"

    def test_multiple_edges(self):
        """Test widget with multiple edges."""
        nodes = [
            {"id": "1", "data": {"label": "A"}},
            {"id": "2", "data": {"label": "B"}},
            {"id": "3", "data": {"label": "C"}},
        ]
        edges = [
            {"id": "e1", "source": "1", "target": "2"},
            {"id": "e2", "source": "1", "target": "3"},
            {"id": "e3", "source": "2", "target": "3"},
        ]

        widget = DynamicDAG(nodes=nodes, edges=edges)

        assert len(widget.edges) == 3


class TestDynamicDAGTraits:
    """Test widget traits and synchronization."""

    def test_traits_are_synchronized(self):
        """Test that traits have sync=True."""
        widget = DynamicDAG()

        # Check that traits are tagged for sync
        assert widget.traits()['nodes'].metadata.get('sync') is True
        assert widget.traits()['edges'].metadata.get('sync') is True
        assert widget.traits()['selected_node'].metadata.get('sync') is True
        assert widget.traits()['styles'].metadata.get('sync') is True

    def test_selected_node(self):
        """Test selected_node trait."""
        widget = DynamicDAG()

        assert widget.selected_node == {}

        # Simulate a node selection
        widget.selected_node = {"id": "1", "label": "Test"}

        assert widget.selected_node["id"] == "1"


class TestDynamicDAGIntegration:
    """Test complete widget scenarios."""

    def test_simple_pipeline(self):
        """Test a simple ETL pipeline."""
        nodes = [
            {"id": "extract", "type": "datasource", "data": {"label": "Extract"}},
            {"id": "transform", "type": "box", "data": {"label": "Transform"}},
            {"id": "load", "type": "datasource", "data": {"label": "Load"}},
        ]
        edges = [
            {"id": "e1", "source": "extract", "target": "transform"},
            {"id": "e2", "source": "transform", "target": "load"},
        ]

        widget = DynamicDAG(nodes=nodes, edges=edges)

        assert len(widget.nodes) == 3
        assert len(widget.edges) == 2

    def test_branching_workflow(self):
        """Test a branching workflow."""
        nodes = [
            {"id": "source", "type": "datasource", "data": {"label": "Source"}},
            {"id": "branch1", "type": "box", "data": {"label": "Branch 1"}},
            {"id": "branch2", "type": "box", "data": {"label": "Branch 2"}},
            {"id": "merge", "type": "box", "data": {"label": "Merge"}},
        ]
        edges = [
            {"id": "e1", "source": "source", "target": "branch1"},
            {"id": "e2", "source": "source", "target": "branch2"},
            {"id": "e3", "source": "branch1", "target": "merge"},
            {"id": "e4", "source": "branch2", "target": "merge"},
        ]

        widget = DynamicDAG(nodes=nodes, edges=edges)

        assert len(widget.nodes) == 4
        assert len(widget.edges) == 4

        # Verify branching structure
        source_edges = [e for e in widget.edges if e["source"] == "source"]
        assert len(source_edges) == 2

        merge_edges = [e for e in widget.edges if e["target"] == "merge"]
        assert len(merge_edges) == 2
