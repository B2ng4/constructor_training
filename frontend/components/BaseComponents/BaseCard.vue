<template>
    <q-card class="my-card shadow-1" :style="{ maxWidth: width }">
      <q-card-section>
        <div class="text-h6">{{ title }}</div>
      </q-card-section>
      <q-card-section>
        <slot name="body"></slot>
      </q-card-section>
    </q-card>
</template>
<script>
export default {
	name: "BaseCard",
    props: {
        title: null,
        width: {
            default: '250px'
        }
    }
};
</script>

<style scoped>
.my-card {
    width: 100%;
}
</style>
