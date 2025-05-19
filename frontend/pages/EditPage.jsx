import { useParams } from "react-router";

function EditPage() {
	const { uuid } = useParams();

	return (
		<p className="read-the-docs">
			Editing training with UUID: {uuid}
		</p>
	);
}

export default EditPage;