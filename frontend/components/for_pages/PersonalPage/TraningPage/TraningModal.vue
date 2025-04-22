<template>
    <q-dialog 
        :model-value="showModal" 
        >
      <q-card>
        <q-card-section>
          <div class="text-h6">Создание тренинга</div>
        </q-card-section>
  
        <q-card-section>
            <q-input color="secondary" filled v-model="titleTraning" label="Название" />
            <q-input
                v-model="descriptionTraning"
                filled
                class="q-mt-md"
                label="Описание"
                type="textarea"
                color="secondary"
            />
        </q-card-section>
  
        <q-card-actions align="right">
          <q-btn flat label="Создать" color="secondary" @click="createTraning()"/>
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-btn 
            color="secondary" 
            text-color="white" 
            class="q-ml-auto q-mr-xl" 
            label="Создать" 
            @click="showModal = true"
        />
</template>
  
<script>
import axios from 'axios';

export default {
    data() {
      return {
        titleTraning: '',
        descriptionTraning: '',

        showModal: false,
      }
    },
    methods: {
      async createTraning() {
        axios.post(`${__BASE__URL__}/training/create_training`,
        {title: this.titleTraning, description: this.descriptionTraning},
        {headers: {Authorization: `Bearer ${localStorage.getItem('tokenAuth')}`}, },
        )
        .then(() => {
        });
      }
    },
}
</script>