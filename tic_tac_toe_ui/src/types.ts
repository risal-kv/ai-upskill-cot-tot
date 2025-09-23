export type Player = 'X' | 'O';

export type CellValue = Player | null;

// Board is a 1D array of 9 cells [0..8]
export type Board = CellValue[];

export type Mode = 'cot' | 'tot';

export interface CotResponse {
	mode: 'cot';
	move: number; // 0..8 index chosen by AI
	reasoning: string; // chain-of-thought style explanation (from backend)
}

export interface TreeNode {
	id?: string;
	thought: string; // short statement/thought at this node
	reason: string; // justification for taking this branch
	score?: number; // optional score/heuristic
	children?: TreeNode[];
}

export interface TotResponse {
	mode: 'tot';
	move: number; // 0..8 index chosen by AI
	reasoning: string; // overall ToT summary reasoning
	tree: TreeNode; // full tree-of-thought structure
}

export type AiResponse = CotResponse | TotResponse;

export interface EvaluationResult {
	winner: Player | null;
	isDraw: boolean;
} 