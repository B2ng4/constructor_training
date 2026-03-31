<template>
	<q-btn-dropdown
		flat
		no-caps
		rounded
		color="grey-8"
		icon="account_tree"
		dropdown-icon="expand_more"
		class="passage-steps-dropdown"
		content-class="passage-steps-content"
		menu-anchor="bottom left"
		menu-self="top left"
		:offset="[0, 8]"
	>
		<template #label>
			<span class="passage-steps-dropdown__label passage-steps-dropdown__label--full">
				Шаг {{ currentIndex + 1 }} из {{ steps.length }}
			</span>
			<span class="passage-steps-dropdown__label passage-steps-dropdown__label--short">
				{{ currentIndex + 1 }} / {{ steps.length }}
			</span>
		</template>
		<div class="step-list">
			<div class="step-list-header">
				<q-icon name="route" size="18px" class="step-list-header__icon" />
				<div class="step-list-header__text">
					<div class="step-list-header__title">Шаги тренинга</div>
					<div class="step-list-header__sub">{{ steps.length }} {{ stepsWord }}</div>
				</div>
			</div>
			<q-separator class="step-list-sep" />
			<q-list class="step-list-items" dense>
				<q-item
					v-for="(step, idx) in steps"
					:key="step.id"
					clickable
					v-close-popup
					:active="idx === currentIndex"
					active-class="step-item--active"
					class="step-item"
					@click="onSelectStep(step)"
				>
					<q-item-section avatar class="step-item__avatar">
						<q-icon
							v-if="idx < currentIndex"
							name="check_circle"
							color="positive"
							size="22px"
						/>
						<q-icon
							v-else-if="idx === currentIndex"
							name="play_circle"
							color="primary"
							size="22px"
						/>
						<q-avatar v-else size="26px" class="step-item__num">
							{{ idx + 1 }}
						</q-avatar>
					</q-item-section>
					<q-item-section>
						<q-item-label class="step-item__title">
							{{ step.meta?.name ?? `Шаг ${idx + 1}` }}
						</q-item-label>
						<q-item-label v-if="idx === currentIndex" caption class="step-item__caption">
							Текущий шаг
						</q-item-label>
					</q-item-section>
				</q-item>
			</q-list>
		</div>
	</q-btn-dropdown>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	steps: { type: Array, default: () => [] },
	currentIndex: { type: Number, default: 0 },
});

const emit = defineEmits(["select-step"]);

const stepsWord = computed(() => {
	const n = props.steps.length;
	const m10 = n % 10;
	const m100 = n % 100;
	if (m100 >= 11 && m100 <= 14) return "шагов";
	if (m10 === 1) return "шаг";
	if (m10 >= 2 && m10 <= 4) return "шага";
	return "шагов";
});

function onSelectStep(step) {
	emit("select-step", step);
}
</script>

<style scoped>
.passage-steps-dropdown {
	max-width: min(240px, 46vw);
	z-index: 10;
	background: rgba(255, 255, 255, 0.92) !important;
	backdrop-filter: blur(10px);
	box-shadow: 0 2px 14px rgba(15, 23, 42, 0.08);
	border: 1px solid rgba(15, 23, 42, 0.06);
	font-weight: 600;
}

.passage-steps-dropdown :deep(.q-btn__content) {
	min-width: 0;
}

.passage-steps-dropdown__label {
	font-size: 14px;
	letter-spacing: 0.01em;
}

.passage-steps-dropdown__label--full {
	display: inline;
}

.passage-steps-dropdown__label--short {
	display: none;
}

@media (max-width: 599px) {
	.passage-steps-dropdown__label--full {
		display: none;
	}

	.passage-steps-dropdown__label--short {
		display: inline;
	}
}

.step-list {
	min-width: 280px;
	max-width: min(360px, 92vw);
}

.step-list-header {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 14px 16px 12px;
	background: linear-gradient(
		160deg,
		color-mix(in srgb, var(--q-primary) 12%, white),
		rgba(248, 250, 252, 0.98)
	);
}

.step-list-header__icon {
	color: var(--q-primary);
	opacity: 0.9;
}

.step-list-header__title {
	font-size: 15px;
	font-weight: 700;
	color: #0f172a;
	line-height: 1.25;
}

.step-list-header__sub {
	font-size: 12px;
	font-weight: 500;
	color: #64748b;
	margin-top: 2px;
}

.step-list-sep {
	background: rgba(15, 23, 42, 0.08);
}

.step-list-items {
	max-height: min(52vh, 360px);
	overflow-y: auto;
	padding: 6px 0 10px;
}

.step-item {
	min-height: 48px;
	padding: 6px 12px 6px 8px;
	border-radius: 0;
	transition: background 0.15s ease;
}

.step-item:hover {
	background: rgba(15, 23, 42, 0.04);
}

.step-item__avatar {
	min-width: 40px;
}

.step-item__num {
	background: rgba(148, 163, 184, 0.22) !important;
	color: #475569 !important;
	font-size: 12px;
	font-weight: 700;
}

.step-item__title {
	font-size: 14px;
	font-weight: 600;
	color: #1e293b;
	line-height: 1.35;
}

.step-item__caption {
	color: var(--q-primary) !important;
	font-weight: 600;
	margin-top: 2px;
}

.step-item--active {
	background: color-mix(in srgb, var(--q-primary) 10%, white) !important;
	border-left: 3px solid var(--q-primary);
	padding-left: 9px !important;
}
</style>

<style>
.passage-steps-content {
	border-radius: 14px !important;
	box-shadow:
		0 12px 40px rgba(15, 23, 42, 0.14),
		0 0 0 1px rgba(15, 23, 42, 0.06) !important;
	overflow: hidden;
	padding: 0 !important;
}
</style>
