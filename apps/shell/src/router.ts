import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '@martin/common'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/search' },
    {
      path: '/search',
      component: () => import('./search/SearchPage.vue'),
    },
    {
      path: '/sign-in',
      component: () => import('./auth/SignInPage.vue'),
    },
    {
      path: '/sign-up',
      component: () => import('./auth/SignUpPage.vue'),
    },
    {
      path: '/workspace/:pathMatch(.*)*',
      component: () => import('./workspace-host.vue'),
    },
  ],
})

// navigation guard
const PROTECTED = ['/search', '/workspace']
const PUBLIC_ONLY = ['/sign-in', '/sign-up']

router.beforeEach((to, from, next) => {
  const { user, loading } = authStore.state
  const path = to.path

  if (loading) {
    // still initializing; allow
    next()
    return
  }

  if (!user && PROTECTED.some((p) => path.startsWith(p))) {
    next('/sign-in')
    return
  }

  if (user && PUBLIC_ONLY.includes(path)) {
    next('/')
    return
  }

  next()
})

export default router
