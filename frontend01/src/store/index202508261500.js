import Vue from 'vue'
import Vuex from 'vuex'
import request from '@/utils/request'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    token: localStorage.getItem('token') || '',
    user: null,
    menuTree: [], // 用于存储菜单数据
    isCollapse: false, // 导航栏是否折叠
    menuPosition: 'left', // 菜单位置，left（左侧）或top（顶部）
    routeLoading: false // 路由加载状态
  },
  mutations: {
    // 同步更新状态的方法
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER(state, user) {
      state.user = user
    },
    SET_MENU_TREE(state, menuTree) {
      state.menuTree = menuTree
      // 添加localStorage持久化
      localStorage.setItem('menuTree', JSON.stringify(menuTree));
    },
    TOGGLE_COLLAPSE(state) {
      state.isCollapse = !state.isCollapse
    },
    SET_COLLAPSE(state, collapse) {
      state.isCollapse = collapse
    },
    SET_MENU_POSITION(state, position) {
      state.menuPosition = position
    },
    SET_ROUTE_LOADING(state, loading) {
      state.routeLoading = loading
    },
    LOGOUT(state) {
      state.token = ''
      state.user = null
      state.menuTree = []
      state.isCollapse = false // 重置折叠状态
      state.menuPosition = 'left' // 重置菜单位置
      state.routeLoading = false // 重置路由加载状态
      localStorage.removeItem('token')
      localStorage.removeItem('menuTree')
    }
  },
  actions: {
    // 异步操作和业务逻辑
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      commit('SET_MENU_TREE', user.menu_tree || [])
    },
    fetchUserInfo({ commit }) {
  return request.get('/api/userinfo/').then(response => { // 改为GET请求
    const userData = response.data;
    const menuTree = userData.menu_tree || [];

    commit('SET_USER', userData);
    commit('SET_MENU_TREE', menuTree);
    localStorage.setItem('menuTree', JSON.stringify(menuTree));
  }).catch(error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    throw error;
  });
},
    logout({ commit }) {
      commit('LOGOUT')
    },
    toggleCollapse({ commit }) {
      commit('TOGGLE_COLLAPSE')
    },
    setCollapse({ commit }, collapse) {
      commit('SET_COLLAPSE', collapse)
    },
    setMenuPosition({ commit }, position) {
      commit('SET_MENU_POSITION', position)
    },
    setRouteLoading({ commit }, loading) {
      commit('SET_ROUTE_LOADING', loading)
    }
  },
  getters: {
    // 计算属性
    isLoggedIn: state => !!state.token,
    currentUser: state => state.user,
    menuTree: state => state.menuTree,
    isCollapse: state => state.isCollapse,
    menuPosition: state => state.menuPosition,
    routeLoading: state => state.routeLoading
  }
})
