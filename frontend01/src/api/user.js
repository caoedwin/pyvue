// src/api/user.js
import request from '@/utils/request' // 确保你已经有request.js

export function login(data) {
  return request({
    url: '/api/login/',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/api/logout/',
    method: 'post'
  })
}

export function getUserInfo() {
  return request({
    url: '/api/userinfo/',
    method: 'get'
  })
}
