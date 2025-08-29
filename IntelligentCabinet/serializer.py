from rest_framework import serializers
from .models import *

class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        # 保留原始字段名 Menu_title 和 url
        fields = '__all__'
        extra_kwargs = {
            # 'position': {'read_only': True},
            'id': {'read_only': True},
        }

class CabinetGridUpdateSerializer(serializers.ModelSerializer):
    # 添加 cabinet 字段为只读主键字段
    cabinet = serializers.PrimaryKeyRelatedField(
        queryset=Cabinet.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = CabinetGrid
        fields = '__all__'
        extra_kwargs = {
            # 'position': {'read_only': True},
            'id': {'read_only': True},
            'row': {'read_only': True},  # 行创建后不可修改
            'col': {'read_only': True}  # 列创建后不可修改
        }


class CabinetCreateSerializer(serializers.ModelSerializer):
    gridData = serializers.ListField(
        child=serializers.ListField(
            child=serializers.DictField()
        ),
        write_only=True,
        required=True
    )

    class Meta:
        model = Cabinet
        fields = ['name', 'location', 'description', 'rows', 'cols', 'gridData']
        extra_kwargs = {
            'name': {'required': True},
            'rows': {'min_value': 1, 'max_value': 20},
            'cols': {'min_value': 1, 'max_value': 20}
        }

    def validate(self, data):
        # 验证柜体名称唯一性
        if Cabinet.objects.filter(name=data['name']).exists():
            raise serializers.ValidationError("柜体名称已存在")

        # 验证网格数据结构
        grid_data = data['gridData']
        rows = data['rows']
        cols = data['cols']

        if len(grid_data) != rows:
            raise serializers.ValidationError(f"行数不匹配，应为 {rows} 行")

        for i, row in enumerate(grid_data):
            if len(row) != cols:
                raise serializers.ValidationError(f"第 {i+1} 行列数不匹配，应为 {cols} 列")

            for j, cell in enumerate(row):
                if 'position' not in cell:
                    raise serializers.ValidationError(f"第 {i+1} 行第 {j+1} 列缺少位置信息")

                # 验证位置格式 (例如 A1, B2)
                position = cell['position']
                if not (len(position) >= 2 and position[0].isalpha() and position[1:].isdigit()):
                    raise serializers.ValidationError(f"位置 '{position}' 格式无效，应为字母+数字格式")

        return data

    def create(self, validated_data):
        grid_data = validated_data.pop('gridData')
        cabinet = Cabinet.objects.create(**validated_data)

        # 批量创建关联的柜格
        grid_instances = []
        for row_index, row in enumerate(grid_data):
            for col_index, cell in enumerate(row):
                grid_instances.append(CabinetGrid(
                    cabinet=cabinet,
                    row=row_index + 1,
                    col=col_index + 1,
                    position=cell['position'],
                    status=cell.get('status', 0),
                    Customer=cell.get('Customer', ''),
                    ProCode=cell.get('ProCode', ''),
                    CampalCode=cell.get('CampalCode', ''),
                    Brow_at=cell.get('borrowDate'),
                    BrowReson=cell.get('BrowReson', ''),
                    Take_at=cell.get('takeoutDate'),
                    TakeReson=cell.get('TakeReson', ''),
                    Back_at=cell.get('reserveDate'),
                    user=cell.get('user', ''),
                    phone=cell.get('phone', ''),
                    notes=cell.get('notes', ''),
                    creator=self.context['request'].session.get('account_pyvue', '')
                ))

        CabinetGrid.objects.bulk_create(grid_instances)
        return cabinet


class CabinetGridSerializer(serializers.ModelSerializer):
    # 保留原始字段名 perms
    cabinet = CabinetSerializer()

    class Meta:
        model = CabinetGrid
        fields = '__all__'
        # fields = ('id', 'cabinet', 'row', 'col', 'position', 'status', 'Customer', 'ProCode', 'CampalCode', 'Brow_at', 'BrowReson', 'Take_at', 'TakeReson', 'Back_at', 'user', 'phone', 'notes', 'creator', 'created_at', 'updated_at')


class GridRecordSerializer(serializers.ModelSerializer):
    # 保留原始字段名 role
    grid = CabinetGridSerializer()
    menu_tree = serializers.SerializerMethodField()

    class Meta:
        model = GridRecord
        # 保留所有原始字段名
        fields = '__all__'
