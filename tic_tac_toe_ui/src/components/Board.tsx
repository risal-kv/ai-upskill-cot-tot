import type { Board as BoardType } from '../types';

interface BoardProps {
	board: BoardType;
	onCellClick?: (index: number) => void;
	disabled?: boolean;
}

export function Board({ board, onCellClick, disabled }: BoardProps) {
	return (
		<div className="ttt-board">
			{board.map((cell, idx) => {
				const isClickable = !disabled && cell === null;
				return (
					<button
						key={idx}
						className={`ttt-cell${isClickable ? ' clickable' : ''}`}
						onClick={() => isClickable && onCellClick && onCellClick(idx)}
						aria-label={`cell-${idx}`}
					>
						{cell ?? ''}
					</button>
				);
			})}
		</div>
	);
}

export default Board; 