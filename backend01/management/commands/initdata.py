# backend01/management/commands/initdata.py
# 在Terminal窗口运行python manage.py initdata
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from backend01.models import Menu, Permission, Role, UserInfo


class Command(BaseCommand):
    help = 'Initialize application data'

    def handle(self, *args, **options):
        # 检查数据是否已存在
        if Menu.objects.exists():
            self.stdout.write(self.style.WARNING('Data already exists. Skipping initialization.'))
            return

        # 创建菜单
        main_menu = Menu.objects.create(
            title='系统管理',
            icon='el-icon-setting',
            order=1
        )
        user_menu = Menu.objects.create(
            title='用户管理',
            icon='el-icon-user',
            parent=main_menu,
            path='/user',
            order=1
        )
        role_menu = Menu.objects.create(
            title='角色管理',
            icon='el-icon-s-custom',
            parent=main_menu,
            path='/role',
            order=2
        )

        # 创建权限
        user_perm = Permission.objects.create(
            Menu_title='用户管理权限',
            url='/api/user/',
            menu=user_menu
        )
        role_perm = Permission.objects.create(
            Menu_title='角色管理权限',
            url='/api/role/',
            menu=role_menu
        )

        # 创建角色
        admin_role = Role.objects.create(name='管理员')
        admin_role.perms.add(user_perm, role_perm)

        # 创建管理员用户
        if not UserInfo.objects.filter(account='edwin').exists():
            admin_user = UserInfo.objects.create(
                account='edwin',
                username='Admin',
                email='admin@example.com',
                department=2,
                is_staff=True,
                is_active=True,
                is_superuser=True,
                password=make_password('DCT@2019')
            )
            admin_user.role.add(admin_role)
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        self.stdout.write(self.style.SUCCESS('Data initialized successfully'))