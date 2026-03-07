import * as React from "react";
import { createRender, useModelState } from "@anywidget/react";
import { useCallback, useState } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ReactFlowProvider,
  Handle,
  Position,
  Node,
  Edge,
  NodeProps,
  Connection,
  NodeChange,
  EdgeChange,
} from "@xyflow/react";
import dagre from "dagre";
import "@xyflow/react/dist/style.css";
import "./dynamic_dag.css";

interface NodeData {
  label: string;
  [key: string]: any;
}

interface NodeStyle {
  background: string;
  color: string;
  borderColor: string;
  borderWidth: number;
}

interface StylesConfig {
  datasource: NodeStyle;
  box: NodeStyle;
  default: NodeStyle;
  [key: string]: NodeStyle;
}

// Custom DataSource Node (cylinder shape)
const createDataSourceNode = (styles: NodeStyle) => {
  const DataSourceNode: React.FC<NodeProps<NodeData>> = ({ data, selected }) => {
    return (
      <div
        className={`custom-node datasource-node ${selected ? 'selected' : ''}`}
        style={{
          background: styles.background,
          color: styles.color,
          borderColor: selected ? '#3498db' : styles.borderColor,
          borderWidth: `${styles.borderWidth}px`,
          borderStyle: 'solid',
        }}
      >
        <Handle type="target" position={Position.Top} />
        <div className="node-content">
          <div className="node-label">{data.label}</div>
        </div>
        <Handle type="source" position={Position.Bottom} />
      </div>
    );
  };
  return DataSourceNode;
};

// Custom Box Node (rectangular shape)
const createBoxNode = (styles: NodeStyle) => {
  const BoxNode: React.FC<NodeProps<NodeData>> = ({ data, selected }) => {
    return (
      <div
        className={`custom-node box-node ${selected ? 'selected' : ''}`}
        style={{
          background: styles.background,
          color: styles.color,
          borderColor: selected ? '#3498db' : styles.borderColor,
          borderWidth: `${styles.borderWidth}px`,
          borderStyle: 'solid',
        }}
      >
        <Handle type="target" position={Position.Top} />
        <div className="node-content">
          <div className="node-label">{data.label}</div>
        </div>
        <Handle type="source" position={Position.Bottom} />
      </div>
    );
  };
  return BoxNode;
};


// Auto-layout function using dagre
const getLayoutedElements = (nodes: Node[], edges: Edge[]): Node[] => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: "TB", ranksep: 120, nodesep: 80 });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 150, height: 80 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 75,
        y: nodeWithPosition.y - 40,
      },
    };
  });

  return layoutedNodes;
};

const FlowComponent: React.FC = () => {
  const [inputNodes, setInputNodes] = useModelState<Node[]>("nodes");
  const [inputEdges, setInputEdges] = useModelState<Edge[]>("edges");
  const [selectedNodeInfo, setSelectedNodeInfo] = useModelState<Node | null>("selected_node");
  const [stylesConfig] = useModelState<StylesConfig>("styles");
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [popup, setPopup] = useState<Node | null>(null);

  // Create node types with dynamic styles
  const nodeTypes = React.useMemo(() => {
    if (!stylesConfig) return {};
    return {
      datasource: createDataSourceNode(stylesConfig.datasource),
      box: createBoxNode(stylesConfig.box),
    };
  }, [stylesConfig]);

  // Update nodes when inputNodes changes
  React.useEffect(() => {
    if (inputNodes && Array.isArray(inputNodes) && inputNodes.length > 0) {
      // Check if any node is missing position
      const needsLayout = inputNodes.some(node => !node.position || (node.position.x === undefined && node.position.y === undefined));

      if (needsLayout && inputEdges) {
        // Apply auto-layout
        const layoutedNodes = getLayoutedElements(inputNodes, inputEdges);
        setNodes(layoutedNodes);
      } else {
        setNodes(inputNodes);
      }
    }
  }, [inputNodes, inputEdges, setNodes]);

  // Update edges when inputEdges changes
  React.useEffect(() => {
    if (inputEdges && Array.isArray(inputEdges)) {
      setEdges(inputEdges);
    }
  }, [inputEdges, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdges = addEdge({ ...params, style: { strokeWidth: 2 } }, edges);
      setEdges(newEdges);
      // Sync back to Python
      setInputEdges(newEdges);
    },
    [edges, setEdges, setInputEdges]
  );

  const onNodesChangeHandler = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes);
      // Optionally sync node changes back to Python
      // This would require batching changes to avoid too many syncs
    },
    [onNodesChange]
  );

  const onEdgesChangeHandler = useCallback(
    (changes: EdgeChange[]) => {
      onEdgesChange(changes);
    },
    [onEdgesChange]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      console.log("Node clicked:", node);
      setPopup(node);
      setSelectedNodeInfo(node);
    },
    [setSelectedNodeInfo]
  );

  const closePopup = () => {
    setPopup(null);
  };

  return (
    <div style={{ position: "relative", height: "500px", width: "100%" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChangeHandler}
        onEdgesChange={onEdgesChangeHandler}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Background />
        <Controls />
      </ReactFlow>

      {popup && (
        <div className="node-popup">
          <div className="popup-content">
            <button className="close-btn" onClick={closePopup}>×</button>
            <h3>{(popup.data as NodeData)?.label || popup.id}</h3>
            <div className="popup-body">
              <p><strong>ID:</strong> {popup.id}</p>
              <p><strong>Type:</strong> {popup.type || 'default'}</p>
              {popup.data && Object.keys(popup.data).length > 1 && (
                <>
                  <p><strong>Additional Data:</strong></p>
                  <pre>{JSON.stringify(popup.data, null, 2)}</pre>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const render = createRender(() => {
  return (
    <ReactFlowProvider>
      <FlowComponent />
    </ReactFlowProvider>
  );
});

export default { render };
