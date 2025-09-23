import type { Board, CellValue, EvaluationResult, Player } from '../types';

const WIN_LINES: number[][] = [
	[0, 1, 2],
	[3, 4, 5],
	[6, 7, 8],
	[0, 3, 6],
	[1, 4, 7],
	[2, 5, 8],
	[0, 4, 8],
	[2, 4, 6],
];

export function createEmptyBoard(): Board {
	return Array<CellValue>(9).fill(null);
}

export function calculateWinner(board: Board): Player | null {
	for (const [a, b, c] of WIN_LINES) {
		const v = board[a];
		if (v && v === board[b] && v === board[c]) return v;
	}
	return null;
}

export function isBoardFull(board: Board): boolean {
	return board.every((c) => c !== null);
}

export function evaluateBoard(board: Board): EvaluationResult {
	const winner = calculateWinner(board);
	if (winner) return { winner, isDraw: false };
	if (isBoardFull(board)) return { winner: null, isDraw: true };
	return { winner: null, isDraw: false };
}

export function getAvailableMoves(board: Board): number[] {
	const moves: number[] = [];
	for (let i = 0; i < board.length; i++) if (board[i] === null) moves.push(i);
	return moves;
}

export function countMarks(board: Board): { x: number; o: number } {
	let x = 0;
	let o = 0;
	for (const c of board) {
		if (c === 'X') x++;
		if (c === 'O') o++;
	}
	return { x, o };
}

// Determine next player assuming X starts.
export function getNextPlayer(board: Board, startingPlayer: Player = 'X'): Player {
	const { x, o } = countMarks(board);
	if (startingPlayer === 'X') {
		return x === o ? 'X' : 'O';
	} else {
		return x === o ? 'O' : 'X';
	}
}

export function applyMove(board: Board, index: number, player: Player): Board {
	if (index < 0 || index > 8) return board;
	if (board[index] !== null) return board;
	const next = board.slice();
	next[index] = player;
	return next;
} 