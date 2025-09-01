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
        <!-- 添加顶部菜单注销按钮 -->

          <!-- 修改：将用户名和注销整合到下拉菜单 -->
        <el-submenu index="user-menu" class="user-submenu">
          <template #title>
            <i class="el-icon-user"></i>
            <span>{{ userName }}</span>
          </template>
          <el-menu-item @click="confirmLogout">
            <i class="el-icon-switch-button"></i>
            <span>注销</span>
          </el-menu-item>
        </el-submenu>
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
        <!-- 修改：将用户信息改为子菜单 -->
        <el-submenu index="user-menu" class="user-submenu">
          <template #title>
            <i class="el-icon-user"></i>
            <span slot="title">{{ userName }}</span>
          </template>
          <el-menu-item @click="confirmLogout">
            <i class="el-icon-switch-button"></i>
            <span>注销</span>
          </el-menu-item>
        </el-submenu>
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
  data() {
    return {
      topMenuHeight: 60 // 默认高度
    }
  },
  computed: {
    // mapGetters(['user'])从 Vuex store 中获取数据,对应store/index.js里面的getters里面的
    ...mapGetters(['menuTree', 'isCollapse', 'menuPosition', 'currentUser']),
    activeMenu() {
      return this.$route.path
    },
    menuPositionClass() {
      return `menu-${this.menuPosition}`
    },
    isTopLevelLayout() {
      const matched = this.$route.matched;
      return matched[0] && matched[0].meta && matched[0].meta.isRootLayout === true;
    },
    // 获取用户名称
    userName() {
      //console.log("this.user", this.user)
      return this.currentUser ?.username || '用户';
    },
    mainContainerStyle() {
      if (this.menuPosition === 'top') {
        return {
          marginTop: `${this.topMenuHeight}px`,
          height: `calc(100vh - ${this.topMenuHeight}px)`
        }
      }
      return {}
    }
  },
  mounted() {
    this.updateTopMenuHeight();
    window.addEventListener('resize', this.updateTopMenuHeight);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateTopMenuHeight);
  },
  methods: {
    ...mapActions(['setCollapse', 'setRouteLoading']),
    updateTopMenuHeight() {
      if (this.menuPosition === 'top' && this.$refs.topMenu) {
        // 获取菜单的实际高度
        this.topMenuHeight = this.$refs.topMenu.$el.clientHeight;
      }
    },
    toggleMenuPosition() {
      const newPosition = this.menuPosition === 'left' ? 'top' : 'left'
      this.$store.dispatch('setMenuPosition', newPosition)
      if (newPosition === 'left' && this.isCollapse) {
        this.setCollapse(false)
      }
      // 菜单位置切换后更新高度
      this.$nextTick(() => {
        this.updateTopMenuHeight();
      });
    },

    handleMenuSelect(path) {
      // 排除注销项
      if (path === 'logout') return;

      // 关闭所有展开的子菜单
      if (this.$refs.topMenu) {
        this.$refs.topMenu.closeMenu();
      }

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

      // 导航后更新菜单高度
      this.$nextTick(this.updateTopMenuHeight);
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
    },
    toggleCollapse() {
      this.$store.commit('TOGGLE_COLLAPSE');
    },
    handleSelect(key, keyPath) {
      console.log(key, keyPath);
    },

    // 添加确认弹框
    confirmLogout() {
      this.$confirm('确定要注销登录吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.handleLogout();
      }).catch(() => {
        // 取消操作
      });
    },
    handleLogout() {
      // 清除本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('menuTree');
      localStorage.removeItem('user');
      // 重置 Vuex 状态
      this.$store.commit('SET_MENU_TREE', []);
      this.$store.commit('SET_TOKEN', null);
      this.$store.commit('SET_USER', null);

      // 跳转到登录页面
      this.$router.push('/login');
      this.$message({
        type: 'success',
        message: '注销成功!'
      });
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
  padding: 0 20px;
  height: 50px;
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.right-menu {
  margin-left: auto;
}

.el-menu-vertical-demo {
  border-right: none;
  flex: 1;
  width: 100% !important;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 100% !important;
}

.el-menu--collapse .el-submenu__title span,
.el-menu--collapse .el-submenu__title .el-submenu__icon-arrow,
.el-menu--collapse .el-menu-item span,
.el-menu--collapse .el-menu-item i {
  display: none;
}

/* 新增样式 */
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}

/* 顶部菜单样式 */
.top-menu-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  background-color: #545c64;
  overflow: visible; /* 允许子菜单显示 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: height 0.3s ease;
}


.top-menu {
  display: flex;
  align-items: center;
}

/* 修复顶部菜单右侧区域 */
.top-menu-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.user-name {
  color: #fff;
  margin-right: 15px;
  font-size: 14px;
}

.logout-button {
  color: #409EFF !important; /* 蓝色文字，与图片一致 */
  padding: 0 10px;
  font-size: 14px;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 左侧菜单样式 */
.sidebar-container {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1001;
  width: 210px;
  height: 100%;
  transition: width 0.3s;
  background-color: #304156;
}

.sidebar-container.collapsed {
  width: 64px;
}

.toggle-button {
  height: 40px;
  line-height: 40px;
  text-align: center;
  color: #fff;
  background-color: #263445;
  cursor: pointer;
}

/* 左侧菜单底部样式 */
.sidebar-bottom {
  position: absolute;
  bottom: 0;
  width: 100%;
  background-color: #304156;
  border-top: 1px solid #434d5b;
}

.user-info {
  padding: 12px 20px;
  color: #bfcbd9;
  display: flex;
  align-items: center;
}

.user-info i {
  margin-right: 8px;
  font-size: 16px;
}

.logout-menu-item {
  border-top: 1px solid #434d5b;
  background-color: #304156 !important;
  color: #bfcbd9 !important;
}

.logout-menu-item:hover {
  background-color: #263445 !important;
  color: #409EFF !important;
}

/* 折叠状态下调整样式 */
.sidebar-container.collapsed .sidebar-bottom {
  width: 64px;
}

.sidebar-container.collapsed .user-info,
.sidebar-container.collapsed .logout-menu-item span {
  display: none;
}

/* 主内容区域 */
.main-container {
  min-height: 100%;
  transition: margin-left 0.3s;
  margin-left: 210px;
  position: relative;
}

/* 修复主内容区域 */
.main-container-top {
  margin-top: 60px; /* 初始值 */
  height: calc(100vh - 60px); /* 初始值 */
  transition: margin-top 0.3s ease;
}

/* 修复菜单项样式 */
.el-menu--horizontal .el-submenu .el-submenu__title {
  height: 60px; /* 固定高度 */
  line-height: 60px; /* 垂直居中 */
}

.el-menu--horizontal > .el-menu-item {
  height: 60px; /* 固定高度 */
  line-height: 60px; /* 垂直居中 */
}

/* 菜单项活动状态修复 */
.el-menu-item.is-active {
  border-bottom: 3px solid #ffd04b !important;
}

/* 子菜单样式优化 */
.el-menu--horizontal .el-menu--popup {
  padding: 0;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}

.el-menu--horizontal .el-menu--popup .el-menu-item {
  min-width: 160px;
  height: 48px;
  line-height: 48px;
}

/* 修复用户菜单位置 */
.user-submenu {
  float: right !important;
  margin-right: 20px;
}


.sidebar-container.collapsed + .main-container {
  margin-left: 64px;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .top-menu-container {
    overflow-x: auto;
    white-space: nowrap;
  }

  .el-menu--horizontal {
    display: inline-block;
    min-width: 100%;
  }
}
</style>
