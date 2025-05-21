import { useParams } from "react-router";
import axios from "axios";
import { useEffect, useState } from "react";
import BaseCanvas from "@components/for_pages/EditPage/EditPageBaseCanvas.jsx"

/*
 Метод получения данных тренинга
*/
async function getTrainings(uuid) {
	let result = await axios.get(`${__BASE__URL__}/training/` + uuid);
	try {
		return result.data;
	} catch (error) {
		return error;
	}
}
/*
 Страница EditPage()
*/
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
				<BaseCanvas props={dataTraining} />
		</>
	);
}

export default EditPage;