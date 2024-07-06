from rest_framework import serializers

from .models import UserInfo, Role, Permission, Menu, Books

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        filds = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        filds = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        filds = '__all__'

class BooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books  # 序列化的对象名
        fields = '__all__'  # 序列化的字段名，或者指定字段 fields = ("id","name","age")