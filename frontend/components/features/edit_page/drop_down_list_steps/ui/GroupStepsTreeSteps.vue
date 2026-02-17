<template>
	<Tree :key="stepsKey" :data="stepsArray" item-key="id" nesting-key="steps" v-slot="{ item }">
		<div
			@click="store.selectStep(item)"
			class="tree-item-content cursor-pointer"
			:class="{ active: item.id === store.selectedStep?.id }"
		>
			<span>{{ item.meta?.name ?? "Шаг без названия" }}</span>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="delete_outline"
				color="grey-7"
				class="delete-btn"
				@click.stop="confirmDelete(item)"
			>
				<q-tooltip>Удалить шаг</q-tooltip>
			</q-btn>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from "@components/vue_dnd_kit_components/tree";
import { watchDebounced } from "@vueuse/core";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi, TrainingApi } from "@api";
import { computed, ref } from "vue";
import { useQuasar } from "quasar";

const $q = useQuasar();
const store = useTrainingData();
const { steps } = storeToRefs(store);
const api = new TrainingStepApi();
const trainingApi = new TrainingApi();

const stepsArray = computed(() => Array.isArray(steps.value) ? steps.value : []);
const stepsKey = computed(() => stepsArray.value.map((s) => s.id).join(",") || "empty");

const changeSteps = computed(() => {
	return stepsArray.value.map((el, index) => {
		return {
			id: el.id,
			step_number: index + 1
		};
	});
});

const skipReorderRef = ref(false);

watchDebounced(
	stepsArray,
	async () => {
		if (skipReorderRef.value) return;
		await api.reorderSteps(store.trainingData.uuid, { steps: changeSteps.value });
		$q.notify({
			color: 'positive',
			message: 'Порядок изменен',
			position: 'bottom-right',
		});
	},
	{ debounce: 500, maxWait: 1000, deep: true },
);

function confirmDelete(step) {
	const stepName = step.meta?.name ?? "Шаг без названия";
	$q.dialog({
		title: "Удалить шаг?",
		message: `Шаг «${stepName}» будет удалён без возможности восстановления.`,
		cancel: { label: "Отмена", flat: true },
		ok: { label: "Удалить", color: "negative", flat: true },
		persistent: true,
	}).onOk(async () => {
		await deleteStep(step.id);
	});
}

async function deleteStep(stepId) {
	try {
		skipReorderRef.value = true;
		await api.deleteStep(store.trainingData.uuid, stepId);
		const { data } = await trainingApi.getTrainingByUuid(store.trainingData.uuid);
		store.setTrainingData(data);
		$q.notify({
			color: "positive",
			message: "Шаг удалён",
			position: "bottom-right",
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось удалить шаг",
			position: "top",
		});
	} finally {
		skipReorderRef.value = false;
	}
}
</script>

<style scoped>
.tree-item-content {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 6px 10px;
	flex: 1;
	border-radius: 8px;
	transition: background-color 0.15s ease;
}

.tree-item-content:hover {
	background-color: rgba(0, 0, 0, 0.04);
}

.tree-item-content .delete-btn {
	opacity: 0;
	margin-left: auto;
	transition: opacity 0.15s ease;
}

.tree-item-content:hover .delete-btn {
	opacity: 0.6;
}

.tree-item-content:hover .delete-btn:hover {
	opacity: 1;
}

.tree-item-content.active .delete-btn {
	opacity: 0.6;
}

.active {
	background-color: rgba(80, 100, 247, 0.1);
	border-radius: 8px;
}

.active:hover {
	background-color: rgba(80, 100, 247, 0.16);
}

.tree-item-content span {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	font-size: 13px;
}
</style>
