import { useParams } from "react-router";
import { Excalidraw } from "@excalidraw/excalidraw";
import axios from "axios";
import { useEffect, useState } from "react";

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

	useEffect(() => {
		async function fetchData() {
			const data = await getTrainings(uuid);
			setDataTraining(data);
		}
		fetchData();
	}, [uuid]);
	return (
		<>
			<h1>{dataTraining?.title}</h1>
		<div style={{ height: "900px" }}>
			<Excalidraw/>
		</div>
		</>
	);
}

export default EditPage;