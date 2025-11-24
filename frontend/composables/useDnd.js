import { ref } from "vue";

export default function useDnd() {
	const files = ref([]);

	const dnd = (event) => {
		files.value = event.dataTransfer.files;
	};

	return [files, dnd];
}
