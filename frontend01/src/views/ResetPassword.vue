<template>
  <div class="reset-password-container">
    <el-form ref="form" :model="resetForm" class="reset-form">
      <h2>重置密码</h2>

      <el-form-item>
        <el-input
          v-model="resetForm.password"
          prefix-icon="el-icon-lock"
          type="password"
          placeholder="新密码"
          show-password
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-input
          v-model="resetForm.confirmPassword"
          prefix-icon="el-icon-lock"
          type="password"
          placeholder="确认新密码"
          show-password
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="handleReset"
          :loading="loading"
          class="reset-btn"
        >确认重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import request from '@/utils/request';

export default {
  data() {
    return {
      resetForm: {
        password: '',
        confirmPassword: ''
      },
      loading: false,
      phone: this.$route.query.phone,
      token: this.$route.query.token
    };
  },
  methods: {
    handleReset() {
      if (this.resetForm.password !== this.resetForm.confirmPassword) {
        this.$message.error('两次输入的密码不一致');
        return;
      }

      this.loading = true;
      request.post('/api/reset_password/', {
        phone: this.phone,
        token: this.token,
        new_password: this.resetForm.password
      }).then(() => {
        this.$message.success('密码重置成功');
        this.$router.push('/login');
      }).catch(error => {
        console.error('重置密码失败:', error);
        this.$message.error(error.response?.data?.detail || '重置密码失败');
      }).finally(() => {
        this.loading = false;
      });
    }
  }
};
</script>

<style scoped>
.reset-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2d3a4b;
}

.reset-form {
  width: 380px;
  padding: 40px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.reset-form h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.reset-btn {
  width: 100%;
}
</style>
