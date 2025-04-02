import axios from "axios";

export async function checkAuth(tokenAuth) {
    return axios.get(`${__BASE__URL__}/auth/me`, {headers: {Authorization: `Bearer ${tokenAuth}`}})
    .then((response) => {
        return {dataUser: response.data, status: true} 
    })
    .catch(() => {
        return {status: false} 
    })

}