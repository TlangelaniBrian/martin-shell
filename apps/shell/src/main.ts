import { createApp } from 'vue'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from './App.vue'
import router from './router.js'
import './css/globals.css'

const app = createApp(App)
app.use(router)
app.use(VueQueryPlugin)
app.mount('#app')
