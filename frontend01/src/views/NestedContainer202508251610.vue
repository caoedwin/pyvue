<template>
  <div class="nested-container">
    <!-- 二级菜单标题 -->
    <h2 v-if="showTitle" class="submenu-title">{{ $route.meta.title }}</h2>

    <!-- 三级菜单侧边栏 -->
    <div v-if="hasChildren" class="submenu-sidebar">
      <router-link
        v-for="child in childrenRoutes"
        :key="child.path"
        :to="child.path"
        class="submenu-item"
      >
        {{ child.meta.title }}
      </router-link>
    </div>

    <!-- 内容区域 -->
    <div :class="['content-area', { 'has-sidebar': hasChildren }]">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    childrenRoutes() {
      return this.$route.matched.slice(-1)[0]?.children || []
    },
    hasChildren() {
      return this.childrenRoutes.length > 0
    },
    showTitle() {
      return this.$route.meta.title && !this.hasChildren
    }
  }
}
</script>

<style scoped>
.nested-container {
  display: flex;
  height: 100%;
}

.submenu-sidebar {
  width: 200px;
  border-right: 1px solid #eee;
  padding: 20px 0;
}

.submenu-item {
  display: block;
  padding: 10px 20px;
  color: #333;
}

.content-area {
  flex: 1;
  padding: 20px;
}

.content-area.has-sidebar {
  padding-left: 30px;
}

.submenu-title {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  margin: 0;
}
</style>
