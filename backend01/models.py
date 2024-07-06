from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-

class UserInfo(models.Model):
    """
    用户：划分角色
    """
    account = models.CharField(max_length=32,unique=True)
    password = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    email = models.EmailField()
    role = models.ManyToManyField("Role")

    class Meta:
        verbose_name = 'UserInfo'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class Role(models.Model):
    """
    角色：绑定权限
    """
    name = models.CharField(max_length=32, unique=True)
    perms=models.ManyToManyField('Permission')

    class Meta:
        verbose_name = 'Role'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name

class Permission(models.Model):
    """
    角色：绑定权限
    """
    Menu_title=models.CharField(max_length=32, unique=True)
    url = models.CharField(max_length=128, unique=True)
    menu = models.ForeignKey("Menu", null=True, blank=True, on_delete=True)
    class Meta:
        verbose_name = 'Permission'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示带菜单前缀的权限
        return '{menu}---{permission}'.format(menu=self.menu, permission=self.Menu_title)

class Menu(models.Model):
    """
    菜单
    """
    title = models.CharField(max_length=32, unique=True)
    parent = models.ForeignKey("Menu", null=True, blank=True,on_delete=True)
    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单
    class Meta:
        verbose_name = 'Menu'#不写verbose_name, admin中默认的注册名会加s
        verbose_name_plural = verbose_name
    def __str__(self):
        # 显示层级菜单
        title_list = [self.title]
        p = self.parent
        while p:
            title_list.insert(0, p.title)
            p = p.parent
        return '-'.join(title_list)

class Books(models.Model):
    name = models.CharField(max_length=30)
    author = models.CharField(max_length=30, blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)
