import { addCabinetAction as addCabinet } from '@/api/cabinet'
import { deleteCabinetAction as deleteCabinet } from '@/api/cabinet'

const state = {
  cabinets: [],
  currentCabinetId: null,
  isAdmin: false,
  currentUser: null,
  CustomerOptions: []
}

const mutations = {
  SET_CABINETS: (state, data) => {
    state.cabinets = data.cabinets
    state.isAdmin = data.isAdmin
    state.currentUser = data.currentUser
    state.CustomerOptions = data.CustomerOptions
  },
  SET_CURRENT_CABINET: (state, cabinetId) => {
    state.currentCabinetId = cabinetId
  },
  ADD_CABINET: (state, cabinet) => {
    state.cabinets.push(cabinet)
  },
  UPDATE_GRID: (state, { cabinetId, rowIndex, colIndex, data }) => {
    const cabinet = state.cabinets.find(c => c.id === cabinetId)
    if (cabinet) {
      cabinet.gridData[rowIndex][colIndex] = {
        ...cabinet.gridData[rowIndex][colIndex],
        ...data
      }
    }
  },
  REMOVE_CABINET: (state, cabinetId) => {
    state.cabinets = state.cabinets.filter(c => c.id !== cabinetId)
  }
}

const actions = {
  // 获取所有柜体数据
  async fetchCabinetData({ commit }) {
    try {
      const response = await cabinetApi.getCabinetData()
      commit('SET_CABINETS', response.data)
      return response.data
    } catch (error) {
      throw new Error('获取柜体数据失败: ' + error.message)
    }
  },

  // 添加新柜体
  async addCabinet({ commit }, cabinetData) {
    try {
      const response = await cabinetApi.addCabinet(cabinetData)
      commit('ADD_CABINET', response.data)
      return response.data
    } catch (error) {
      throw new Error('添加柜体失败: ' + error.message)
    }
  },

  // 删除柜体
  async deleteCabinet({ commit }, cabinetId) {
    try {
      await cabinetApi.deleteCabinet(cabinetId)
      commit('REMOVE_CABINET', cabinetId)
    } catch (error) {
      throw new Error('删除柜体失败: ' + error.message)
    }
  },

  // 更新柜格信息
  async updateGrid({ commit }, { gridId, data }) {
    try {
      const response = await cabinetApi.updateGrid(gridId, data)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: response.data
      })
      return response.data
    } catch (error) {
      throw new Error('更新柜格信息失败: ' + error.message)
    }
  },

  // 用户预约柜格
  async reserveCell({ commit }, { gridId, data }) {
    try {
      const response = await cabinetApi.reserveCell(gridId, data)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 2, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('预约柜格失败: ' + error.message)
    }
  },

  // 取消预约
  async cancelReservation({ commit }, gridId) {
    try {
      const response = await cabinetApi.cancelReservation(gridId)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 0, user: null, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('取消预约失败: ' + error.message)
    }
  },

  // 确认借出
  async confirmBorrow({ commit }, gridId) {
    try {
      const response = await cabinetApi.confirmBorrow(gridId)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 1, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('确认借出失败: ' + error.message)
    }
  },

  // 取出保留
  async takeOutCell({ commit }, { gridId, data }) {
    try {
      const response = await cabinetApi.takeOutCell(gridId, data)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 3, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('取出保留失败: ' + error.message)
    }
  },

  // 取消保留
  async cancelTakenReserve({ commit }, gridId) {
    try {
      const response = await cabinetApi.cancelTakenReserve(gridId)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 0, user: null, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('取消保留失败: ' + error.message)
    }
  },

  // 归还柜格
  async returnCell({ commit }, gridId) {
    try {
      const response = await cabinetApi.returnCell(gridId)

      // 从gridId解析柜体ID和位置信息
      const [cabinetId, rowIndex, colIndex] = gridId.split('-').map(part => {
        if (part.includes('row')) return parseInt(part.replace('row', ''))
        if (part.includes('col')) return parseInt(part.replace('col', ''))
        return parseInt(part)
      })

      commit('UPDATE_GRID', {
        cabinetId,
        rowIndex,
        colIndex,
        data: { status: 0, user: null, ...response.data }
      })
      return response.data
    } catch (error) {
      throw new Error('归还柜格失败: ' + error.message)
    }
  }
}

const getters = {
  cabinets: state => state.cabinets,
  currentCabinetId: state => state.currentCabinetId,
  isAdmin: state => state.isAdmin,
  currentUser: state => state.currentUser,
  CustomerOptions: state => state.CustomerOptions,
  currentCabinet: state => {
    return state.cabinets.find(c => c.id === state.currentCabinetId) || {}
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
