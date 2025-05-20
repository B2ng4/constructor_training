import { Tldraw, useEditor } from 'tldraw';
import { useEffect, useState } from 'react';

//Отрисовка шагов
function Steps(props) {
	const editor = useEditor()
	useEffect(() => {
		if (!editor) return
		props.training.steps.forEach((step) => {
			editor.createPage({id: `page:${step.id}`, name: String(step.id), meta: {data: step}});
		})
		//создается стандартная страница библы
		editor.deletePage('page:page')
	}, [editor])
	return null;
}

function getTraining(training) {
	const [selectedTraining, setSelectedTraining] = useState(null);
	setSelectedTraining(training);
	return selectedTraining;
}

function CustomTldraw(props) {
	return (
		<Tldraw>
			<Steps training={props.training} />
		</Tldraw>
	);
}

export default CustomTldraw;