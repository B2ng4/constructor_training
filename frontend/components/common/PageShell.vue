<template>
	<div class="page-shell">
		<header class="page-shell__header">
			<div class="page-shell__text">
				<h1 class="page-shell__title">{{ title }}</h1>
				<p v-if="subtitle" class="page-shell__subtitle">{{ subtitle }}</p>
			</div>
			<div v-if="$slots.actions" class="page-shell__actions">
				<slot name="actions" />
			</div>
		</header>
		<slot />
	</div>
</template>

<script setup>
defineProps({
	title: { type: String, required: true },
	subtitle: { type: String, default: "" },
});
</script>

<style scoped>
.page-shell {
	position: relative;
	z-index: 1;
	max-width: 1200px;
	margin: 0 auto;
	padding: 36px 32px 56px;
	display: flex;
	flex-direction: column;
	gap: 28px;
}

.page-shell__header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 24px;
	flex-wrap: wrap;
	margin-bottom: 4px;
}

.page-shell__text {
	min-width: 0;
}

.page-shell__title {
	font-size: 34px;
	font-weight: 750;
	color: #0f172a;
	margin: 0 0 6px;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.page-shell__subtitle {
	font-size: 16px;
	color: #64748b;
	margin: 0;
	font-weight: 450;
	line-height: 1.5;
	max-width: 520px;
}

.page-shell__actions {
	display: flex;
	align-items: center;
	gap: 12px;
	flex-shrink: 0;
}

@media (max-width: 768px) {
	.page-shell {
		padding: 28px 24px 40px;
		gap: 24px;
	}

	.page-shell__header {
		flex-direction: column;
		align-items: flex-start;
		gap: 16px;
	}

	.page-shell__title {
		font-size: 28px;
	}
}

@media (max-width: 640px) {
	.page-shell {
		padding: 20px 16px 32px;
		gap: 20px;
	}

	.page-shell__header {
		align-items: center;
		text-align: center;
	}

	.page-shell__title {
		font-size: 24px;
	}

	.page-shell__subtitle {
		font-size: 15px;
	}

	.page-shell__actions {
		width: 100%;
		justify-content: center;
	}
}
</style>
