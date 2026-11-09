import { MarkerType } from "@vue-flow/core";

export const SCENARIO_NODE_WIDTH = 224;
export const SCENARIO_NODE_HEIGHT = 198;
export const SCENARIO_NODE_GAP_X = 150;
export const SCENARIO_NODE_GAP_Y = 86;

export const TRIGGER_META = {
	success: { label: "Успешное действие", color: "#22c55e" },
	error: { label: "Ошибка", color: "#ef4444" },
	attempts_exceeded: { label: "Превышены попытки", color: "#f59e0b" },
	choice: { label: "Выбор пользователя", color: "#3b82f6" },
	condition: { label: "Условие", color: "#a855f7" },
	default: { label: "По умолчанию", color: "#64748b" },
};

export function sortStepsByNumber(steps) {
	return [...(steps || [])].sort(
		(a, b) => (a.step_number ?? 0) - (b.step_number ?? 0),
	);
}

export function createLinearTransitions(steps) {
	const sorted = sortStepsByNumber(steps);
	return sorted.map((step, index) => ({
		id: `draft-${step.id}`,
		source_step_id: step.id,
		target_step_id: sorted[index + 1]?.id ?? null,
		trigger_type: "success",
		label: null,
		condition: null,
		priority: 0,
		is_default: false,
	}));
}

function graphPositions(steps, transitions, startStepId) {
	const ids = new Set(steps.map((step) => step.id));
	const outgoing = new Map(steps.map((step) => [step.id, []]));
	for (const edge of transitions) {
		if (edge.target_step_id != null && ids.has(edge.target_step_id)) {
			outgoing.get(edge.source_step_id)?.push(edge.target_step_id);
		}
	}
	const levels = new Map();
	const queue = startStepId != null ? [[startStepId, 0]] : [];
	while (queue.length) {
		const [id, level] = queue.shift();
		if (!ids.has(id) || (levels.has(id) && levels.get(id) <= level)) continue;
		levels.set(id, level);
		for (const target of outgoing.get(id) || []) queue.push([target, level + 1]);
	}
	let fallbackLevel = Math.max(0, ...levels.values()) + 1;
	for (const step of sortStepsByNumber(steps)) {
		if (!levels.has(step.id)) levels.set(step.id, fallbackLevel++);
	}
	const rows = new Map();
	const positions = new Map();
	for (const step of steps) {
		const level = levels.get(step.id) ?? 0;
		const row = rows.get(level) || 0;
		rows.set(level, row + 1);
		positions.set(step.id, {
			x: 110 + level * (SCENARIO_NODE_WIDTH + SCENARIO_NODE_GAP_X),
			y: 80 + row * (SCENARIO_NODE_HEIGHT + SCENARIO_NODE_GAP_Y),
		});
	}
	return positions;
}

export function buildScenarioGraph(steps, scenario = {}, callbacks = {}) {
	const sorted = sortStepsByNumber(steps);
	const transitions = scenario.transitions?.length
		? scenario.transitions
		: createLinearTransitions(sorted);
	const startStepId = scenario.start_step_id ?? sorted[0]?.id ?? null;
	const positions = graphPositions(sorted, transitions, startStepId);
	const nodes = [
		{
			id: "scenario-start",
			type: "terminal",
			position: { x: -190, y: 100 },
			draggable: false,
			data: { kind: "start", label: "Старт" },
		},
		...sorted.map((step) => ({
			id: `step-${step.id}`,
			type: "step",
			position: positions.get(step.id),
			draggable: true,
			selectable: true,
			data: {
				step,
				selected: step.id === callbacks.selectedStepId,
				onDelete: callbacks.onDelete,
				onSelect: callbacks.onSelect,
			},
		})),
		{
			id: "scenario-finish",
			type: "terminal",
			position: {
				x: 250 + (Math.max(0, ...[...positions.values()].map((p) => p.x)) || 0),
				y: 100,
			},
			draggable: true,
			data: { kind: "finish", label: "Завершение" },
		},
	];
	const edges = transitions.map((transition, index) => {
		const meta = TRIGGER_META[transition.trigger_type] || TRIGGER_META.default;
		return {
			id: `transition-${transition.id ?? `${transition.source_step_id}-${transition.target_step_id}-${transition.trigger_type}-${index}`}`,
			source: `step-${transition.source_step_id}`,
			target: transition.target_step_id == null ? "scenario-finish" : `step-${transition.target_step_id}`,
			type: "scenario",
			animated: transition.trigger_type === "success",
			markerEnd: { type: MarkerType.ArrowClosed, color: meta.color },
			style: { stroke: meta.color, strokeWidth: 2.4 },
			data: { transition, meta, onEdit: callbacks.onEditTransition },
		};
	});
	if (startStepId != null) {
		edges.unshift({
			id: "scenario-start-edge",
			source: "scenario-start",
			target: `step-${startStepId}`,
			type: "scenario",
			animated: true,
			markerEnd: { type: MarkerType.ArrowClosed, color: "#5064f7" },
			style: { stroke: "#5064f7", strokeWidth: 2.6 },
			data: { startEdge: true, meta: { label: "Начало", color: "#5064f7" } },
		});
	}
	return { nodes, edges, transitions, startStepId };
}

export function stepLabel(step) {
	const name = (step?.meta?.name ?? "").trim();
	if (name && name !== "Шаг без названия") return name;
	return `Шаг ${step?.step_number ?? ""}`.trim();
}

export function stepActionLabel(step) {
	if (step?.action_type?.name) return step.action_type.name;
	const actions = step?.area?.actions;
	if (Array.isArray(actions) && actions.length > 0) {
		const id = actions[0]?.action_type_id;
		if (id === 5) return "Ввод текста";
		if (id === 6) return "Нажатие клавиши";
		if (id === 1) return "Левый клик";
	}
	return "Действие не задано";
}
