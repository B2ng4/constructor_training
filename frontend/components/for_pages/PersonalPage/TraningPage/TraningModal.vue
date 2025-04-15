<template>
    <q-dialog 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)"
        >
      <q-card>
        <q-card-section>
          <div class="text-h6">Создание тренинга</div>
        </q-card-section>
  
        <q-card-section>
            <q-input filled v-model="text" label="Название" />
            <q-input
                v-model="text"
                filled
                class="q-mt-md"
                label="Описание"
                type="textarea"
            />
        </q-card-section>
  
        <q-card-actions align="right">
          <q-btn flat label="Создать" color="secondary" @click="$emit('update:modelValue', false)" />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>
  
<script>
export default {
    props: {
        modelValue: {
            type: Boolean,
            default: false
        }
    },
    emits: ['update:modelValue']
}
</script>