import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/index.js";
import { Quasar, Notify, Dialog } from "quasar";
import quasarLang from "quasar/lang/ru";
import "@assets/styles/index.css";
import { createPinia } from "pinia";
import VueDndKitPlugin from "@vue-dnd-kit/core";
import { colorSchema } from "./config/colorSchema.js";

const pinia = createPinia();
createApp(App)
	.use(router)
	.use(VueDndKitPlugin)
	.use(Quasar, {
		plugins: { Notify, Dialog },
		lang: quasarLang,
		config: { ...colorSchema},
	})
	.use(pinia)
	.mount("#app");
