<template>
	<q-btn-dropdown
		class="passage-steps-dropdown"
		dropdown-icon="menu"
		color="primary"
		content-class="passage-steps-content"
		:label="`Шаг ${currentIndex + 1} из ${steps.length}`"
	>
		<div class="step-list">
			<div class="step-list-header">
				<span class="text-caption text-grey-7 text-weight-medium">
					Шаги тренинга ({{ steps.length }})
				</span>
			</div>
			<q-list class="step-list-items">
				<q-item
					v-for="(step, idx) in steps"
					:key="step.id"
					clickable
					:active="idx === currentIndex"
					active-class="step-active"
					@click="onSelectStep(step)"
				>
					<q-item-section avatar>
						<q-icon
							v-if="idx < currentIndex"
							name="check_circle"
							color="positive"
							size="20px"
						/>
						<q-icon
							v-else-if="idx === currentIndex"
							name="play_circle"
							color="primary"
							size="20px"
						/>
						<q-avatar v-else size="24px" color="grey-4">
							<span class="text-caption text-grey-6">{{ idx + 1 }}</span>
						</q-avatar>
					</q-item-section>
					<q-item-section>
						<q-item-label>{{ step.meta?.name ?? `Шаг ${idx + 1}` }}</q-item-label>
					</q-item-section>
				</q-item>
			</q-list>
		</div>
	</q-btn-dropdown>
</template>

<script setup>
const props = defineProps({
	steps: { type: Array, default: () => [] },
	currentIndex: { type: Number, default: 0 },
});

const emit = defineEmits(["select-step"]);

function onSelectStep(step) {
	emit("select-step", step);
}
</script>

<style scoped>
.passage-steps-dropdown {
	z-index: 10;
}

.step-list {
	min-width: 260px;
	max-width: 320px;
}

.step-list-header {
	padding: 12px 16px 8px;
}

.step-list-items {
	max-height: 320px;
	overflow-y: auto;
}

.step-active {
	background: rgba(80, 100, 247, 0.1);
}
</style>

<style>
.passage-steps-content {
	border-radius: 12px !important;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.14) !important;
	overflow: hidden;
}
</style>
