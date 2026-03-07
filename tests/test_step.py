"""Tests for the Step model."""

from ipydagflow.models.step import Step


class TestStepCreation:
    """Test Step creation and initialization."""

    def test_create_step_minimal(self):
        """Test creating a step with minimal parameters."""
        step = Step(id="test", label="Test Step")
        assert step.id == "test"
        assert step.label == "Test Step"
        assert step.step_type == "box"
        assert step.data == {}
        assert step.children == []
        assert step.parents == []

    def test_create_step_with_type(self):
        """Test creating a step with custom type."""
        step = Step(id="ds", label="Data Source", step_type="datasource")
        assert step.step_type == "datasource"

    def test_create_step_with_data(self):
        """Test creating a step with custom data."""
        data = {"connection": "postgres://localhost", "table": "users"}
        step = Step(id="db", label="Database", data=data)
        assert step.data == data
        assert step.data["connection"] == "postgres://localhost"


class TestStepRelationships:
    """Test Step parent/child relationships."""

    def test_add_child(self):
        """Test adding a child step."""
        parent = Step(id="parent", label="Parent")
        child = Step(id="child", label="Child")

        result = parent.add_child(child)

        assert child in parent.children
        assert parent in child.parents
        assert result == child  # Returns child for chaining

    def test_add_child_idempotent(self):
        """Test that adding same child multiple times doesn't duplicate."""
        parent = Step(id="parent", label="Parent")
        child = Step(id="child", label="Child")

        parent.add_child(child)
        parent.add_child(child)

        assert len(parent.children) == 1
        assert len(child.parents) == 1

    def test_add_children_multiple(self):
        """Test adding multiple children at once."""
        parent = Step(id="parent", label="Parent")
        child1 = Step(id="child1", label="Child 1")
        child2 = Step(id="child2", label="Child 2")
        child3 = Step(id="child3", label="Child 3")

        result = parent.add_children(child1, child2, child3)

        assert len(parent.children) == 3
        assert child1 in parent.children
        assert child2 in parent.children
        assert child3 in parent.children
        assert parent in child1.parents
        assert parent in child2.parents
        assert parent in child3.parents
        assert result == [child1, child2, child3]

    def test_add_parent(self):
        """Test adding a parent step."""
        parent = Step(id="parent", label="Parent")
        child = Step(id="child", label="Child")

        result = child.add_parent(parent)

        assert parent in child.parents
        assert child in parent.children
        assert result == parent  # Returns parent for chaining

    def test_add_parent_idempotent(self):
        """Test that adding same parent multiple times doesn't duplicate."""
        parent = Step(id="parent", label="Parent")
        child = Step(id="child", label="Child")

        child.add_parent(parent)
        child.add_parent(parent)

        assert len(child.parents) == 1
        assert len(parent.children) == 1

    def test_chaining(self):
        """Test chaining add_child calls."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s4 = Step(id="s4", label="Step 4")

        # Chain: s1 -> s2 -> s3 -> s4
        s1.add_child(s2).add_child(s3).add_child(s4)

        assert s2 in s1.children
        assert s3 in s2.children
        assert s4 in s3.children
        assert s1 in s2.parents
        assert s2 in s3.parents
        assert s3 in s4.parents


class TestStepTraversal:
    """Test Step graph traversal methods."""

    def test_get_all_descendants_linear(self):
        """Test getting descendants in a linear chain."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s1.add_child(s2).add_child(s3)

        descendants = s1.get_all_descendants()

        assert len(descendants) == 2
        assert s2 in descendants
        assert s3 in descendants

    def test_get_all_descendants_branching(self):
        """Test getting descendants in a branching structure."""
        root = Step(id="root", label="Root")
        branch1 = Step(id="b1", label="Branch 1")
        branch2 = Step(id="b2", label="Branch 2")
        leaf1 = Step(id="l1", label="Leaf 1")
        leaf2 = Step(id="l2", label="Leaf 2")

        root.add_children(branch1, branch2)
        branch1.add_child(leaf1)
        branch2.add_child(leaf2)

        descendants = root.get_all_descendants()

        assert len(descendants) == 4
        assert branch1 in descendants
        assert branch2 in descendants
        assert leaf1 in descendants
        assert leaf2 in descendants

    def test_get_all_descendants_empty(self):
        """Test getting descendants when there are none."""
        leaf = Step(id="leaf", label="Leaf")
        descendants = leaf.get_all_descendants()
        assert len(descendants) == 0

    def test_get_all_ancestors_linear(self):
        """Test getting ancestors in a linear chain."""
        s1 = Step(id="s1", label="Step 1")
        s2 = Step(id="s2", label="Step 2")
        s3 = Step(id="s3", label="Step 3")
        s1.add_child(s2).add_child(s3)

        ancestors = s3.get_all_ancestors()

        assert len(ancestors) == 2
        assert s1 in ancestors
        assert s2 in ancestors

    def test_get_all_ancestors_multiple_paths(self):
        """Test getting ancestors with multiple paths."""
        root1 = Step(id="r1", label="Root 1")
        root2 = Step(id="r2", label="Root 2")
        middle = Step(id="m", label="Middle")
        leaf = Step(id="l", label="Leaf")

        root1.add_child(middle)
        root2.add_child(middle)
        middle.add_child(leaf)

        ancestors = leaf.get_all_ancestors()

        assert len(ancestors) == 3
        assert root1 in ancestors
        assert root2 in ancestors
        assert middle in ancestors

    def test_get_all_ancestors_empty(self):
        """Test getting ancestors when there are none."""
        root = Step(id="root", label="Root")
        ancestors = root.get_all_ancestors()
        assert len(ancestors) == 0


class TestStepEquality:
    """Test Step equality and hashing."""

    def test_equality_by_id(self):
        """Test that steps are equal if they have the same id."""
        step1 = Step(id="test", label="Label 1")
        step2 = Step(id="test", label="Label 2")
        assert step1 == step2

    def test_inequality_different_id(self):
        """Test that steps with different ids are not equal."""
        step1 = Step(id="test1", label="Test")
        step2 = Step(id="test2", label="Test")
        assert step1 != step2

    def test_inequality_with_non_step(self):
        """Test that step is not equal to non-step objects."""
        step = Step(id="test", label="Test")
        assert step != "test"
        assert step != 123
        assert step != None

    def test_hashable(self):
        """Test that steps can be used in sets and as dict keys."""
        step1 = Step(id="s1", label="Step 1")
        step2 = Step(id="s2", label="Step 2")
        step3 = Step(id="s1", label="Different label")  # Same id as step1

        step_set = {step1, step2, step3}
        assert len(step_set) == 2  # step1 and step3 are the same

        step_dict = {step1: "value1", step2: "value2"}
        assert step_dict[step3] == "value1"  # step3 has same id as step1

    def test_hash_consistency(self):
        """Test that hash is consistent with equality."""
        step1 = Step(id="test", label="Label 1")
        step2 = Step(id="test", label="Label 2")
        assert hash(step1) == hash(step2)


class TestStepRepresentation:
    """Test Step string representation."""

    def test_repr(self):
        """Test __repr__ output."""
        step = Step(id="test_id", label="Test Label", step_type="datasource")
        repr_str = repr(step)

        assert "Step" in repr_str
        assert "test_id" in repr_str
        assert "Test Label" in repr_str
        assert "datasource" in repr_str

    def test_repr_default_type(self):
        """Test __repr__ with default type."""
        step = Step(id="test", label="Test")
        repr_str = repr(step)
        assert "box" in repr_str
