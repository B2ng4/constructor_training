<template>
	<div v-if="selectedStep" class="passage-step-hint">
		<q-expansion-item
			:label="hintLabel"
			:icon="selectedStep?.hint ? 'lightbulb' : 'lightbulb_outline'"
			:class="{ 'has-hint': selectedStep?.hint }"
			:default-opened="forceShow"
			v-model="hintExpanded"
			dense
			dense-toggle
			expand-icon-class="text-grey-6"
			header-class="hint-header"
		>
			<template v-if="selectedStep?.hint">
				<q-card flat class="hint-content">
					<q-card-section class="q-pt-none">
						{{ selectedStep.hint }}
					</q-card-section>
				</q-card>
			</template>
		</q-expansion-item>
	</div>
</template>

<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
	selectedStep: { type: Object, default: null },
	/** После 3 неверных попыток подсказка показывается автоматически */
	forceShow: { type: Boolean, default: false },
});

const hintExpanded = ref(false);

watch(
	() => props.forceShow,
	(force) => {
		if (force) hintExpanded.value = true;
	},
	{ immediate: true }
);

watch(
	() => props.selectedStep?.id,
	() => {
		hintExpanded.value = props.forceShow;
	}
);

const hintLabel = computed(() =>
	props.selectedStep?.hint ? "Показать подсказку" : "Подсказки нет"
);
</script>

<style scoped>
.passage-step-hint {
	position: absolute;
	top: 64px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 5;
	min-width: 200px;
	max-width: 400px;
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(16px);
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.6);
	overflow: hidden;
}

.passage-step-hint :deep(.hint-header) {
	font-size: 13px;
	font-weight: 500;
	color: #64748b;
}

.passage-step-hint :deep(.has-hint .hint-header) {
	color: #1a1a2e;
}

.hint-content {
	background: transparent;
	font-size: 13px;
	color: #475569;
	line-height: 1.5;
}
</style>
