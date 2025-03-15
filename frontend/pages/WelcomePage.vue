<template>
	<q-toolbar class="text-primary">
		<q-toolbar-title class="q-ml-xl display-none cursor-pointer">
			<q-avatar square class="q-mr-xs">
			<img src="/favicon.svg" alt="">
		</q-avatar>
			Конструктор Тренингов
		</q-toolbar-title>
		<q-tabs v-model="tab" shrink class="q-mr-xl">
			<q-tab name="Home" label="Главная" />
			<q-tab name="Event" label="Мероприятия" />
			<q-tab name="Organizators" label="Для организаторов" />
		</q-tabs>
		<router-link to="/login">
			<q-btn outline color="primary" label="Вход" class="q-mr-xl"/>
		</router-link>
	</q-toolbar>
</template>
<script>
export default {
	name: "WelcomePage",
};
</script>

<style scoped>
@media (max-width: 800px) {
  .display-none {
    display: none;
  }
}
</style>
