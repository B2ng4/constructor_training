<template>
	<q-dialog :model-value="modelValue" maximized @update:model-value="emit('update:modelValue', $event)">
		<q-card class="scenario-map-dialog column">
			<header class="scenario-map-dialog__header">
				<div class="scenario-map-dialog__heading">
					<div class="scenario-map-dialog__mark"><q-icon name="account_tree" size="22px" /></div>
					<div>
						<div class="scenario-map-dialog__title">Сценарий тренинга</div>
						<div class="scenario-map-dialog__subtitle">Соединяйте шаги и задавайте поведение каждой ветки</div>
					</div>
				</div>
				<div class="scenario-map-dialog__status" :class="{ 'scenario-map-dialog__status--warning': validation.warnings?.length }">
					<q-icon :name="validation.valid === false ? 'error_outline' : validation.warnings?.length ? 'warning_amber' : 'check_circle'" />
					{{ statusText }}
				</div>
				<q-space />
				<q-btn flat round icon="fit_screen" @click="canvasRef?.fitView?.()"><q-tooltip>Показать весь граф</q-tooltip></q-btn>
				<q-btn flat round icon="auto_fix_high" @click="resetLayout"><q-tooltip>Выровнять блоки автоматически</q-tooltip></q-btn>
				<q-btn unelevated no-caps color="primary" icon="save" label="Сохранить сценарий" :loading="saving" :disable="!dirty" class="scenario-map-dialog__save" @click="saveGraph" />
				<q-btn flat round icon="close" @click="requestClose" />
			</header>

			<div v-if="validation.errors?.length || validation.warnings?.length" class="scenario-map-dialog__issues">
				<span v-for="message in validation.errors" :key="message" class="scenario-issue scenario-issue--error">{{ message }}</span>
				<span v-for="message in validation.warnings" :key="message" class="scenario-issue">{{ message }}</span>
			</div>

			<main class="scenario-map-dialog__canvas">
				<q-inner-loading :showing="loading" color="primary" />
				<div v-if="!stepsArray.length && !loading" class="scenario-map-dialog__empty">
					<q-icon name="account_tree" size="58px" color="grey-5" />
					<div class="text-h6 q-mt-md">Сначала добавьте шаги</div>
					<p>После загрузки скриншотов здесь появится интерактивная блок-схема.</p>
				</div>
				<ScenarioMapCanvas
					v-else
					ref="canvasRef"
					:flow-id="flowId"
					v-model:nodes="nodes"
					v-model:edges="edges"
					@connect="onConnect"
					@node-drag-stop="onNodeDragStop"
					@edges-delete="onEdgesDelete"
				/>
			</main>
		</q-card>
	</q-dialog>

	<q-dialog v-model="transitionDialog" persistent>
		<q-card class="transition-dialog">
			<q-card-section class="transition-dialog__head">
				<div>
					<div class="transition-dialog__title">Настройка перехода</div>
					<div class="transition-dialog__route">{{ transitionRouteLabel }}</div>
				</div>
				<q-btn flat round dense icon="close" @click="cancelTransitionEdit" />
			</q-card-section>
			<q-card-section class="transition-dialog__body">
				<label class="field-label">Событие</label>
				<q-select v-model="transitionDraft.trigger_type" :options="triggerOptions" emit-value map-options outlined dense options-dense />
				<label class="field-label">Подпись на схеме</label>
				<q-input v-model="transitionDraft.label" outlined dense maxlength="120" placeholder="Например: Клиент — юрлицо" />
				<template v-if="transitionDraft.trigger_type === 'attempts_exceeded'">
					<label class="field-label">Количество ошибок</label>
					<q-input v-model.number="attemptsValue" type="number" min="1" outlined dense />
				</template>
				<template v-if="transitionDraft.trigger_type === 'condition'">
					<div class="condition-grid">
						<div><label class="field-label">Переменная</label><q-select v-model="conditionField" :options="conditionFields" emit-value map-options outlined dense /></div>
						<div><label class="field-label">Оператор</label><q-select v-model="conditionOperator" :options="operatorOptions" emit-value map-options outlined dense /></div>
					</div>
					<label class="field-label">Значение</label>
					<q-input v-model="conditionValue" outlined dense />
				</template>
				<div class="transition-default">
					<div><strong>Резервный переход</strong><span>Использовать, если другие условия не подошли</span></div>
					<q-toggle v-model="transitionDraft.is_default" color="primary" />
				</div>
			</q-card-section>
			<q-card-actions class="transition-dialog__actions">
				<q-btn v-if="editingTransitionIndex >= 0" flat no-caps color="negative" label="Удалить" @click="deleteEditedTransition" />
				<q-space />
				<q-btn flat no-caps label="Отмена" @click="cancelTransitionEdit" />
				<q-btn unelevated no-caps color="primary" label="Применить" @click="applyTransition" />
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useQuasar } from "quasar";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import ScenarioMapCanvas from "./ScenarioMapCanvas.vue";
import { buildScenarioGraph, createLinearTransitions, sortStepsByNumber, stepLabel, TRIGGER_META } from "@utils/scenarioMapLayout.js";

