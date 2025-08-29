import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout'
import store from '@/store'

Vue.use(VueRouter)

// 创建基本路由 (包含通配符路由)
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
  {
    path: '*',
    redirect: '/404',
    hidden: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 动态添加路由的方法 (修复路径问题)
export function addDynamicRoutes(menuTree) {
  console.log('开始添加动态路由，菜单树:', menuTree);

  // 创建新的路由数组
  const newRoutes = []

  // 添加布局路由
  const layoutRoute = {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    name: 'Layout',
    children: []
  }

  // 添加仪表盘路由
  layoutRoute.children.push({
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue'),
    name: 'Dashboard',
    meta: { title: '控制面板', icon: 'dashboard' }
  })

  // 递归添加菜单路由 - 修复嵌套路由问题
  const addRoutes = (menuItems, parentRoute = null) => {
    menuItems.forEach(item => {
      // 处理带子菜单的项
      if (item.children && item.children.length) {
        // 即使顶级菜单没有path，也要创建路由节点
        const routePath = item.path || `/menu-${item.id}`;

        const route = {
          path: routePath,
          component: parentRoute ?
            (() => import(`@/views/${item.component || 'EmptyPage'}.vue`)) :
            Layout,
          name: `Menu_${item.id}`,
          meta: { title: item.title, icon: item.icon },
          children: []
        }

        // 递归添加子路由
        addRoutes(item.children, route)

        if (parentRoute) {
          parentRoute.children.push(route)
        } else {
          layoutRoute.children.push(route)
        }
      } else if (item.path) {
        // 处理叶子菜单项
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

  // 添加菜单路由到布局路由
  addRoutes(menuTree, layoutRoute)

  // 检查并移除可能存在的旧布局路由
  const existingLayout = router.options.routes.find(r => r.name === 'Layout')
  if (existingLayout) {
    console.log('移除旧布局路由');
    router.removeRoute('Layout')
  }

  // 添加新的布局路由
  console.log('添加新布局路由:', layoutRoute);
  router.addRoute(layoutRoute)

  // 确保通配符路由最后添加
  const wildcardExists = router.options.routes.find(r => r.path === '*')
  if (!wildcardExists) {
    router.addRoute({
      path: '*',
      redirect: '/404'
    })
  }

  console.log('动态路由添加完成，当前路由表:', router.getRoutes());
}


// 改进的路由守卫
router.beforeEach(async (to, from, next) => {
  console.log(`从 ${from.path} 跳转到 ${to.path}`)

  // 不需要认证的页面
  const noAuthPages = ['/login', '/404', '/route-loading']

  if (noAuthPages.includes(to.path)) {
    next()
    return
  }

  // 检查是否登录
  const token = localStorage.getItem('token')
  if (!token) {
    next('/login')
    return
  }

  // 显示路由加载状态
  store.dispatch('setRouteLoading', true)

  // 检查是否已经添加动态路由
  if (store.state.menuTree.length === 0) {
    // 创建全局加载锁
    if (!window.__DYNAMIC_ROUTES_LOADING__) {
      window.__DYNAMIC_ROUTES_LOADING__ = new Promise(async resolve => {
        try {
          // 尝试从本地存储获取菜单数据
          const menuTree = JSON.parse(localStorage.getItem('menuTree') || '[]')
          //console.log(menuTree,'menuTree')

          if (menuTree.length > 0) {
            // 提交到Vuex并添加动态路由
            store.commit('SET_MENU_TREE', menuTree)
            addDynamicRoutes(menuTree)
          } else {
            // 尝试从API获取菜单数据
            await store.dispatch('fetchUserInfo')
            const menuTree = store.state.menuTree
            if (menuTree.length > 0) {
              localStorage.setItem('menuTree', JSON.stringify(menuTree))
              addDynamicRoutes(menuTree)
            }
          }
        } catch (error) {
          console.error('获取菜单数据失败:', error)
          next('/login')
          return
        }
        resolve()
      })
    }

    // 等待路由添加完成
    try {
      await window.__DYNAMIC_ROUTES_LOADING__
    } catch (error) {
      console.error('路由加载失败:', error)
    } finally {
      delete window.__DYNAMIC_ROUTES_LOADING__
      store.dispatch('setRouteLoading', false)
    }

    // 添加后重新导航
    if (to.path !== from.path) {
      next({ ...to, replace: true })
    } else {
      next()
    }
    return
  }

  // 确保路由存在
  if (to.matched.length === 0) {
    next('/404')
  } else {
    store.dispatch('setRouteLoading', false)
    next()
  }
})

export default router
