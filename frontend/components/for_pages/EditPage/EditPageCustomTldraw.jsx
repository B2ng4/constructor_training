import { Tldraw, useEditor } from 'tldraw';
import { useEffect } from 'react';

function PageManager(props) {
	const editor = useEditor()

	useEffect(() => {
		if (!editor) return
		props.training.steps.forEach((step) => {
			editor.createPage({id: `page:${step.id}`});
		})
		editor.setCurrentPage('page:1')
	}, [editor])

	return null
}

function CustomTldraw(props) {
	return (
		<Tldraw>
			<PageManager training={props.training} />
		</Tldraw>
	)
}

export default CustomTldraw;