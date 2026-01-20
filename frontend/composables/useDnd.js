import { ref } from "vue";

export default function useDnd() {
	const files = ref([]);

	const dnd = (event) => {
		files.value = [...event.dataTransfer.files].map((item, index) => {
			return {
				id: index,
				name: item.name,
				url: URL.createObjectURL(item),
				size: item.size,
				originalFile: item,
			};
		});
	};

	return [files, dnd];
}
