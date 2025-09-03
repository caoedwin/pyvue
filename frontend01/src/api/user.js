// src/api/user.js
import request from '@/utils/request' // 确保你已经有request.js
import Cookies from 'js-cookie' // 确保这里正确导入

export function login(data) {
  return request({
    url: '/api/login/',
    method: 'post',
    data
  })
}

export function send_verification_code(data) {
  return request({
    url: '/api/send_verification_code/',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

export function register(data) {
  return request({
    url: '/api/register/',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

export function reset_password(data) {
  return request({
    url: '/api/reset_password/',
    method: 'post',
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken')  // 关键：添加CSRF token，Django默认要求所有非安全的HTTP方法（如POST、PUT、PATCH、DELETE）都需要提供CSRF token
    },
    data
  })
}

export function logout() {
  return request({
    url: '/api/reset_password/',
    method: 'post'
  })
}

export function getUserInfo() {
  return request({
    url: '/api/userinfo/',
    method: 'get'
  })
}
