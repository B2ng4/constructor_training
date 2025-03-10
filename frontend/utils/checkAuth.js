import axios from "axios";

export async function checkAuth(tokenAuth) {
    return axios.get('http://localhost:8001/auth/me', {headers: {Authorization: `Bearer ${tokenAuth}`}})
    .then((response) => {
        return {dataUser: response.data, status: true} 
    })
    .catch(() => {
        return {status: false} 
    })
}