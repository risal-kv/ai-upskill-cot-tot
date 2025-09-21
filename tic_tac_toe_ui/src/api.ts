import type { AiResponse, Board, Mode, TreeNode } from './types';

export interface MoveRequest {
	mode: Mode;
	board: (null | 'X' | 'O')[]; // 9 cells
	toMove?: 'O';
	beam?: number;
	depth?: number;
}

export async function requestAiMove(baseUrl: string, req: MoveRequest): Promise<AiResponse> {
	const res = await fetch(`${baseUrl.replace(/\/$/, '')}/api/v1/move`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(req),
	});
	if (!res.ok) {
		const text = await res.text();
		throw new Error(text || `HTTP ${res.status}`);
	}
	const data = await res.json();
	// Backend returns { mode, move (0..8), reasoning, tree? }
	if (data.mode === 'cot') {
		return {
			mode: 'cot',
			move: data.move,
			reasoning: data.reasoning ?? '',
		};
	}
	// tot
	return {
		mode: 'tot',
		move: data.move,
		reasoning: data.reasoning ?? '',
		tree: data.tree as TreeNode,
	};
}

export function boardToPayload(board: Board): (null | 'X' | 'O')[] {
	// UI Board is 1D 9-length array of CellValue (null|'X'|'O')
	if (board.length !== 9) throw new Error('Board must have 9 cells');
	return board.map((c) => (c === null ? null : c));
} 