from rest_framework import serializers
from .models import UserInfo, Menu, Permission, Role, Books


# 因为菜单树是一个动态构建的字典结构，我们使用Serializer来手动序列化
class MenuTreeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    icon = serializers.CharField()
    path = serializers.CharField()
    children = serializers.ListField(child=serializers.DictField())


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        # 保留原始字段名 Menu_title 和 url
        fields = ('id', 'Menu_title', 'url')


class RoleSerializer(serializers.ModelSerializer):
    # 保留原始字段名 perms
    perms = PermissionSerializer(many=True)

    class Meta:
        model = Role
        fields = ('id', 'name', 'perms')


class UserInfoSerializer(serializers.ModelSerializer):
    # 保留原始字段名 role
    role = RoleSerializer(many=True)
    menu_tree = serializers.SerializerMethodField()

    class Meta:
        model = UserInfo
        # 保留所有原始字段名
        fields = ('id', 'account', 'username', 'CNname', 'Tel', 'Seat', 'email',
                  'department', 'is_active', 'is_staff', 'is_SVPuser', 'role', 'Photo', 'menu_tree')
        extra_kwargs = {'password': {'write_only': True}}

    def get_menu_tree(self, obj):
        # 使用自定义的菜单树序列化器
        return MenuTreeSerializer(obj.get_menu_tree(), many=True).data

class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books  # 序列化的对象名
        fields = '__all__'  # 序列化的字段名，或者指定字段 fields = ("id","name","age")