<template>
  <div class="app-wrapper" :class="menuPositionClass">
    <!-- 顶部菜单模式 -->
    <div v-if="menuPosition === 'top'" class="top-menu-container">
      <el-menu
        :default-active="activeMenu"
        class="el-menu-demo"
        mode="horizontal"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        @select="handleSelect"
        router
      >
        <!-- 固定仪表盘菜单 -->
        <el-menu-item index="/dashboard">
          <i class="el-icon-dashboard"></i>
          <span>控制面板</span>
        </el-menu-item>

        <!-- 动态生成顶部菜单 -->
        <template v-for="menu in menuTree">
          <template v-if="menu.children && menu.children.length">
            <el-submenu :key="menu.id" :index="menu.id.toString()">
              <template slot="title">
                <i :class="menu.icon"></i>
                <span>{{ menu.title }}</span>
              </template>
              <template v-for="child in menu.children">
                <el-menu-item
                  v-if="!child.children || !child.children.length"
                  :key="child.id"
                  :index="child.path"
                >
                  <i :class="child.icon"></i>
                  <span>{{ child.title }}</span>
                </el-menu-item>
                <el-submenu
                  v-else
                  :key="child.id"
                  :index="child.id.toString()"
                >
                  <template slot="title">
                    <i :class="child.icon"></i>
                    <span>{{ child.title }}</span>
                  </template>
                  <el-menu-item
                    v-for="grandchild in child.children"
                    :key="grandchild.id"
                    :index="grandchild.path"
                  >
                    <span>{{ grandchild.title }}</span>
                  </el-menu-item>
                </el-submenu>
              </template>
            </el-submenu>
          </template>
          <el-menu-item v-else :key="menu.id" :index="menu.path">
            <i :class="menu.icon"></i>
            <span>{{ menu.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </div>

    <!-- 左侧菜单模式 -->
    <div v-else class="sidebar-container" :class="{'collapsed': isCollapse}">
      <!-- 折叠控制按钮 -->
      <div class="collapse-control" v-if="menuPosition === 'left'">
        <el-radio-group :value="isCollapse" @input="setCollapse" size="mini">
          <el-radio-button :label="false">展开</el-radio-button>
          <el-radio-button :label="true">收起</el-radio-button>
        </el-radio-group>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical-demo"
        :collapse="isCollapse"
        @open="handleOpen"
        @close="handleClose"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <!-- 固定仪表盘菜单 -->
        <el-menu-item index="/dashboard" @click="navigate('/dashboard')">
          <i class="el-icon-dashboard"></i>
          <span slot="title">控制面板</span>
        </el-menu-item>

        <!-- 动态生成左侧菜单 -->
        <template v-for="menu in menuTree">
          <template v-if="menu.children && menu.children.length">
            <el-submenu :key="menu.id" :index="menu.id.toString()">
              <template slot="title">
                <i :class="menu.icon"></i>
                <span slot="title">{{ menu.title }}</span>
              </template>
              <template v-for="child in menu.children">
                <el-menu-item
                  v-if="!child.children || !child.children.length"
                  :key="child.id"
                  :index="child.path"
                  @click="navigate(child.path)"
                >
                  <i :class="child.icon"></i>
                  <span>{{ child.title }}</span>
                </el-menu-item>
                <el-submenu
                  v-else
                  :key="child.id"
                  :index="child.id.toString()"
                >
                  <template slot="title">
                    <i :class="child.icon"></i>
                    <span>{{ child.title }}</span>
                  </template>
                  <el-menu-item
                    v-for="grandchild in child.children"
                    :key="grandchild.id"
                    :index="grandchild.path"
                    @click="navigate(grandchild.path)"
                  >
                    <span>{{ grandchild.title }}</span>
                  </el-menu-item>
                </el-submenu>
              </template>
            </el-submenu>
          </template>
          <el-menu-item
            v-else
            :key="menu.id"
            :index="menu.path"
            @click="navigate(menu.path)"
          >
            <i :class="menu.icon"></i>
            <span slot="title">{{ menu.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </div>

    <!-- 主内容区域 -->
    <div class="main-container" :class="{'main-container-top': menuPosition === 'top'}">
      <div v-if="isTopLevelLayout" class="navbar">
        <breadcrumb />
        <div class="right-menu">
          <el-button size="mini" @click="toggleMenuPosition">
            {{ menuPosition === 'left' ? '切换顶部菜单' : '切换侧边菜单' }}
          </el-button>
        </div>
      </div>

      <!-- 添加路由加载状态显示 -->
      <div v-if="$store.state.routeLoading" class="route-loading-overlay">
        <route-loading />
      </div>
      <app-main v-else />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Breadcrumb from './Breadcrumb'
import AppMain from './AppMain'
import RouteLoading from '@/views/RouteLoading'

export default {
  name: 'Layout',
  components: { Breadcrumb, AppMain, RouteLoading },
  computed: {
    ...mapGetters(['menuTree', 'isCollapse', 'menuPosition']),
    activeMenu() {
      return this.$route.path
    },
    menuPositionClass() {
      return `menu-${this.menuPosition}`
    },
  isTopLevelLayout() {
        return this.$route.matched[0]?.meta?.isRootLayout === true;
      }
  },
  methods: {
    ...mapActions(['toggleCollapse', 'setCollapse', 'setRouteLoading']),
    toggleMenuPosition() {
      const newPosition = this.menuPosition === 'left' ? 'top' : 'left'
      this.$store.dispatch('setMenuPosition', newPosition)

      // 切换位置时自动展开菜单
      if (newPosition === 'left' && this.isCollapse) {
        this.setCollapse(false)
      }
    },

    // 处理顶部菜单选择事件
    handleSelect(index) {
      // 使用原始index路径 (已经是规范化路径)
      const path = index;

      // 检查路由是否存在
      const resolved = this.$router.resolve(path);
      const routeExists = resolved.route.matched.length > 0;

      console.log(`选择: ${path}, 路由存在: ${routeExists}`);

      if (path && path !== this.$route.path && routeExists) {
        this.$router.push(path).catch(err => {
          if (err.name !== 'NavigationDuplicated') {
            console.error('导航错误:', err);
          }
        });
      } else if (!routeExists) {
        console.warn(`路由 ${path} 不存在，无法导航`);
        this.setRouteLoading(true);

        // 尝试重新加载路由
        setTimeout(() => {
          this.$router.push('/dashboard');
        }, 1000);
      }
    },

    // 处理左侧菜单导航
    navigate(path) {
      // 使用原始path路径 (已经是规范化路径)
      const routePath = path;

      // 检查路由是否存在
      const resolved = this.$router.resolve(routePath);
      const routeExists = resolved.route.matched.length > 0;

      console.log(`导航到: ${routePath}, 路由存在: ${routeExists}`);

      if (routePath && routePath !== this.$route.path && routeExists) {
        this.$router.push(routePath).catch(err => {
          if (err.name !== 'NavigationDuplicated') {
            console.error('导航错误:', err);
          }
        });
      } else if (!routeExists) {
        console.warn(`路由 ${routePath} 不存在，无法导航`);
        this.setRouteLoading(true);

        // 尝试重新加载路由
        setTimeout(() => {
          this.$router.push('/dashboard');
        }, 1000);
      }
    },

    handleOpen(key, keyPath) {
      console.log('菜单展开:', key, keyPath);
    },
    handleClose(key, key极光Path) {
      console.log('菜单关闭:', key, keyPath);
    }
  }
}
</script>

<style scoped>
.app-wrapper {
  display: flex;
  height: 100vh;
  flex-direction: column;
}

/* 顶部菜单容器 */
.top-menu-container {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1001;
  background-color: #545c64;
}

/* 左侧菜单容器 */
.sidebar-container {
  width: 210px;
  background: #304156;
  overflow: hidden;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

/* 折叠状态下的侧边栏容器 */
.sidebar-container.collapsed {
  width: 64px;
}

.collapse-control {
  padding: 10px;
  background: #304156;
  border-bottom: 1px solid #434d5b;
}

/* 主内容区域 */
.main-container {
  flex: 1;
  overflow: auto;
  transition: margin-left 0.3s;
  margin-left: 210px;
  position: relative;
}

/* 路由加载遮罩层 */
.route-loading-overlay {
  position: absolute;
  top: 50px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 当左侧菜单折叠时，调整主内容区域的左边距 */
.sidebar-container.collapsed + .main-container {
  margin-left: 64px;
}

/* 当菜单在顶部时，主内容区域不需要左边距 */
.main-container-top {
  margin-left: 0 !important;
  margin-top: 60px;
  height: calc(100vh - 60px);
}

/* 如果菜单在顶部，整个app-wrapper应该为column布局 */
.app-wrapper.menu-top {
  flex-direction: column;
}

.navbar {
  height: 50px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
  position: relative;
  z-index: 10;
}

.right-menu {
  margin-left: auto;
  margin-right: 20px;
}

/* 左侧菜单样式 */
.el-menu-vertical-demo {
  border-right: none;
  flex: 1;
  width: 100% !important;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 100% !important;
}
</style>

<style>
/* 全局菜单样式 */
.el-menu--collapse .el-submenu__title span {
  display: none;
}

.el-menu--collapse .el-submenu__title .el-submenu__icon-arrow {
  display: none;
}

.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-menu-item i {
  display: none;
}
</style>
