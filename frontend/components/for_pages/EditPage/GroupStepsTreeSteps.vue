<template>
	<Tree
		:data="steps"
		item-key="id"
		nesting-key="steps"
		v-slot="{ item }"
	>
		<div class="tree-item-content cursor-pointer">
			<span>{{ item.meta.name }}</span>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from '@components/vue_dnd_kit_components/Tree';
import { watch } from "vue";

const props = defineProps(['steps']);

watch(props.steps, (value) => {
	console.log(value);
});
</script>

<style scoped>

</style>