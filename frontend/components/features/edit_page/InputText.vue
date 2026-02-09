<template>
	<div
		class="cursor-pointer card text-center q-pa-md"
		style="
		background: rgba(255,255,255,0.68);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		height: 100%"
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
