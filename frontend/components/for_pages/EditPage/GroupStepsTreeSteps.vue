<template>
	<Tree
		:data="steps"
		item-key="id"
		nesting-key="children"
		v-slot="{ item }"
	>
		<div class="tree-item-content">
			<span class="user-name">{{ item.name }}</span>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from '@components/vue_dnd_kit_components/Tree';

const props = defineProps(['steps']);
</script>

<style scoped>

</style>