<template>
  <div class="forgot-password-container">
    <el-form ref="form" :model="forgotForm" class="forgot-form">
      <h2>找回密码</h2>

      <el-form-item>
        <el-input
          v-model="forgotForm.phone"
          prefix-icon="el-icon-mobile-phone"
          placeholder="注册手机号码"
          maxlength="11"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <div class="code-input">
          <el-input
            v-model="forgotForm.code"
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
        <el-button
          type="primary"
          @click="verifyCode"
          :loading="loading"
          class="verify-btn"
        >验证并重置密码</el-button>
      </el-form-item>

      <div class="login-link">
        <el-link type="primary" @click="goToLogin">返回登录</el-link>
      </div>
    </el-form>
  </div>
</template>

<script>
import request from '@/utils/request';

export default {
  data() {
    return {
      forgotForm: {
        phone: '',
        code: ''
      },
      loading: false,
      codeButtonText: '获取验证码',
      codeButtonDisabled: false,
      countdown: 60
    };
  },
  methods: {
    sendVerificationCode() {
      if (!this.forgotForm.phone || !/^1[3-9]\d{9}$/.test(this.forgotForm.phone)) {
        this.$message.error('请输入有效的手机号码');
        return;
      }

      // 调用发送验证码API
      this.codeButtonDisabled = true;
      request.post('/api/send_verification_code/', {
        phone: this.forgotForm.phone,
        type: 'reset_password'
      }).then(() => {
        this.startCountdown();
        this.$message.success('验证码已发送');
      }).catch(error => {
        console.error('发送验证码失败:', error);
        this.$message.error('发送验证码失败');
        this.codeButtonDisabled = false;
      });
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

    verifyCode() {
      if (!this.forgotForm.phone || !this.forgotForm.code) {
        this.$message.error('请填写完整信息');
        return;
      }

      this.loading = true;
      request.post('/api/verify_reset_code/', {
        phone: this.forgotForm.phone,
        code: this.forgotForm.code
      }).then(() => {
        // 验证成功，跳转到重置密码页面
        this.$router.push({
          path: '/reset-password',
          query: {
            phone: this.forgotForm.phone,
            token: '临时令牌' // 实际使用中从响应中获取
          }
        });
      }).catch(error => {
        console.error('验证失败:', error);
        this.$message.error(error.response?.data?.detail || '验证失败');
      }).finally(() => {
        this.loading = false;
      });
    },

    goToLogin() {
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2d3a4b;
}

.forgot-form {
  width: 380px;
  padding: 40px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.forgot-form h2 {
  margin-bottom: 30px;
  text-align: center;
  color: #333;
}

.code-input {
  display: flex;
}

.verify-btn {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}
</style>
