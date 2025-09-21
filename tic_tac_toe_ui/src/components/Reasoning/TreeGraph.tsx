import { useMemo, useRef, useState } from 'react';
import type { TreeNode } from '../../types';

interface TreeGraphProps {
	tree: TreeNode;
	maxDepth?: number; // optional limit if tree is huge
}

interface LaidOutNode {
	id: string;
	x: number;
	y: number;
	width: number;
	height: number;
	node: TreeNode;
	children: LaidOutNode[];
}

interface LayoutResult {
	root: LaidOutNode;
	width: number;
	height: number;
	all: LaidOutNode[];
	edges: Array<{ from: LaidOutNode; to: LaidOutNode }>;
}

const NODE_W = 240;
const NODE_H = 100;
const H_GAP = 48;
const V_GAP = 140;

function layoutTree(root: TreeNode, maxDepth: number | undefined, collapsed: Set<string>): LayoutResult {
	const all: LaidOutNode[] = [];
	const edges: Array<{ from: LaidOutNode; to: LaidOutNode }> = [];

	function walk(node: TreeNode, depth: number, path: string): { laid: LaidOutNode; width: number; height: number } {
		const id = node.id ?? path;
		const clamped = typeof maxDepth === 'number' ? depth >= maxDepth : false;
		const isCollapsed = collapsed.has(id);
		const rawChildren = node.children && node.children.length > 0 ? node.children : [];
		const childResults = !clamped && !isCollapsed && rawChildren.length > 0
			? rawChildren.map((c, idx) => walk(c, depth + 1, `${path}-${idx}`))
			: [];

		const childrenWidth = childResults.length > 0
			? childResults.reduce((sum, cr, idx) => sum + cr.width + (idx > 0 ? H_GAP : 0), 0)
			: 0;
		const subtreeWidth = Math.max(NODE_W, childrenWidth);
		const laid: LaidOutNode = {
			id,
			x: 0,
			y: depth * (NODE_H + V_GAP),
			width: NODE_W,
			height: NODE_H,
			node,
			children: childResults.map((cr) => cr.laid),
		};
		all.push(laid);
		return { laid, width: subtreeWidth, height: laid.y + NODE_H };
	}

	const built = walk(root, 0, '0');

	function assignX(laid: LaidOutNode): number {
		if (laid.children.length === 0) return NODE_W;
		const childWidths = laid.children.map(assignX);
		const totalChildrenWidth = childWidths.reduce((a, b) => a + b, 0) + H_GAP * (laid.children.length - 1);
		const subtreeWidth = Math.max(NODE_W, totalChildrenWidth);
		let xStart = laid.x - totalChildrenWidth / 2;
		for (let i = 0; i < laid.children.length; i++) {
			const c = laid.children[i];
			const cw = childWidths[i];
			c.x = xStart + cw / 2;
			xStart += cw + H_GAP;
			edges.push({ from: laid, to: c });
		}
		return subtreeWidth;
	}

	built.laid.x = 0;
	const totalWidth = assignX(built.laid);

	let minX = Infinity;
	let maxY = 0;
	for (const n of all) {
		if (n.x < minX) minX = n.x;
		if (n.y + n.height > maxY) maxY = n.y + n.height;
	}
	const PADDING = 24;
	const shift = PADDING - minX;
	for (const n of all) n.x += shift;
	const width = totalWidth + PADDING * 2;
	const height = maxY + PADDING;

	return { root: built.laid, width, height, all, edges };
}

function wrapText(text: string, maxChars: number): string[] {
	if (!text) return [];
	const words = text.split(/\s+/);
	const lines: string[] = [];
	let current = '';
	for (const w of words) {
		const tentative = current ? current + ' ' + w : w;
		if (tentative.length <= maxChars) {
			current = tentative;
		} else {
			if (current) lines.push(current);
			current = w;
		}
	}
	if (current) lines.push(current);
	return lines.slice(0, 3); // clamp to 3 lines to stay within height
}

