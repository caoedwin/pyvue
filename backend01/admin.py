from django.contrib import admin
from backend01.models import Books
# Register your models here.
from django.contrib import admin
from .models import UserInfo, Role, Permission, Menu, Imgs
from django.contrib.auth.admin import UserAdmin

# from extraadminfilters.filters import UnionFieldListFilter

# Register your models here.
admin.site.site_url = '/index/'

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('title','parent','icon','order','path',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('title',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-title',)
    #后台数据列表排序方式
    list_display_links = ('title',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('title',)  # 过滤器
    search_fields = ('title',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('Menu_title','url','components','menu',)
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('Menu_title','url',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-url',)
    #后台数据列表排序方式
    list_display_links = ('Menu_title','url',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('Menu_title','url',)  # 过滤器
    search_fields = ('Menu_title','url',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields' : ('name','perms')
        }),
        # ('Advanced options',{
        #     'classes': ('collapse',),
        #     'fields' : ('Start_time', 'End_time', 'Result_time','Result','Comments')
        # }),
    )
    list_display = ('name', 'show_pers', 'show_users')
    # 列表里显示想要显示的字段
    def show_users(self, obj):
        user_list = []
        for user in obj.userinfo_set.all():
            # print(user)
            user_list.append(user.username)
        return '， '.join(user_list)

    show_users.short_description = '成員'  # 设置表头
    def show_pers(self, obj):
        per_list = []
        for perm in obj.perms.all():
            print(perm,1)
            per_list.append(perm.url)
        return '， '.join(per_list)

    show_pers.short_description = '權限'  # 设置表头
    filter_horizontal = ('perms',)
    # 列表里显示想要显示的字段
    list_per_page = 200
    # 满50条数据就自动分页
    ordering = ('-name',)
    #后台数据列表排序方式
    list_display_links = ('name',)
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Tester',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    list_filter = ('name',)  # 过滤器
    search_fields = ('name',)  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选
    filter_horizontal = ('perms',)


class CustomUserAdmin(UserAdmin):
    # 修改列表显示的字段
    list_display = ('account', 'username', 'CNname', 'email', 'is_staff', 'is_superuser', 'is_SVPuser')

    # 其他设置保持不变...
    fieldsets = (
        (None, {'fields': ('account', 'password')}),
        ('个人信息', {'fields': ('username', 'CNname', 'email', 'Tel', 'Seat', 'department')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_SVPuser', 'role', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account', 'password1', 'password2'),
        }),
    )

    search_fields = ('account', 'username', 'email')
    ordering = ('account',)
    filter_horizontal = ('role', 'groups', 'user_permissions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'department')

admin.site.register(UserInfo, CustomUserAdmin)


@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'add_time')
    # 列表里显示想要显示的字段
    list_per_page = 500
    # 满50条数据就自动分页
    ordering = ('-author',)
    # 后台数据列表排序方式
    list_display_links = ('name', 'author', 'add_time')
    # 设置哪些字段可以点击进入编辑界面
    # list_editable = ('Object',)
    # 筛选器
    # list_filter = ('Customer','Project', 'Unit', 'Phase', 'Tester', 'Testitem','Result', 'Start_time', 'End_time', 'Result_time','Item_Des', 'Comments')  # 过滤器
    # list_filter = ('Customer','Phase', 'ItemNo_d', 'Item_d', 'TestItems')  # 过滤器
    search_fields = ('name', 'author', 'add_time')  # 搜索字段
    # date_hierarchy = 'Start_time'  # 详细时间分层筛选