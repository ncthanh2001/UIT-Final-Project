import { createApp } from "vue";
import { CkeditorPlugin } from "@ckeditor/ckeditor5-vue";

import App from "./App.vue";
import router from "./router";
import { initSocket } from "./socket";
import VueApexCharts from "vue3-apexcharts"; 
import { frappeRequest, pageMetaPlugin, resourcesPlugin, setConfig } from "frappe-ui";

import "./index.css";

const app = createApp(App);

setConfig("resourceFetcher", frappeRequest);

app.use(router); 
app.use(resourcesPlugin);
app.use(pageMetaPlugin);
app.use(VueApexCharts);
app.use(CkeditorPlugin);
const socket = initSocket();
app.config.globalProperties.$socket = socket;

app.mount("#app");
