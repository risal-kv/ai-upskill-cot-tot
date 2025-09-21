import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Board from './Board';
import ReasoningPanel from './Reasoning/ReasoningPanel';
import { applyMove, createEmptyBoard, evaluateBoard, getNextPlayer } from '../lib/game';
import type { AiResponse, Board as BoardType, Mode, Player } from '../types';
import { requestAiMove } from '../lib/api';

interface GameProps {
	initialMode?: Mode;
	startingPlayer?: Player; // human player's mark; AI will be the other mark
}

const STORAGE_KEY = 'ttt_game_state_v1';

export function Game({ initialMode = 'cot', startingPlayer = 'X' }: GameProps) {
	const loadSaved = () => {
		try {
			const raw = sessionStorage.getItem(STORAGE_KEY);
			return raw ? (JSON.parse(raw) as { board?: BoardType; mode?: Mode; human?: Player; aiResponse?: AiResponse | null; cotHistory?: string[] }) : null;
		} catch {
			return null;
		}
	};
	const saved = loadSaved();

	const [board, setBoard] = useState<BoardType>(() => saved?.board ?? createEmptyBoard());
	const [mode, setMode] = useState<Mode>(() => saved?.mode ?? initialMode);
	const [human, setHuman] = useState<Player>(() => saved?.human ?? startingPlayer);
	const ai = useMemo<Player>(() => (human === 'X' ? 'O' : 'X'), [human]);
	const [aiResponse, setAiResponse] = useState<AiResponse | null>(() => saved?.aiResponse ?? null);
	const [cotHistory, setCotHistory] = useState<string[]>(() => saved?.cotHistory ?? []);
	const [loading, setLoading] = useState(false);
	const abortRef = useRef<AbortController | null>(null);

	// Persist on relevant changes
	useEffect(() => {
		try {
			sessionStorage.setItem(
				STORAGE_KEY,
				JSON.stringify({ board, mode, human, aiResponse, cotHistory })
			);
		} catch {
			// ignore
		}
	}, [board, mode, human, aiResponse, cotHistory]);

	const status = useMemo(() => {
		const e = evaluateBoard(board);
		if (e.winner) return `${e.winner} wins`;
		if (e.isDraw) return 'Draw';
		return `${getNextPlayer(board)} to move`;
	}, [board]);

	const reset = useCallback(() => {
		if (abortRef.current) abortRef.current.abort();
		setBoard(createEmptyBoard());
		setAiResponse(null);
		setCotHistory([]);
		setLoading(false);
		try { sessionStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }
	}, []);

	const onCellClick = useCallback(
		(idx: number) => {
			if (loading) return;
			const { winner, isDraw } = evaluateBoard(board);
			if (winner || isDraw) return;
			const current = getNextPlayer(board, 'X');
			if (current !== human) return; // not human turn
			if (board[idx] !== null) return;

			const next = applyMove(board, idx, human);
			setBoard(next);
		},
		[board, human, loading]
	);

	// Trigger AI move when it's AI's turn
	useEffect(() => {
		const { winner, isDraw } = evaluateBoard(board);
		if (winner || isDraw) return;
		const current = getNextPlayer(board, 'X');
		if (current !== ai) return;

		setLoading(true);
		const ac = new AbortController();
		abortRef.current = ac;
		requestAiMove({ board, player: ai, mode, abortSignal: ac.signal })
			.then((resp) => {
				setAiResponse(resp);
				if (resp.mode === 'cot' && resp.reasoning) {
					setCotHistory((h) => [...h, resp.reasoning]);
				}
				if (typeof resp.move === 'number') {
					setBoard((b) => applyMove(b, resp.move, ai));
				}
			})
			.catch((err) => {
				console.error(err);
			})
			.finally(() => {
				setLoading(false);
				abortRef.current = null;
			});
	}, [board, ai, mode]);

	const canStartAi = useMemo(() => {
		return getNextPlayer(board, 'X') === ai;
	}, [board, ai]);

	return (
		<div className="game-layout">
			<header className="controls">
				<div className="row">
					<label>
						Mode:
						<select value={mode} onChange={(e) => setMode(e.target.value as Mode)} disabled={loading}>
							<option value="cot">CoT</option>
							<option value="tot">ToT</option>
						</select>
					</label>
					<label>
						Human:
						<select value={human} onChange={(e) => setHuman(e.target.value as Player)} disabled={loading}>
							<option value="X">X</option>
							<option value="O">O</option>
						</select>
					</label>
					<button onClick={reset} disabled={loading}>Reset</button>
				</div>
				<div className="row status">
					<strong>Status:</strong> {status}
				</div>
			</header>
			<main className="content">
				<section className="board-section">
					<div className="board-title">Tic Tac Toe</div>
					<Board board={board} onCellClick={onCellClick} disabled={loading} />
					{loading && <div className="loading">AI thinking…</div>}
					{canStartAi && !loading && (
						<button className="ai-move" onClick={() => setBoard((b) => b)}>
							Request AI Move
						</button>
					)}
				</section>
				<aside className="reasoning-section">
					<ReasoningPanel response={aiResponse} cotHistory={cotHistory} />
				</aside>
			</main>
		</div>
	);
}

export default Game; 