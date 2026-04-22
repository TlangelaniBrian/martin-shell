import { createRouter, createWebHistory } from 'vue-router'
import { authStore, authReady } from '@martin/common'

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
      path: '/auth/callback/google',
      component: () => import('./auth/OAuthCallbackPage.vue'),
    },
    {
      path: '/auth/forgot-password',
      component: () => import('./auth/ForgotPasswordPage.vue'),
    },
    {
      path: '/auth/verify',
      component: () => import('./auth/VerifyPage.vue'),
    },
    {
      path: '/account',
      component: () => import('./account/AccountPage.vue'),
    },
    {
      path: '/briefcases',
      component: () => import('./briefcases/BriefcasesPage.vue'),
    },
    {
      path: '/briefcases/:id',
      component: () => import('./briefcases/BriefcaseWorkspacePage.vue'),
    },
    {
      path: '/workspace/:pathMatch(.*)*',
      component: () => import('./workspace-host.vue'),
    },
  ],
})

const PROTECTED = ['/search', '/workspace', '/briefcases', '/account']
const PUBLIC_ONLY = ['/sign-in', '/sign-up', '/auth/']

router.beforeEach(async (to, _from, next) => {
  await authReady

  const { user } = authStore.state
  const path = to.path

  if (!user && PROTECTED.some((p) => path.startsWith(p))) {
    next('/sign-in')
    return
  }

  if (user && PUBLIC_ONLY.some((p) => path.startsWith(p))) {
    next('/')
    return
  }

  next()
})

export default router
