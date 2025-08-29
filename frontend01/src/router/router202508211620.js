// 修改后的 router.js
import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout'
import store from '@/store'

Vue.use(VueRouter)

// 创建基本路由 (移除通配符路由)
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
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 兼容的检查路由是否存在的方法
function routeExists(name) {
  return router.getRoutes().some(route => route.name === name)
}

// 修复后的动态路由添加方法
export function addDynamicRoutes(menuTree) {
  console.log('开始添加动态路由，菜单树:', menuTree)

  // 兼容方法替换：检查通配符路由是否存在
  if (routeExists('Wildcard')) {
    try {
      // 尝试移除通配符路由
      if (router.removeRoute) {
        router.removeRoute('Wildcard')
      } else {
        // 对于旧版本Vue Router，使用更复杂的方式移除路由
        const routes = router.options.routes.filter(r => r.name !== 'Wildcard')
        router.matcher = new VueRouter({ routes }).matcher
      }
    } catch (e) {
      console.warn('移除通配符路由失败', e)
    }
  }

  // 1. 创建新的布局路由
  const layoutRoute = {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    name: 'Layout',
    children: [
      {
        path: '/dashboard',
        component: () => import('@/views/Dashboard.vue'),
        name: 'Dashboard',
        meta: { title: '控制面板', icon: 'dashboard' }
      }
    ]
  }

  // 2. 递归添加菜单路由
  const addRoutes = (menuItems, parentRoute = null) => {
    menuItems.forEach(item => {
      if (item.children && item.children.length) {
        const route = {
          path: item.path || `/menu-${item.id}`,
          component: parentRoute ? 
            (() => import(`@/views/${item.component || 'EmptyPage'}.vue`)) : 
            Layout,
          name: `Menu_${item.id}`,
          meta: { title: item.title, icon: item.icon },
          children: []
        }

        addRoutes(item.children, route)

        if (parentRoute) {
          parentRoute.children.push(route)
        } else {
          layoutRoute.children.push(route)
        }
      } else if (item.path) {
        const leafRoute = {
          path: item.path,
          component: () => import(`@/views/${item.component || 'EmptyPage'}.vue`),
          name: `Page_${item.id}`,
          meta: { title: item.title, icon: item.icon }
        }

        if (parentRoute) {
          parentRoute.children.push(leafRoute)
        } else {
          layoutRoute.children.push(leafRoute)
        }
      }
    })
  }

  // 3. 添加菜单树到布局路由
  addRoutes(menuTree)

  // 4. 移除旧布局路由（如果存在）
  if (routeExists('Layout')) {
    try {
      if (router.removeRoute) {
        router.removeRoute('Layout')
      } else {
        // 旧版本处理
        const routes = router.options.routes.filter(r => r.name !== 'Layout')
        router.matcher = new VueRouter({ routes }).matcher
      }
    } catch (e) {
      console.warn('移除旧布局路由失败', e)
    }
  }

  // 5. 添加新的布局路由
  console.log('添加新布局路由:', layoutRoute);
  router.addRoute(layoutRoute)

  // 6. 最后添加通配符路由
  router.addRoute({
    path: '*',
    redirect: '/404',
    name: 'Wildcard',
    hidden: true
  })

  console.log('动态路由添加完成', router.getRoutes())
}

// 改进的路由守卫
router.beforeEach(async (to, from, next) => {
  console.log(`路由跳转: ${from.path} → ${to.path}`)

  // 无需认证的白名单
  const noAuthPages = ['/login', '/404', '/route-loading']
  
  if (noAuthPages.includes(to.path)) {
    return next()
  }

  // 1. 检查认证令牌
  const token = localStorage.getItem('token')
  if (!token) {
    return next('/login')
  }

  // 2. 检查动态路由是否已加载
  if (store.state.menuTree.length === 0) {
    // 显示加载状态
    store.dispatch('setRouteLoading', true)
    
    try {
      // 使用全局锁避免重复加载
      if (!window.__DYNAMIC_ROUTES_LOADING__) {
        window.__DYNAMIC_ROUTES_LOADING__ = (async () => {
          let menuTree = JSON.parse(localStorage.getItem('menuTree') || '[]')
          
          if (!menuTree.length) {
            await store.dispatch('fetchUserInfo')
            menuTree = store.state.menuTree
            localStorage.setItem('menuTree', JSON.stringify(menuTree))
          } else {
            // 关键：将从localStorage读取的菜单树提交到Vuex
            store.commit('SET_MENU_TREE', menuTree)
          }
          
          // 关键点：保存目标路径，用于加载后重定向
          window.__ORIGINAL_TARGET__ = to.fullPath
          addDynamicRoutes(menuTree)
        })()
      }
      
      // 等待动态路由加载完成
      await window.__DYNAMIC_ROUTES_LOADING__
      
      // 加载后重定向到原始目标路径
      const target = window.__ORIGINAL_TARGET__ || '/dashboard'
      delete window.__ORIGINAL_TARGET__
      delete window.__DYNAMIC_ROUTES_LOADING__
      
      console.log(`重定向到原始路径: ${target}`)
      
      // 修复无限循环的关键：检查目标路径是否与当前路径相同
      if (to.path === target) {
        // 如果目标路径与当前路径相同，直接继续导航
        return next()
      } else {
        // 否则重定向到目标路径
        return next(target)
      }
    } catch (error) {
      console.error('路由加载失败:', error)
      return next('/login')
    } finally {
      store.dispatch('setRouteLoading', false)
    }
  }

  // 3. 确保路由存在
  if (to.matched.length === 0) {
    console.warn(`路由未匹配: ${to.path}`)
    return next('/404')
  }

  next()
})

export default router