const props = defineProps({ modelValue: { type: Boolean, default: false } });
const emit = defineEmits(["update:modelValue"]);
const $q = useQuasar();
const store = useTrainingData();
const { steps, selectedStep, trainingData } = storeToRefs(store);
const api = new TrainingStepApi();
const flowId = "scenario-map-flow";
const canvasRef = ref(null);
const nodes = ref([]);
const edges = ref([]);
const nodePositions = ref({});
const transitions = ref([]);
const startStepId = ref(null);
const validation = ref({ valid: true, errors: [], warnings: [] });
const loading = ref(false);
const saving = ref(false);
const dirty = ref(false);
const transitionDialog = ref(false);
const transitionDraft = ref({});
const editingTransitionIndex = ref(-1);
const attemptsValue = ref(3);
const conditionField = ref("wrong_attempts");
const conditionOperator = ref(">=");
const conditionValue = ref(3);
const stepsArray = computed(() => sortStepsByNumber(steps.value || []));
const trainingUuid = computed(() => trainingData.value?.uuid || "");
const triggerOptions = Object.entries(TRIGGER_META).map(([value, meta]) => ({ value, label: meta.label }));
const conditionFields = [
	{ value: "wrong_attempts", label: "Количество ошибок" },
	{ value: "score", label: "Набранные баллы" },
	{ value: "selected_option", label: "Выбранный вариант" },
];
const operatorOptions = ["==", "!=", ">=", "<=", ">", "<"].map((value) => ({ value, label: value }));
const statusText = computed(() => validation.value.errors?.length ? "Есть ошибки" : validation.value.warnings?.length ? `${validation.value.warnings.length} замечания` : "Граф готов");
const transitionRouteLabel = computed(() => {
	const source = stepsArray.value.find((s) => s.id === transitionDraft.value.source_step_id);
	const target = stepsArray.value.find((s) => s.id === transitionDraft.value.target_step_id);
	return `${stepLabel(source)} → ${target ? stepLabel(target) : "Завершение"}`;
});

watch(() => props.modelValue, (open) => { if (open) void loadGraph(); });
watch(() => selectedStep.value?.id, () => { if (props.modelValue) rebuildGraph(); });

async function loadGraph() {
	if (!trainingUuid.value) return;
	loading.value = true;
	try {
		try {
			nodePositions.value = JSON.parse(localStorage.getItem(`scenario-layout:${trainingUuid.value}`) || "{}");
		} catch {
			nodePositions.value = {};
		}
		const { data } = await api.getScenarioGraph(trainingUuid.value);
		startStepId.value = data.start_step_id ?? stepsArray.value[0]?.id ?? null;
		transitions.value = data.transitions?.length ? data.transitions.map((x) => ({ ...x })) : createLinearTransitions(stepsArray.value);
		validation.value = data.validation || { valid: true, errors: [], warnings: [] };
		dirty.value = !data.transitions?.length && !!stepsArray.value.length;
		rebuildGraph();
		await nextTick();
		canvasRef.value?.fitView?.();
	} catch {
		$q.notify({ type: "negative", message: "Не удалось загрузить сценарий" });
	} finally { loading.value = false; }
}

function rebuildGraph() {
	const graph = buildScenarioGraph(stepsArray.value, { start_step_id: startStepId.value, transitions: transitions.value }, {
		selectedStepId: selectedStep.value?.id,
		onSelect: (step) => { store.selectStep(step); rebuildGraph(); },
		onDelete: null,
		onEditTransition: editTransition,
	});
	nodes.value = graph.nodes.map((node) => ({
		...node,
		position: nodePositions.value[node.id] || node.position,
	}));
	edges.value = graph.edges;
	validateLocal();
}

async function resetLayout() {
	nodePositions.value = {};
	localStorage.removeItem(`scenario-layout:${trainingUuid.value}`);
	rebuildGraph();
	await nextTick();
	canvasRef.value?.fitView?.();
}

