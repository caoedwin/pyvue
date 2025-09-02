from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class Imgs(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField(upload_to='photos/')

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Menu(models.Model):
    title = models.CharField(max_length=32, unique=True)
    parent = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)
    icon = models.CharField(max_length=32, default='el-icon-menu')
    order = models.IntegerField(default=0, verbose_name='排序')
    path = models.CharField(max_length=128, blank=True, null=True, verbose_name='路由路径')

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = verbose_name
        ordering = ['order']

    def __str__(self):
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)


class Permission(models.Model):
    Menu_title = models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)#前端获取到的动态路由里面的url，不可以与后端的实际的url重复否则可能就直接访问后端api接口而不是前端网页，甚至/IntelligentCabinet/cabinetsmanage/在后端url文件里都没有，更重要的是components跳转到哪个vue文档
    components = models.CharField(max_length=128, default='')
    menu = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.menu}---{self.Menu_title}'


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    perms = models.ManyToManyField(Permission)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class UserInfoManager(BaseUserManager):
    def create_user(self, account, password=None, **extra_fields):
        if not account:
            raise ValueError('必须提供账号')
        user = self.model(account=account, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, account, password=None, **extra_fields):
        # 确保正确设置所有权限标志
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # 添加以下两个字段的设置
        extra_fields.setdefault('is_authenticated', True)
        extra_fields.setdefault('is_anonymous', False)

    def get_by_natural_key(self, account):
        return self.get(account=account)


class UserInfo(AbstractBaseUser):
    SeatChoice = (
        ('KS-Plant5', 'KS-Plant5'),
        ('KS-Plant3', 'KS-Plant3'),
        ('KS-Plant2', 'KS-Plant2'),
        ('CQ', 'CQ'),
        ('CD', 'CD'),
        ('TPE', 'TPE'),
        ('PCP', 'PCP'),
        ('LKE', 'LKE'),
    )
    DEPARTMENT_CHOICES = (
        (1, '测试部门'),
        (2, '开发部门'),
        (3, 'PM'),
        (4, '其它部门'),
    )

    account = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=32)
    CNname = models.CharField(max_length=32, default='')
    Tel = models.CharField(max_length=32, null=True, blank=True, default='')
    Seat = models.CharField(max_length=108, choices=SeatChoice, default='KS-Plant5')
    email = models.EmailField()
    department = models.IntegerField(verbose_name='部门', choices=DEPARTMENT_CHOICES, default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_SVPuser = models.BooleanField(default=False)
    role = models.ManyToManyField("Role")
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField('auth.Group', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', blank=True)
    Photo = models.ManyToManyField(Imgs, blank=True, verbose_name='图片表')
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    USERNAME_FIELD = 'account'
    REQUIRED_FIELDS = ['email', 'username']
    objects = UserInfoManager()

    # 添加以下方法
    def get_short_name(self):
        """返回用户的简称（通常用用户名）"""
        return self.username

    def get_full_name(self):
        """返回用户全名（使用中文名或用户名）"""
        return self.CNname if self.CNname else self.username

    @property
    def is_anonymous(self):
        """始终返回False，因为这是已认证用户"""
        return False

    @property
    def is_authenticated(self):
        """始终返回True，因为这是已认证用户"""
        return True

    def has_perm(self, perm, obj=None):
        """用户是否有特定权限?"""
        return self.is_staff or self.is_superuser

    def has_module_perms(self, app_label):
        """用户是否有权限访问app?"""
        return self.is_staff or self.is_superuser

    def get_all_permissions(self, obj=None):
        """获取所有权限"""
        return set()  # 如果使用简单的权限系统，可以返回空集

    def get_user_permissions(self, obj=None):
        """获取用户特定权限"""
        return set()  # 如果使用简单的权限系统，可以返回空集

    def get_menu_tree(self):
        # 获取用户有权限的菜单及其关联的权限
        accessible_permissions = Permission.objects.filter(
            role__userinfo=self
        ).select_related('menu').prefetch_related('menu__parent').distinct()

        # 获取所有相关菜单ID（包括祖先菜单）
        all_menu_ids = set()
        # 创建菜单ID到权限信息的映射（包括url和component）
        menu_to_permission = {}
        for perm in accessible_permissions:
            menu = perm.menu
            if menu:
                # 添加当前菜单及其所有祖先
                current = menu
                while current:
                    if current.id not in all_menu_ids:
                        all_menu_ids.add(current.id)
                        # 如果是当前菜单（非祖先），存储权限信息
                        if current == menu:
                            menu_to_permission[current.id] = {
                                'url': perm.url,
                                'component': perm.components
                            }
                        current = current.parent
                    else:
                        break  # 避免循环引用

        # 获取所有菜单对象
        all_menus = Menu.objects.filter(id__in=all_menu_ids).select_related('parent')
        menu_dict = {menu.id: menu for menu in all_menus}

        # 递归构建菜单树
        def build_tree(menu_id):
            menu = menu_dict[menu_id]
            # 获取当前菜单的权限信息（如果有）
            perm_info = menu_to_permission.get(menu_id, {})
            node = {
                "id": menu.id,
                "title": menu.title,
                "icon": menu.icon,
                "path": perm_info.get('url', menu.path),  # 优先使用权限URL，如果没有则使用菜单路径
                "component": perm_info.get('component', None),  # 添加component字段
                "children": []
            }

            # 查找直接子菜单
            children = [m for m in menu_dict.values() if m.parent_id == menu_id]

            # 递归构建子菜单树
            for child in children:
                node["children"].append(build_tree(child.id))

            # 按order字段排序
            node["children"].sort(key=lambda x: menu_dict[x["id"]].order if hasattr(menu_dict[x["id"]], 'order') else 0)

            return node

        # 构建完整菜单树
        root_menus = [m for m in menu_dict.values() if m.parent_id is None]
        menu_tree = [build_tree(root.id) for root in root_menus]
        print(menu_tree)
        return menu_tree

    def __str__(self):
        return self.username


class Books(models.Model):
    name = models.CharField(max_length=30)
    author = models.CharField(max_length=30, blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)