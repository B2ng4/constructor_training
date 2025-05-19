import { useParams } from "react-router";
import { Excalidraw } from "@excalidraw/excalidraw";

function EditPage() {
	const { uuid } = useParams();

	return (
		<>
		<div style={{ height: "900px" }}>
			<Excalidraw />
		</div>
		</>
	);
}

export default EditPage;