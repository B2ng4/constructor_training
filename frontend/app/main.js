import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/index.js";
import { Quasar, Notify, Dialog, Dark } from "quasar";
import quasarLang from "quasar/lang/ru";
import "@fontsource-variable/inter";
import "@assets/styles/index.css";
import "highlight.js/styles/github-dark.css";
import { createPinia } from "pinia";
import VueDndKitPlugin from "@vue-dnd-kit/core";
import { colorSchema } from "./config/colorSchema.js";

const savedTheme = localStorage.getItem("skillsnap-theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
Dark.set(savedTheme ? savedTheme === "dark" : prefersDark);
document.documentElement.style.colorScheme = Dark.isActive ? "dark" : "light";

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
