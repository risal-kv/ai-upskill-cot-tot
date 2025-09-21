import './App.css'
import { Routes, Route, useLocation } from 'react-router-dom'
import { Game } from './components/Game'
import { GraphPage } from './components/Reasoning/GraphPage'

function App() {
	const { pathname } = useLocation();
	return (
		<div className="app">
			{pathname === '/' && <h1>Tic Tac Toe (AI)</h1>}
			<Routes>
				<Route path="/" element={<Game />} />
				<Route path="/graph" element={<GraphPage />} />
			</Routes>
		</div>
	)
}

export default App
