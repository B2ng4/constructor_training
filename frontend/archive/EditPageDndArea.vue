<script>
import { Background } from '@vue-flow/background'
export default {
	name: "EditPageDndArea",
	components: {Background},
};
</script>

<template>
	<div class="dropzone-background">
		<Background :size="2" :gap="20" pattern-color="#BDBDBD" />

		<div class="overlay">
			<slot />
		</div>
	</div>
</template>

<style scoped>

</style>