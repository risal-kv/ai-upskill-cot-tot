import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import TreeGraph from './TreeGraph';
import type { TreeNode } from '../../types';

function useQueryKey(defaultKey: string) {
	const { search } = useLocation();
	const params = new URLSearchParams(search);
	return params.get('key') || defaultKey;
}

export function GraphPage() {
	const navigate = useNavigate();
	const { state } = useLocation() as { state?: { key?: string } };
	const stateKey = state?.key || 'tot_tree';
	const key = useQueryKey(stateKey);
	const [tree, setTree] = useState<TreeNode | null>(null);

	useEffect(() => {
		try {
			const rawLS = localStorage.getItem(key);
			const rawSS = sessionStorage.getItem(key);
			const raw = rawLS || rawSS;
			if (raw) setTree(JSON.parse(raw));
		} catch {
			// ignore
		}
	}, [key]);

	if (!tree) {
		return (
			<div style={{ minHeight: '100vh', padding: 16 }}>
				<div style={{ marginBottom: 12 }}>
					<Link to="/">← Back</Link>
				</div>
				<p>No tree available. Go back and generate a ToT response.</p>
			</div>
		);
	}

	return (
		<div style={{ minHeight: '100vh', height: '100vh', width: '100vw', margin: 0, padding: 0 }}>
			<button
				style={{ position: 'fixed', top: 12, left: 12, zIndex: 10 }}
				onClick={() => navigate(-1)}
			>
				← Back
			</button>
			<div style={{ height: '100%', width: '100%' }}>
				<TreeGraph tree={tree} />
			</div>
		</div>
	);
}

export default GraphPage; 