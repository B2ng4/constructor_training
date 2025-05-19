import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import EditPage from '@pages/EditPage';
import { BrowserRouter, Routes, Route } from "react-router";
import "@excalidraw/excalidraw/index.css";

createRoot(document.getElementById('react-app')).render(
	<StrictMode>
		<BrowserRouter>
			<Routes>
				<Route path="/training/edit/:uuid" element={<EditPage />} />
			</Routes>
		</BrowserRouter>
	</StrictMode>
);
