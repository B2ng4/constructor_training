<template>
	<NodeResizer min-width="100" min-height="30" />

	<Handle type="target" :position="Position.Left" />
	<Handle type="source" :position="Position.Right" />
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core'
import { NodeResizer } from '@vue-flow/node-resizer'

defineProps(['data'])
</script>

<style>
@import "@vue-flow/node-resizer/dist/style.css";
</style>

