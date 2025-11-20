<template>
	<Tree
		:data="steps"
		item-key="id"
		nesting-key="steps"
		v-slot="{ item }"
	>
		<div class="tree-item-content cursor-pointer">
			<span>{{ item.id }}</span>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from '@components/vue_dnd_kit_components/Tree';

const props = defineProps(['steps']);
</script>

<style scoped>

</style>