<template>

</template>
  
<script>
import axios from 'axios';
export default {
    name: 'RegistrationForm',
    data() {
    return {
        user: {
        surname: '',
        name: '',
        phone: '',
        email: '',
        password: '',
        }
    }
    },
    methods: {
        async onSubmit() {
        axios.post(`${__BASE__URL__}/auth/register`, {
            email: this.user.email,
            phone_number: this.user.phone,
            first_name: this.user.name,
            last_name: this.user.surname,
            password: this.user.password,
        });
        }
    }
}
</script>
