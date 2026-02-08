<template>
	<svg
		xmlns="http://www.w3.org/2000/svg"
		:height="size"
		viewBox="0 -960 960 960"
		:width="size"
		:fill="color"
	>
		<path
			:d="picture"
		/>
	</svg>
</template>

<script setup>
defineProps(['size', 'color', 'picture']);
</script>
