// vue.config.js
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  css: {
    loaderOptions: {
      scss: {
        implementation: require('sass'),
        sassOptions: {
          fiber: require('fibers'),
        },
      }
    }
  },
  devServer: {
    // 强制设置 Host 头
    headers: {
      "Host": "localhost:8000"
    },

    proxy: {
      // 处理所有以 /api 开头的请求
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true, // 关键：修改 Host 头
        secure: false, // 开发环境禁用 HTTPS 检查
        logLevel: 'debug', // 开启详细日志
        pathRewrite: {
          '^/api': '/api' // 保持路径不变
        },
        // 显式设置请求头
        onProxyReq(proxyReq) {
          proxyReq.setHeader('Host', 'localhost:8000');
          proxyReq.setHeader('X-Forwarded-Host', 'localhost:8080');
        }
      },

      // 添加通配符处理所有请求
      '**': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        bypass: function(req) {
          // 跳过静态资源请求
          if (req.url.startsWith('/static') || req.url.startsWith('/public')) {
            return req.url;
          }
        }
      }
    }
  }
})
