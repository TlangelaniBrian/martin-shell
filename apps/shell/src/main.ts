import { createApp } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { configureApi } from '@martin/common'
import App from './App.vue'
import router from './router.js'
import './css/globals.css'

configureApi(import.meta.env.VITE_API_URL)

const app = createApp(App)
app.use(router)
app.use(VueQueryPlugin)
app.mount('#app')
