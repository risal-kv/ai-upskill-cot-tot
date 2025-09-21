import { useState } from 'react';
import type { TreeNode } from '../../types';

interface TreeNodeViewProps {
	node: TreeNode;
	depth?: number;
}

export function TreeNodeView({ node, depth = 0 }: TreeNodeViewProps) {
	const [expanded, setExpanded] = useState(true);
	const hasChildren = !!node.children && node.children.length > 0;

	return (
		<div className="tot-node" style={{ marginLeft: depth * 12 }}>
			<div className="tot-node-header">
				{hasChildren && (
					<button className="toggle" onClick={() => setExpanded((e) => !e)}>
						{expanded ? '−' : '+'}
					</button>
				)}
				<div className="tot-node-content">
					<div className="tot-thought">{node.thought}</div>
					<div className="tot-reason">{node.reason}</div>
					{typeof node.score === 'number' && (
						<div className="tot-score">score: {node.score}</div>
					)}
				</div>
			</div>
			{hasChildren && expanded && (
				<div className="tot-children">
					{node.children!.map((child, idx) => (
						<TreeNodeView key={child.id ?? idx} node={child} depth={depth + 1} />
					))}
				</div>
			)}
		</div>
	);
}

export default TreeNodeView; 