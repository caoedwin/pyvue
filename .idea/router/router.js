import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout'
import store from '@/store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/404.vue'),
    name: 'NotFound',
    hidden: true
  },
  {
    path: '/route-loading',
    component: () => import('@/views/RouteLoading.vue'),
    name: 'RouteLoading',
    hidden: true
  },
  /*{
    path: '/',
    redirect: '/dashboard',
    meta: { hideInBreadcrumb: true }
  },
  {
    path: '*',
    redirect: '/404',
    meta: { hideInBreadcrumb: true }
  }//加了这两个，刷新页面后就会跳到404
*/
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

function routeExists(name) {
  return router.getRoutes().some(route => route.name === name)
}

export function addDynamicRoutes(menuTree) {
  if (routeExists('Wildcard')) {
    try {
      router.removeRoute('Wildcard')
    } catch (e) {
      console.warn('移除通配符路由失败', e)
    }
  }

  const layoutRoute = {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    name: 'Layout',
    meta: {
      isRootLayout: true,
      hideInBreadcrumb: true
    },
    children: [
      {
        path: '/dashboard',
        component: () => import('@/views/Dashboard.vue'),
        name: 'Dashboard',
        meta: { title: '控制面板', icon: 'dashboard' }
      }
    ]
  }

  const addRoutes = (menuItems, parentRoute = null, level = 0) => {
    menuItems.forEach(item => {
      if (item.children && item.children.length) {
        const route = {
          path: item.path || `/menu-${item.id}`,
          component: level === 0 ?
            () => import('@/views/NestedContainer.vue') :
            null,
          name: `Menu_${item.id}`,
          meta: {
            title: item.title,
            icon: item.icon,
            hideInBreadcrumb: level > 0
          },
          redirect: item.children[0].path,
          children: []
        }

        if (parentRoute) {
          parentRoute.children.push(route)
        } else {
          layoutRoute.children.push(route)
        }

        addRoutes(item.children, route, level + 1)
      }
      else if (item.path) {
        console.log(item,item.component,item.path)
        const leafRoute = {
          path: item.path,
          component: () => import(`@/views/${item.component || 'EmptyPage'}.vue`),
          name: `Page_${item.id}`,
          meta: {
            // title: item.title,
            icon: item.icon,
            isLeaf: true
          }
        }

        if (parentRoute) {
          parentRoute.children.push(leafRoute)
        } else {
          layoutRoute.children.push(leafRoute)
        }
      }
    })
  }

  addRoutes(menuTree)

  if (routeExists('Layout')) {
    try {
      router.removeRoute('Layout')
    } catch (e) {
      console.warn('移除旧布局路由失败', e)
    }
  }

  router.addRoute(layoutRoute)
  router.addRoute({
    path: '*',
    redirect: '/404',
    name: 'Wildcard',
    hidden: true
  })
  //console.log('动态路由添加完成', JSON.stringify(router.getRoutes()))
  console.log('动态路由添加完成', router.getRoutes())
}

router.beforeEach(async (to, from, next) => {
  console.log(`路由跳转: ${from.path} → ${to.path}`)
  console.log('路由匹配记录:', to.matched.map(r => r.path))
  console.log('路由名称:', to.matched.map(r => r.name))
  const noAuthPages = ['/login', '/404', '/route-loading']
  if (noAuthPages.includes(to.path)) return next()

  if (!localStorage.getItem('token')) return next('/login')

  if (store.state.menuTree.length === 0) {
    try {
      const savedMenuTree = JSON.parse(localStorage.getItem('menuTree') || '[]');
      // 添加此处：打印从localStorage读取的menuTree
      console.log('从localStorage读取的menuTree:', JSON.stringify(savedMenuTree));
      if (savedMenuTree.length) {
        store.commit('SET_MENU_TREE', savedMenuTree);
        addDynamicRoutes(savedMenuTree);
        return next(to.path);
      }

      await store.dispatch('fetchUserInfo');
      // 添加此处：打印从API获取的menuTree
      console.log('从API获取的menuTree:', store.state.menuTree);
      addDynamicRoutes(store.state.menuTree);
    } catch (error) {
      console.error('路由加载失败:', error);
      localStorage.removeItem('token');
      return next('/login');
    }
  }

  if (to.matched.length === 0) {
    console.warn(`路由未匹配: ${to.path}`)
    return next('/404')
  }

  next()
})

export default router
