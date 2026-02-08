<template>
    <q-card class="my-card shadow-1" :style="{ maxWidth: width }">
      <q-card-section>
        <slot name="title"></slot>
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