function onNodeDragStop(event) {
	const node = event?.node;
	if (!node?.id || !node.position) return;
	nodePositions.value = {
		...nodePositions.value,
		[node.id]: { x: node.position.x, y: node.position.y },
	};
	localStorage.setItem(`scenario-layout:${trainingUuid.value}`, JSON.stringify(nodePositions.value));
}

function parseStepNodeId(id) { return id?.startsWith("step-") ? Number(id.slice(5)) : null; }
function onConnect(connection) {
	if (connection.source === "scenario-start") {
		const target = parseStepNodeId(connection.target);
		if (target) { startStepId.value = target; dirty.value = true; rebuildGraph(); }
		return;
	}
	const source = parseStepNodeId(connection.source);
	const target = connection.target === "scenario-finish" ? null : parseStepNodeId(connection.target);
	if (!source || connection.target === "scenario-start" || connection.source === "scenario-finish") return;
	transitionDraft.value = { source_step_id: source, target_step_id: target, trigger_type: "success", label: "", condition: null, priority: 0, is_default: false };
	editingTransitionIndex.value = -1;
	transitionDialog.value = true;
}
function editTransition(item) {
	const index = transitions.value.findIndex((x) => x === item || (x.id != null && x.id === item.id));
	if (index < 0) return;
	editingTransitionIndex.value = index;
	transitionDraft.value = { ...transitions.value[index] };
	attemptsValue.value = transitionDraft.value.condition?.value ?? 3;
	conditionField.value = transitionDraft.value.condition?.field ?? "wrong_attempts";
	conditionOperator.value = transitionDraft.value.condition?.operator ?? ">=";
	conditionValue.value = transitionDraft.value.condition?.value ?? 3;
	transitionDialog.value = true;
}
function applyTransition() {
	const item = { ...transitionDraft.value };
	if (item.trigger_type === "attempts_exceeded") item.condition = { field: "wrong_attempts", operator: ">=", value: Number(attemptsValue.value) || 1 };
	else if (item.trigger_type === "condition") item.condition = { field: conditionField.value, operator: conditionOperator.value, value: conditionValue.value };
	else item.condition = null;
	if (editingTransitionIndex.value >= 0) transitions.value.splice(editingTransitionIndex.value, 1, item);
	else transitions.value.push(item);
	dirty.value = true;
	transitionDialog.value = false;
	rebuildGraph();
}
function cancelTransitionEdit() { transitionDialog.value = false; }
function deleteEditedTransition() {
	if (editingTransitionIndex.value >= 0) transitions.value.splice(editingTransitionIndex.value, 1);
	dirty.value = true;
	transitionDialog.value = false;
	rebuildGraph();
}
function onEdgesDelete(deleted) {
	const ids = new Set(deleted.map((edge) => edge.data?.transition?.id).filter((id) => id != null));
	const refs = new Set(deleted.map((edge) => edge.data?.transition).filter(Boolean));
	transitions.value = transitions.value.filter((item) => !refs.has(item) && !ids.has(item.id));
	dirty.value = true;
	rebuildGraph();
}
function validateLocal() {
	const warnings = [];
	const errors = [];
	if (stepsArray.value.length && !startStepId.value) errors.push("Не выбран стартовый шаг");
	const outgoing = new Set(transitions.value.map((x) => x.source_step_id));
	const dead = stepsArray.value.filter((s) => !outgoing.has(s.id));
	if (dead.length) warnings.push(`${dead.length} шаг(а) не имеют исходящего перехода`);
	validation.value = { valid: !errors.length, errors, warnings };
}
async function saveGraph() {
	saving.value = true;
	try {
		const payload = {
			start_step_id: startStepId.value,
			transitions: transitions.value.map(({ source_step_id, target_step_id, trigger_type, label, condition, priority, is_default }) => ({ source_step_id, target_step_id, trigger_type, label: label || null, condition, priority: priority || 0, is_default: !!is_default })),
		};
		const { data } = await api.saveScenarioGraph(trainingUuid.value, payload);
		transitions.value = data.transitions.map((x) => ({ ...x }));
		validation.value = data.validation;
		dirty.value = false;
		rebuildGraph();
		$q.notify({ type: "positive", message: "Сценарий сохранён", position: "bottom-right" });
	} catch (error) {
		const detail = error?.response?.data?.detail;
		validation.value = typeof detail === "object" ? detail : validation.value;
		$q.notify({ type: "negative", message: "Не удалось сохранить сценарий" });
	} finally { saving.value = false; }
}
function requestClose() {
	if (!dirty.value) { emit("update:modelValue", false); return; }
	$q.dialog({ title: "Есть несохранённые изменения", message: "Закрыть карту и потерять изменения?", cancel: "Остаться", ok: { label: "Закрыть", color: "negative", flat: true } }).onOk(() => emit("update:modelValue", false));
}
</script>

