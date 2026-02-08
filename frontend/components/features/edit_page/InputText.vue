<template>
	<div
		class="cursor-pointer card text-center rounded-4 q-pa-md"
		style="background: #ffffff"
	>
		<span>
			{{ model }}
		</span>
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
				@keyup.enter="scope.set"
			/>
		</q-popup-edit>
	</div>
</template>

<script setup>
const model = defineModel();
</script>
