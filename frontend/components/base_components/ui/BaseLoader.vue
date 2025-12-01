<template>
	<q-inner-loading :showing="model">
		<q-spinner-gears :size="size" color="primary" />
	</q-inner-loading>
</template>

<script setup>
const props = defineProps(['size']);
const model = defineModel();
</script>
