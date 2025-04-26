<template>
		<!--Модалка-->
    <q-dialog ref="dialog" v-model="showModal" persistent transition-show="scale" transition-hide="scale">
      <q-card style="width: 700px; max-width: 80vw;">
        <q-card-section class="row">
          <div class="text-h6">Создание тренинга</div>
					<q-space />
					<q-btn icon="close" flat round dense v-close-popup />
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
        <q-card-actions align="right" class="row justify-center">
          <q-btn flat class="fit" label="Создать" color="secondary" @click="createTraning()"/>
        </q-card-actions>
      </q-card>
    </q-dialog>
		<!--Кнопка создания-->
    <q-btn
            color="secondary"
            text-color="white"
						class="size-button-50"
            label="Создать"
            @click="showModal = true"
        />
</template>
  
<script>
import axios from 'axios';
import { useTrainingStore } from "../../../../store/trainingStore.js";

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
				const store = useTrainingStore();
        axios.post(`${__BASE__URL__}/training/create_training`,
        {title: this.titleTraning, description: this.descriptionTraning},
					{headers:
							{Authorization:
									`Bearer ${localStorage.getItem('tokenAuth')}`
							},
						},
        )
        .then(() => {
					store.addTraining(
						{title: this.titleTraning, description: this.descriptionTraning, hiddenStatus: true}
					);
					this.titleTraning = '';
					this.descriptionTraning = '';
        })
				.catch(() => {
					this.$q.notify({ message: 'Произошла ошибка', position: 'top', type: 'negative' });
				})
					.finally(() => {
						this.$refs.dialog.hide();
					});
      }
    },
}
</script>