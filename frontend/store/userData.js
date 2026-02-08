import { defineStore } from 'pinia';

export const useUserStore = defineStore('useUserStore', {
    state: () => {
        return {
            id: '',
            email: '',
            phone_number: '',
            first_name: '',
            last_name:'',
        };
      },
      getters: {
        getName: (state) => state.first_name,
      },
})