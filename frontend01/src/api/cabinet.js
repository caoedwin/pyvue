import request from '@/utils/request'
import Cookies from 'js-cookie'  // 新增


// 获取所有柜体数据
export function getCabinetData(params) {
  return request({
    url: '/IntelligentCabinet/init-data/',
    method: 'get',
    params: params // 使用 params 而不是 data
    // data: data // 使用 params 而不是 data
  })
}

// 添加柜体
export function addCabinetAction(data) {
  return request({
    url: '/IntelligentCabinet/cabinets/',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data: {
      isGetData: 'addCabinet',
      newCabinet: data
    }
  })
}

// 删除柜体
export function deleteCabinetAction(cabinetId) {
  return request({
    url: `/IntelligentCabinet/cabinets/${cabinetId}/`,
    method: 'delete',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data: {
      isGetData: 'deleteCabinet'
    }
  })
}

// 更新柜格信息，包括管理员编辑柜格信息，取出保留，取消保留，归还柜格。其实其他涉及柜格信息变更的动作也可以用这个接口，包括用户预约柜格，取消预约，确认借出
export function updateGrid(cabinet, data) {
  return request({
    url: `/IntelligentCabinet/grids/${cabinet}/update/`,
    method: 'patch',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data: {
      isGetData: 'updategrid',
      cabinet: cabinet,
      gridinfo: data
    }
  })
}

// 用户预约柜格
export function reserveCell(gridId, data) {
  return request({
    url: `/IntelligentCabinet/grids/${gridId}/reserve/`,
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

// 取消预约
export function cancelReservation(gridId, data) {
  return request({
    url: `/IntelligentCabinet/grids/${gridId}/cancel-reserve/`,
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

// 确认借出
export function confirmBorrow(gridId, data) {
  return request({
    url: `/IntelligentCabinet/grids/${gridId}/confirm-borrow/`,
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

// 获取所有柜体数据 (兼容旧代码)
export function getCabinets() {
  return getCabinetData()
}
