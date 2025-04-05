<template>
    <q-dialog v-model="visible" persistent>
      <q-card>
        <q-btn @click="closeModal" class="block q-ml-auto q-mt-sm q-mr-sm" icon="close" flat round dense/>
        <q-card-section>
            <slot name="header"></slot>
        </q-card-section>
        <q-card-section class="q-pt-none">
            <slot name="body"></slot>
        </q-card-section>
      </q-card>
    </q-dialog>
</template>

<script>
export default {
    name: 'BaseModal',
    props: ['show'],
    emits: ['close'],
    data() {
        return {
            visible: this.show
        }
    },
    watch: {
        show(newVal) {
            this.visible = newVal;
        }
    },
    methods: {
        closeModal() {
            this.visible = false;
            this.$emit('close');
        }
    }
}
</script>