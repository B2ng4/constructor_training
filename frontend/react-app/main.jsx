import { createRoot } from 'react-dom/client';
import EditPage from '@pages/EditPage';
import { BrowserRouter, Routes, Route } from "react-router";

createRoot(document.getElementById('react-app')).render(
		<BrowserRouter>
			<Routes>
				<Route path="/training/edit/:uuid" element={<EditPage />} />
			</Routes>
		</BrowserRouter>
);
