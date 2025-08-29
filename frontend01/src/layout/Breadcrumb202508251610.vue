<template>
  <el-breadcrumb separator="/" class="breadcrumb">
    <el-breadcrumb-item
      v-for="(item, index) in breadcrumb"
      :key="index"
      :to="isCurrentRoute(item) ? null : item.path"
    >
      {{ item.meta.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script>
export default {
  computed: {
    breadcrumb() {
      // 正确实现：过滤有标题且不隐藏的路由记录
      return this.$route.matched.filter(route =>
        route.meta && route.meta.title && !route.meta.hideInBreadcrumb
      );
    }
  },
  methods: {
    isCurrentRoute(item) {
      return this.$route.path === item.path;
    }
  }
}
</script>

<style scoped>
.breadcrumb {
  margin-left: 20px;
  line-height: 50px;
}

/* 为当前路由添加不同样式 */
.el-breadcrumb__item:last-child .el-breadcrumb__inner {
  color: #606266;
  cursor: default;
}
</style>
