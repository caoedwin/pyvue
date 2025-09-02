import axios from 'axios'
axios.defaults.withCredentials = true;

// 在文件顶部添加以下辅助函数
function redirectToLogin() {
  localStorage.removeItem('token');
  localStorage.removeItem('menuTree');
  window.location.href = '/login';
}

// 创建 axios 实例
/*1.localhost被视为特殊域名​：
浏览器将 localhost视为比普通域名更敏感的域名
出于安全考虑，许多浏览器在跨源请求 localhost时会默认阻止发送 Cookie​
这种行为在 Chrome 等现代浏览器中特别明显
2.​127.0.0.1被视为标准 IP 地址​：
浏览器将 IP 地址视为普通域名
当您使用 127.0.0.1时，浏览器会正常处理跨域 Cookie*/
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 使用环境变量
  withCredentials: true, // 关键：发送请求时携带cookie
  timeout: 5000
})

// 请求拦截器
service.interceptors.request.use(config => {
  // 确保始终携带凭证
    config.withCredentials = true
  // 如果是登录请求，不添加 token
  if (config.url.endsWith('/login/')) {
    return config;
  }

  const token = localStorage.getItem('token');
  console.log(token,'utils/resquest');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  return config;
});

// 在响应拦截器中处理401错误
service.interceptors.response.use(
  response => response,
  error => {
    console.log("error.message", error.message)
    const status = error.response?.status;
    if (status === 401 ||
        (error.message.includes('401') ||
         error.message.includes('Unauthorized'))) {
      redirectToLogin();
    }
    return Promise.reject(error);
  }

);

export default service
