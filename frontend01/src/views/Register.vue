<template>
  <div class="register-container">
    <el-form ref="form" :model="registerForm" class="register-form">
      <h2>用户注册</h2>

      <el-form-item>
        <el-input
          v-model="registerForm.phone"
          prefix-icon="el-icon-mobile-phone"
          placeholder="手机号码"
          maxlength="11"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <div class="code-input">
          <el-input
            v-model="registerForm.code"
            prefix-icon="el-icon-message"
            placeholder="验证码"
            style="width: 60%"
          ></el-input>
          <el-button
            type="primary"
            style="width: 35%; margin-left: 5%"
            :disabled="codeButtonDisabled"
            @click="sendVerificationCode"
          >
            {{ codeButtonText }}
          </el-button>
        </div>
      </el-form-item>

      <el-form-item>
        <el-input
          v-model="registerForm.password"
          prefix-icon="el-icon-lock"
          type="password"
          placeholder="设置密码"
          show-password
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-input
          v-model="registerForm.confirmPassword"
          prefix-icon="el-icon-lock"
          type="password"
          placeholder="确认密码"
          show-password
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="handleRegister"
          :loading="loading"
          class="register-btn"
        >注册</el-button>
      </el-form-item>

      <div class="login-link">
        <el-link type="primary" @click="goToLogin">返回登录</el-link>
      </div>
    </el-form>
  </div>
</template>

<script>
import * as userreg from '@/api/user'
import request from '@/utils/request' // 添加缺失的request导入

export default {
  data() {
    return {
      registerForm: {
        phone: '',
        code: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      codeButtonText: '获取验证码',
      codeButtonDisabled: false,
      countdown: 60
    };
  },
  methods: {
    async sendVerificationCode() {
      if (!this.registerForm.phone || !/^1[3-9]\d{9}$/.test(this.registerForm.phone)) {
        this.$message.error('请输入有效的手机号码');
        return;
      }

      // 调用发送验证码API
      this.codeButtonDisabled = true;
      try {
        // 使用await等待API调用
        const response = await userreg.send_verification_code({
          phone: this.registerForm.phone,
          type: 'register'
        });

        // 成功发送后启动倒计时
        this.startCountdown();
        this.$message.success('验证码已发送');
      } catch(error) {
        console.error('发送验证码失败:', error);
        this.$message.error('发送验证码失败');
        this.codeButtonDisabled = false;
      }
    },

    startCountdown() {
      const timer = setInterval(() => {
        this.codeButtonText = `${this.countdown}秒后重新获取`;
        this.countdown--;

        if (this.countdown < 0) {
          clearInterval(timer);
          this.codeButtonText = '获取验证码';
          this.codeButtonDisabled = false;
          this.countdown = 60;
        }
      }, 1000);
    },

    // 修改为异步函数
    async handleRegister() {
      // 表单验证
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.$message.error('两次输入的密码不一致');
        return;
      }

      this.loading = true;
      try {
        // 使用await等待注册结果
        const response = await request.post('/api/register/', {
          phone: this.registerForm.phone,
          code: this.registerForm.code,
          password: this.registerForm.password
        });

        this.$message.success('注册成功');
        this.$router.push('/login');
      } catch(error) {
        console.error('注册失败:', error);
        this.$message.error(error.response?.data?.detail || '注册失败');
      } finally {
        this.loading = false;
      }
    },

    goToLogin() {
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2d3a4b;
}

.register-form {
  width: 380px;
  padding: 40px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-form h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.code-input {
  display: flex;
}

.register-btn {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}
</style>
