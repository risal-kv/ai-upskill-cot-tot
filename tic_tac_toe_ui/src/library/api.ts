import type { AiResponse, Board, Mode, TreeNode } from '../types';

interface RequestArgs {
	board: Board;
	player: 'X' | 'O';
	mode: Mode;
	beam?: number;
	depth?: number;
	abortSignal?: AbortSignal;
}

export async function requestAiMove({ board, player, mode, beam, depth, abortSignal }: RequestArgs): Promise<AiResponse> {
	const baseUrl = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
	const payload = {
		mode,
		player,
		board: board.map((c) => (c === null ? null : c)),
		beam,
		depth,
	};
	const res = await fetch(`${baseUrl.replace(/\/$/, '')}/api/v1/move`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload),
		signal: abortSignal,
	});
	if (!res.ok) throw new Error(await res.text());
	const data = await res.json();
	if (data.mode === 'cot') {
		return { mode: 'cot', move: data.move, reasoning: data.reasoning ?? '' };
	}
	return { mode: 'tot', move: data.move, reasoning: data.reasoning ?? '', tree: data.tree as TreeNode };
} 