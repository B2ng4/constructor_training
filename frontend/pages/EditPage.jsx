import { useParams } from "react-router";
import axios from "axios";
import { useEffect, useState } from "react";
import 'tldraw/tldraw.css';
import CustomTldraw from "@components/for_pages/EditPage/EditPageCustomTldraw.jsx";

//Получаем тренинг
async function getTrainings(uuid) {
	let result = await axios.get(`${__BASE__URL__}/training/` + uuid);
	try {
		return result.data;
	} catch (error) {
		return error;
	}
}

function EditPage() {
	const { uuid } = useParams();
	const [dataTraining, setDataTraining] = useState(null);
	const [isLoading, setIsLoading] = useState(true);
	useEffect(() => {
		async function fetchData() {
			const data = await getTrainings(uuid);
			setDataTraining(data);
			setIsLoading(false);

		}
		fetchData();
	}, [uuid]);
	if (isLoading) return <div>Loading...</div>;
	return (
		<>
			<div style={{ position: 'fixed', inset: 0 }}>
				<CustomTldraw training={dataTraining} />
			</div>
		</>
	);
}

export default EditPage;