import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/index.js";
import { Quasar } from "quasar";
import quasarLang from "quasar/lang/ru";
import "quasar/src/css/index.sass";
import "@quasar/extras/material-icons/material-icons.css";

createApp(App).use(router).use(Quasar, { config: quasarLang }).mount("#app");