<style scoped>
.scenario-map-dialog { width: 100%; height: 100%; background: #f4f7fb; }
.scenario-map-dialog__header { min-height: 76px; display: flex; align-items: center; gap: 14px; padding: 12px 18px; background: rgba(255,255,255,.94); border-bottom: 1px solid rgba(15,23,42,.08); backdrop-filter: blur(18px); }
.scenario-map-dialog__heading { display: flex; align-items: center; gap: 12px; }
.scenario-map-dialog__mark { width: 42px; height: 42px; display: grid; place-items: center; border-radius: 13px; color: #5064f7; background: rgba(80,100,247,.11); }
.scenario-map-dialog__title { color: #0f172a; font-size: 17px; font-weight: 760; }
.scenario-map-dialog__subtitle { color: #64748b; font-size: 12px; }
.scenario-map-dialog__status { display: flex; align-items: center; gap: 6px; padding: 7px 10px; border-radius: 10px; background: rgba(34,197,94,.1); color: #15803d; font-size: 12px; font-weight: 650; }
.scenario-map-dialog__status--warning { background: rgba(245,158,11,.11); color: #b45309; }
.scenario-map-dialog__save { border-radius: 12px; padding: 8px 16px; }
.scenario-map-dialog__issues { display: flex; gap: 8px; padding: 8px 18px; background: rgba(255,255,255,.76); border-bottom: 1px solid rgba(15,23,42,.06); overflow-x: auto; }
.scenario-issue { flex: 0 0 auto; padding: 5px 9px; border-radius: 8px; background: rgba(245,158,11,.1); color: #a16207; font-size: 11px; font-weight: 600; }
.scenario-issue--error { background: rgba(239,68,68,.1); color: #dc2626; }
.scenario-map-dialog__canvas { position: relative; flex: 1; min-height: 0; overflow: hidden; }
.scenario-map-dialog__empty { height: 100%; display: grid; place-content: center; justify-items: center; color: #64748b; text-align: center; }
.transition-dialog { width: 520px; max-width: 94vw; border-radius: 20px; }
.transition-dialog__head { display: flex; justify-content: space-between; gap: 16px; border-bottom: 1px solid rgba(15,23,42,.07); }
.transition-dialog__title { font-size: 18px; font-weight: 750; color: #0f172a; }
.transition-dialog__route { margin-top: 3px; color: #64748b; font-size: 12px; }
.transition-dialog__body { display: grid; gap: 9px; padding: 20px 24px; }
.field-label { margin-top: 6px; color: #475569; font-size: 12px; font-weight: 650; }
.condition-grid { display: grid; grid-template-columns: 1fr 120px; gap: 10px; }
.condition-grid > div { display: grid; gap: 8px; }
.transition-default { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; padding: 13px 14px; border: 1px solid rgba(15,23,42,.08); border-radius: 13px; }
.transition-default strong, .transition-default span { display: block; }
.transition-default strong { color: #0f172a; font-size: 13px; }
.transition-default span { color: #64748b; font-size: 11px; }
.transition-dialog__actions { padding: 14px 20px; border-top: 1px solid rgba(15,23,42,.07); }
:global(body.body--dark) .scenario-map-dialog { background: #0b1220; }
:global(body.body--dark) .scenario-map-dialog__header, :global(body.body--dark) .scenario-map-dialog__issues { background: rgba(17,24,39,.94); border-color: rgba(148,163,184,.14); }
:global(body.body--dark) .scenario-map-dialog__title, :global(body.body--dark) .transition-dialog__title, :global(body.body--dark) .transition-default strong { color: #f1f5f9; }
:global(body.body--dark) .transition-default { border-color: rgba(148,163,184,.16); }

@media (max-width: 900px) {
	.scenario-map-dialog__header { min-height: 68px; padding: 10px 12px; gap: 6px; }
	.scenario-map-dialog__subtitle, .scenario-map-dialog__status { display: none; }
	.scenario-map-dialog__mark { width: 38px; height: 38px; }
	.scenario-map-dialog__save { min-width: 42px; padding: 8px; }
	.scenario-map-dialog__save :deep(.q-btn__content span) { display: none; }
}
</style>
