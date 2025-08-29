<template>
  <div class="route-loading-container">
    <div class="loading-spinner"></div>
    <p>正在加载路由，请稍候...</p>
  </div>
</template>

<script>
export default {
  name: 'RouteLoading'
}
</script>

<style scoped>
.route-loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e0e0e0;
  border-top: 5px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  color: #606266;
  font-size: 16px;
}
</style>
