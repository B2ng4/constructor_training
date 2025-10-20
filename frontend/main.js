import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/index.js";
import { Quasar } from "quasar";
import quasarLang from "quasar/lang/ru";
import "quasar/src/css/index.sass";
import "@quasar/extras/material-icons/material-icons.css";
import "@assets/styles/index.css";
import { Notify } from "quasar";
import { createPinia } from 'pinia';

const pinia = createPinia();
createApp(App)
    .use(router)
    .use(Quasar, { plugins: {Notify}, lang: quasarLang, config: { brand: {secondary: '#6274F8'} } })
    .use(pinia)
    .mount("#app");
