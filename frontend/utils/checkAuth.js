import axios from "axios";
import { useUserStore } from '../store/userData.js'

export async function checkAuth(tokenAuth) {
    return axios.get(`${__BASE__URL__}/auth/me`, {headers: {Authorization: `Bearer ${tokenAuth}`}})
    .then((response) => {
        const store = useUserStore();
        store.first_name = response.data.first_name;
        return {dataUser: response.data, status: true};
    })
    .catch(() => {
        return {status: false};
    });
}