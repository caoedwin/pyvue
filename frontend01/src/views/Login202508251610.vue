<template>
  <div class="login-container">
    <el-form ref="form" :model="loginForm" class="login-form">
      <h2>系统登录</h2>
      <el-form-item>
        <el-input
          v-model="loginForm.account"
          prefix-icon="el-icon-user"
          placeholder="账号"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-input
          v-model="loginForm.password"
          prefix-icon="el-icon-lock"
          type="password"
          placeholder="密码"
          @keyup.enter.native="handleLogin"
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleLogin"
          :loading="loading"
          class="login-btn"
        >登录</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import request from '@/utils/request'
import axios from 'axios'
import { addDynamicRoutes } from '@/router/router.js'

export default {
  data() {
    return {
      loginForm: {
        account: '',
        password: ''
      },
      loading: false
    }
  },
  methods: {
    handleLogin() {
      this.loading = true;

      // 使用封装的 request 实例发送请求
      request.post('/api/login/', {
        account: this.loginForm.account,
        password: this.loginForm.password
      }).then(response => {
        console.log('登录响应:', response.data);

        // 1. 正确获取 access token
        const token = response.data.access;
        localStorage.setItem('token', token);

        // 2. 设置全局请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // 3. 提交到 Vuex
        this.$store.commit('SET_TOKEN', token);

        // 4. 保存用户信息到 Vuex
        if (response.data) {
          this.$store.commit('SET_USER', response.data);
        }

        // 5. 保存菜单数据并动态添加路由
        const menuTree = response.data.user.menu_tree || [];
        localStorage.setItem('token', token);
        this.$store.commit('SET_MENU_TREE', menuTree);
        localStorage.setItem('menuTree', JSON.stringify(menuTree));
        addDynamicRoutes(menuTree);

        // 设置默认跳转路径
        const defaultRoute = menuTree.length > 0 ?
          (menuTree[0].path || '/dashboard') : '/dashboard';

        // 添加短暂延迟确保路由已添加
        setTimeout(() => {
          console.log(`尝试跳转到: ${defaultRoute}`);
          this.$router.push(defaultRoute).catch(err => {
            if (err.name !== 'NavigationDuplicated') {
              console.error('导航错误:', err);
              // 回退到控制面板
              this.$router.push('/dashboard');
            }
          });
        }, 200);
      }).catch(error => {
        console.error('登录过程中发生错误:', error);

        // 错误处理
        let errorMessage = '登录失败';
        if (error.response) {
          if (error.response.status === 401) {
            errorMessage = '账号或密码错误';
          } else if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }
        }

        this.$message.error(errorMessage);
      }).finally(() => {
        this.loading = false;
      });
    }
  }
}
</script>

<style scoped>
/* 保持原有样式不变 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2d3a4b;
}

.login-form {
  width: 340px;
  padding: 40px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-form h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.login-btn {
  width: 100%;
}
</style>