function NodeBox({ n, onToggle, isCollapsed, hasChildren }: { n: LaidOutNode; onToggle: (id: string) => void; isCollapsed: boolean; hasChildren: boolean; }) {
	const title = n.node.thought || '—';
	const reason = n.node.reason || '';
	const scoreStr = typeof n.node.score === 'number' ? ` (${(n.node.score * 100) | 0}%)` : '';
	const titleLines = wrapText(title + scoreStr, 28);
	const reasonLines = wrapText(reason, 34);
	const handleClick = (e: React.MouseEvent) => {
		e.stopPropagation();
		if (hasChildren) onToggle(n.id);
	};
	return (
		<g className={`tg-node${hasChildren ? ' tg-collapsible' : ''}`} transform={`translate(${n.x - n.width / 2}, ${n.y})`} onClick={handleClick}>
			<rect rx={8} ry={8} width={n.width} height={n.height} />
			<title>{`${title}${scoreStr}\n${reason}`}</title>
			{titleLines.map((line, i) => (
				<text key={i} x={12} y={22 + i * 18} className="tg-node-title">{line}</text>
			))}
			{reasonLines.map((line, i) => (
				<text key={i} x={12} y={22 + titleLines.length * 18 + 10 + i * 16} className="tg-node-reason">{line}</text>
			))}
			{hasChildren && (
				<g className="tg-toggle" transform={`translate(${n.width - 24}, 8)`}>
					<rect width={16} height={16} rx={3} ry={3} />
					<text x={8} y={12} textAnchor="middle" className="tg-toggle-sign">{isCollapsed ? '+' : '−'}</text>
				</g>
			)}
		</g>
	);
}


export function TreeGraph({ tree, maxDepth }: TreeGraphProps) {
	const [collapsed, setCollapsed] = useState<Set<string>>(() => new Set());
	const [scale, setScale] = useState(1);
	const [tx, setTx] = useState(0);
	const [ty, setTy] = useState(0);
	const panning = useRef(false);
	const last = useRef<{ x: number; y: number } | null>(null);

	const layout = useMemo(() => layoutTree(tree, maxDepth, collapsed), [tree, maxDepth, collapsed]);

	const onWheel: React.WheelEventHandler<SVGSVGElement> = (e) => {
		e.preventDefault();
		const delta = e.deltaY;
		const next = clamp(scale * (delta > 0 ? 0.9 : 1.1), 0.5, 2.5);
		setScale(next);
	};

	const onMouseDown: React.MouseEventHandler<SVGSVGElement> = (e) => {
		panning.current = true;
		last.current = { x: e.clientX, y: e.clientY };
		(e.currentTarget as SVGSVGElement).classList.add('tg-panning');
	};
	const onMouseMove: React.MouseEventHandler<SVGSVGElement> = (e) => {
		if (!panning.current || !last.current) return;
		const dx = e.clientX - last.current.x;
		const dy = e.clientY - last.current.y;
		last.current = { x: e.clientX, y: e.clientY };
		setTx((t) => t + dx);
		setTy((t) => t + dy);
	};
	const endPan = (svg?: SVGSVGElement | null) => {
		panning.current = false;
		last.current = null;
		if (svg) svg.classList.remove('tg-panning');
	};
	const onMouseUp: React.MouseEventHandler<SVGSVGElement> = (e) => endPan(e.currentTarget as SVGSVGElement);
	const onMouseLeave: React.MouseEventHandler<SVGSVGElement> = (e) => endPan(e.currentTarget as SVGSVGElement);

	const toggle = (id: string) => {
		setCollapsed((prev) => {
			const n = new Set(prev);
			if (n.has(id)) n.delete(id); else n.add(id);
			return n;
		});
	};

	return (
		<div className="tot-graph">
			<svg
				className="tg-svg"
				viewBox={`0 0 ${Math.max(1, layout.width)} ${Math.max(1, layout.height)}`}
				width="100%"
				height="100%"
				preserveAspectRatio="xMidYMid meet"
				style={{ display: 'block' }}
				role="img"
				aria-label="Tree of Thought graph"
				onWheel={onWheel}
				onMouseDown={onMouseDown}
				onMouseMove={onMouseMove}
				onMouseUp={onMouseUp}
				onMouseLeave={onMouseLeave}
			>
				<g transform={`translate(${tx} ${ty}) scale(${scale})`}>
					<g className="tg-edges">
						{layout.edges.map((e, i) => (
							<path key={i} d={edgePath(e.from, e.to)} fill="none" />
						))}
					</g>
					<g className="tg-nodes">
						{layout.all.map((n) => (
							<NodeBox
								key={n.id}
								n={n}
								onToggle={toggle}
								isCollapsed={collapsed.has(n.id)}
								hasChildren={!!(n.node.children && n.node.children.length > 0)}
							/>
						))}
					</g>
				</g>
			</svg>
		</div>
	);
}

function edgePath(from: LaidOutNode, to: LaidOutNode): string {
	const x1 = from.x;
	const y1 = from.y + from.height;
	const x2 = to.x;
	const y2 = to.y;
	const dx = (x2 - x1) * 0.4;
	const c1x = x1 + dx;
	const c1y = y1 + 16;
	const c2x = x2 - dx;
	const c2y = y2 - 16;
	return `M ${x1} ${y1} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${x2} ${y2}`;
}

function clamp(v: number, min: number, max: number): number {
	return Math.max(min, Math.min(max, v));
}

export default TreeGraph; 