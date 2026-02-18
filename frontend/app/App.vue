<template>
	<router-view v-slot="{ Component }">
		<transition name="page" mode="out-in">
			<component :is="Component" />
		</transition>
	</router-view>
</template>

<style>
.page-enter-active,
.page-leave-active {
	transition: opacity 0.25s var(--anim-ease-out, ease-out),
		transform 0.25s var(--anim-ease-out, ease-out);
}
.page-enter-from {
	opacity: 0;
	transform: translateY(6px);
}
.page-leave-to {
	opacity: 0;
	transform: translateY(-4px);
}
</style>

<script>
export default {
	name: "App",
};
</script>
