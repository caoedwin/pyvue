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
        <el-menu-item index="/dashboard">
          <i class="el-icon-dashboard"></i>
          <span>控制面板</span>
        </el-menu-item>

        <template v-for="menu in menuTree">
          <template v-if="menu.children && menu.children.length">
            <el-submenu :key="menu.id" :index="menu.id.toString()">
              <template #title>
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
                  <template #title>
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
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard" @click="navigate('/dashboard')">
          <i class="el-icon-dashboard"></i>
          <span slot="title">控制面板</span>
        </el-menu-item>

        <template v-for="menu in menuTree">
          <template v-if="menu.children && menu.children.length">
            <el-submenu :key="menu.id" :index="menu.id.toString()">
              <template #title>
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
                  <template #title>
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
      const matched = this.$route.matched;
      return matched[0] && matched[0].meta && matched[0].meta.isRootLayout === true;
    }
  },
  methods: {
    ...mapActions(['setCollapse', 'setRouteLoading']),
    toggleMenuPosition() {
      const newPosition = this.menuPosition === 'left' ? 'top' : 'left'
      this.$store.dispatch('setMenuPosition', newPosition)
      if (newPosition === 'left' && this.isCollapse) {
        this.setCollapse(false)
      }
    },

    handleSelect(path) {
      this.navigate(path);
    },

    navigate(path) {
      if (this.$route.path === path) return;

      if (this.$router.resolve(path).route.matched.length) {
        this.$router.push(path).catch(err => {
          if (err.name !== 'NavigationDuplicated') console.error(err);
        });
      } else {
        console.warn(`路由 ${path} 不存在`);
        this.setRouteLoading(true);
        setTimeout(() => this.$router.push('/dashboard'), 1000);
      }
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

.top-menu-container {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1001;
  background-color: #545c64;
}

.sidebar-container {
  width: 210px;
  background: #304156;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar-container.collapsed {
  width: 64px;
}

.collapse-control {
  padding: 10px;
  background: #304156;
  border-bottom: 1px solid #434d5b;
}

.main-container {
  flex: 1;
  overflow: auto;
  transition: margin-left 0.3s;
  margin-left: 210px;
  position: relative;
}

.route-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-container.collapsed + .main-container {
  margin-left: 64px;
}

.main-container-top {
  margin-left: 0 !important;
  margin-top: 60px;
  height: calc(100vh - 60px);
}

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
.el-menu--collapse .el-submenu__title span,
.el-menu--collapse .el-submenu__title .el-submenu__icon-arrow,
.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-menu-item i {
  display: none;
}
</style>
