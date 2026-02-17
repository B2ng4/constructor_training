<template>
	<div
		class="cursor-pointer input-text-card text-center q-pa-md"
		:style="cardStyle"
	>
		<q-tooltip anchor="top middle" :offset="[0, 8]">
			Нажмите, чтобы ввести текст для этого поля
		</q-tooltip>
		<span class="input-text-value">{{ model || "Текст не указан" }}</span>
		<q-popup-edit
			v-model="model"
			auto-save
			v-slot="scope"
		>
			<q-input
				v-model="scope.value"
				dense
				autofocus
				counter
				placeholder="Введите текст"
				@keyup.enter="scope.set"
				@blur="scope.set"
			/>
		</q-popup-edit>
	</div>
</template>

<script setup>
const model = defineModel();

const cardStyle = {
	background: "rgba(255,255,255,0.68)",
	backdropFilter: "blur(10px)",
	WebkitBackdropFilter: "blur(10px)",
	height: "100%",
};
</script>

<style scoped>
.input-text-card:hover {
	background: rgba(255, 255, 255, 0.85) !important;
}

.input-text-value {
	display: block;
	min-height: 1.2em;
}
</style>
