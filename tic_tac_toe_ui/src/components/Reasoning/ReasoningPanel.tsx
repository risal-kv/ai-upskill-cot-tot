import type { AiResponse } from '../../types';
import TreeNodeView from './TreeNodeView';
import TreeGraph from './TreeGraph';
import { useNavigate } from 'react-router-dom';

interface ReasoningPanelProps {
	response: AiResponse | null;
	cotHistory?: string[];
}

export function ReasoningPanel({ response, cotHistory }: ReasoningPanelProps) {
	const navigate = useNavigate();
	if (!response) return null;

	if (response.mode === 'cot') {
		const items = (cotHistory && cotHistory.length > 0)
			? cotHistory
			: (response.reasoning ? [response.reasoning] : []);
		return (
			<section className="reasoning-panel">
				<h3>AI Reasoning (CoT)</h3>
				<pre className="reasoning-text">{items.join('\n\n')}</pre>
			</section>
		);
	}

	const openFullScreen = () => {
		if ('tree' in response && response.tree) {
			const key = 'tot_tree';
			try {
				// store for same-tab navigation and cross-tab
				sessionStorage.setItem(key, JSON.stringify(response.tree));
				localStorage.setItem(key, JSON.stringify(response.tree));
				const url = `${window.location.origin}/graph?key=${encodeURIComponent(key)}`;
				window.open(url, '_blank', 'noopener');
			} catch {
				// fallback to same-tab navigation
				navigate('/graph', { state: { key: 'tot_tree' } });
			}
		}
	};

	return (
		<section className="reasoning-panel">
			<h3>AI Reasoning (ToT)</h3>
			{response.reasoning && (
				<pre className="reasoning-text">{response.reasoning}</pre>
			)}
			{'tree' in response && response.tree && (
				<>
					<div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
						<button onClick={openFullScreen}>Open full-screen graph</button>
					</div>
					<div className="tot-graph-wrap" style={{ maxHeight: 320, overflow: 'hidden' }}>
						<TreeGraph tree={response.tree} />
					</div>
					<div className="tot-tree" style={{ display: 'none' }}>
						<TreeNodeView node={response.tree} />
					</div>
				</>
			)}
		</section>
	);
}

export default ReasoningPanel; 