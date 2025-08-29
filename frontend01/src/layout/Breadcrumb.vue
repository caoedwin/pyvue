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
      const uniqueRoutes = new Map();
      return this.$route.matched.reduce((acc, route) => {
        if (!route.meta || !route.meta.title || route.meta.hideInBreadcrumb)
          return acc;

        if (!uniqueRoutes.has(route.path)) {
          uniqueRoutes.set(route.path, true);
          acc.push(route);
        }
        return acc;
      }, []);
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

.el-breadcrumb__item:last-child .el-breadcrumb__inner {
  color: #606266;
  cursor: default;
}
</style>
