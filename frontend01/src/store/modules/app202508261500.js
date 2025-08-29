const state = {
  isCollapse: false,
  menuPosition: 'left' // 'left' 或 'top'
}

const mutations = {
  TOGGLE_COLLAPSE: state => {
    state.isCollapse = !state.isCollapse
  },
  SET_MENU_POSITION: (state, position) => {
    state.menuPosition = position
  }
}

const actions = {
  toggleCollapse({ commit }) {
    commit('TOGGLE_COLLAPSE')
  }
}

const getters = {
  isCollapse: state => state.isCollapse,
  menuPosition: state => state.menuPosition
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
