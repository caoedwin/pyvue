from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializer import CabinetSerializer, CabinetGridSerializer, GridRecordSerializer, CabinetGridUpdateSerializer, CabinetCreateSerializer
from .models import Cabinet, CabinetGrid, GridRecord
from backend01.models import UserInfo
import datetime
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

#新增柜体
@method_decorator(csrf_exempt, name='dispatch')
class CabinetListView(APIView):
    """柜体列表和创建"""

    def get(self, request):
        cabinets = Cabinet.objects.all()
        serializer = CabinetSerializer(cabinets, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            is_admin = False
            # 添加用户权限信息
            online_user = request.session.get('account_pyvue', '')
            # print(online_user, "online_user")

            if online_user:
                user = UserInfo.objects.filter(account=online_user).first()
                # print(user)
                if user:
                    roles = user.role.values_list('name', flat=True)
                    # print(roles)
                    is_admin = any(role in ['管理员', 'CabinetManageAdmin'] for role in roles)
            # 从 request.data 中提取 'newCabinet' 数据
            cabinet_data = request.data.get('newCabinet', {})

            # 添加 context 传递 request 对象
            serializer = CabinetCreateSerializer(
                data=cabinet_data,
                context={'request': request}  # 关键修复
            ) # 使用 cabinet_data
            # print(serializer.is_valid(), request.data, "request.data.get('gridData', [])")

            if serializer.is_valid():
                with transaction.atomic():
                    cabinet = serializer.save()
                    # 创建关联的柜格
                    grids_data = request.data.get('gridData', [])
                    for row in grids_data:
                        for cell in row:
                            CabinetGrid.objects.create(
                                cabinet=cabinet,
                                row=cell['rowIndex'],
                                col=cell['colIndex'],
                                position=cell['position'],
                                status=cell['status'],
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
                                creator=request.session.get('account_pyvue', '')
                            )
                return Response({
                    "errMsg": "",
                    "cabinets": [CabinetSerializer(cabinet).data],
                    "isAdmin": is_admin,  # 根据实际情况获取
                    "currentUser": {
                        "name": request.user.username,
                        "phone": ""
                    },
                    "CustomerOptions": [choice[0] for choice in CabinetGrid.Customer_CHOICES]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "errMsg": serializer.errors,
                    "cabinets": '',
                    "isAdmin": is_admin,  # 根据实际情况获取
                    "currentUser": {
                        "name": request.session.get("account_pyvue"),
                        "phone": ""
                    },
                    "CustomerOptions": [choice[0] for choice in CabinetGrid.Customer_CHOICES]
                })#, status=status.HTTP_400_BAD_REQUEST) 400前端直接返回异常
        except ValidationError as e:
            # 将DRF的验证错误转换为统一格式
            return Response({
                "errMsg": "创建柜体失败: " + str(e.detail),
                "cabinets": [],
                "isAdmin": is_admin,
                "currentUser": {"name": "", "phone": ""},
                "CustomerOptions": []
            })#, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # 处理其他异常
            return Response({
                "errMsg": f"服务器错误: {str(e)}",
                "cabinets": [],
                "isAdmin": is_admin,
                "currentUser": {"name": "", "phone": ""},
                "CustomerOptions": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#删除柜体
@method_decorator(csrf_exempt, name='dispatch')
class CabinetDetailView(APIView):
    """柜体详情和删除"""

    def delete(self, request, pk):
        try:
            print(pk)
            cabinet = Cabinet.objects.get(pk=pk)
            if cabinet.grids.exclude(status=0).exists():
                return Response(
                    {"error": "柜体中存在非空闲柜格，无法删除"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cabinet.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cabinet.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CabinetGridView(APIView):
    """柜格管理基类"""

    def get_grid(self, pk):
        try:
            return CabinetGrid.objects.get(pk=pk)
        except CabinetGrid.DoesNotExist:
            return None

#更新柜格信息（管理员操作）
@method_decorator(csrf_exempt, name='dispatch')
class GridUpdateView(CabinetGridView):
    """更新柜格信息（管理员操作）"""

    def patch(self, request, pk):
        gridinfo = request.data['gridinfo']

        # 提取 cabinet ID 而不是整个对象
        if 'cabinet' in gridinfo and isinstance(gridinfo['cabinet'], dict):
            gridinfo['cabinet'] = gridinfo['cabinet']['id']

        # 获取柜格实例
        grid = self.get_grid(gridinfo['id'])
        if not grid:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 创建新的数据副本，移除不需要的字段
        cleaned_data = {
            key: value for key, value in gridinfo.items()
            if key not in ['rowIndex', 'colIndex', 'created_at', 'updated_at', 'cabinet']#这些都不是数据库里面需要的数据
        }

        # 添加 cabinet ID（如果缺失）
        if 'cabinet' not in cleaned_data:
            cleaned_data['cabinet'] = grid.cabinet.id

        serializer = CabinetGridUpdateSerializer(grid, data=cleaned_data, partial=True)

        if serializer.is_valid():
            old_status = grid.status
            grid = serializer.save()

            # 创建状态变更记录
            GridRecord.objects.create(
                grid=grid,
                action='update',
                old_status=old_status,
                new_status=grid.status,
                Customer=grid.Customer,
                ProCode=grid.ProCode,
                CampalCode=grid.CampalCode,
                Brow_at=grid.Brow_at,
                BrowReson=grid.BrowReson,
                Take_at=grid.Take_at,
                TakeReson=grid.TakeReson,
                Back_at=grid.Back_at,
                user=grid.user,
                phone=grid.phone,
                notes=grid.notes
            )
            return Response(CabinetGridSerializer(grid).data)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#用户预约操作
@method_decorator(csrf_exempt, name='dispatch')
class UserReserveView(CabinetGridView):
    """用户预约操作"""

    def post(self, request, pk):
        # print('用户预约操作', pk, request.data)
        gridinfo = request.data['cellData']

        # 提取 cabinet ID 而不是整个对象
        if 'cabinet' in gridinfo and isinstance(gridinfo['cabinet'], dict):
            gridinfo['cabinet'] = gridinfo['cabinet']['id']

        # 获取柜格实例
        grid = self.get_grid(pk)
        if not grid:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 创建新的数据副本，移除不需要的字段
        cleaned_data = {
            key: value for key, value in gridinfo.items()
            if key not in ['rowIndex', 'colIndex', 'created_at', 'updated_at', 'cabinet']  # 这些都不是数据库里面需要的数据
        }

        # 添加 cabinet ID（如果缺失）
        if 'cabinet' not in cleaned_data:
            cleaned_data['cabinet'] = grid.cabinet.id

        serializer = CabinetGridUpdateSerializer(grid, data=cleaned_data, partial=True)
        if serializer.is_valid():
            # 设置当前用户为借用人
            data = serializer.validated_data
            data['user'] = request.session.get('account_pyvue', '')
            grid = serializer.save()

            return Response(CabinetGridSerializer(grid).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCancelReserveView(CabinetGridView):
    """用户取消预约"""

    def post(self, request, pk):
        grid = self.get_grid(pk)
        if not grid:
            return Response(status=status.HTTP_404_NOT_FOUND)

        reset_data = {
            'status': 0,
            'Customer': '',
            'ProCode': '',
            'CampalCode': '',
            'Brow_at': None,
            'BrowReson': '',
            'user': '',
            'phone': '',
            'notes': ''
        }
        serializer = CabinetGridUpdateSerializer(grid, data=reset_data, partial=True)
        if serializer.is_valid():
            grid = serializer.save()
            return Response(CabinetGridSerializer(grid).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#管理员确认借出
@method_decorator(csrf_exempt, name='dispatch')
class ConfirmBorrowView(CabinetGridView):
    """管理员确认借出"""

    def post(self, request, pk):
        grid = self.get_grid(pk)
        if not grid:
            return Response(status=status.HTTP_404_NOT_FOUND)

        update_data = {
            'status': request.data['cellData'].get('status', grid.status),
            'Brow_at': datetime.datetime.now()
        }
        # print(request.data,update_data)
        serializer = CabinetGridUpdateSerializer(grid, data=update_data, partial=True)
        if serializer.is_valid():
            old_status = grid.status
            grid = serializer.save()

            # 创建借出记录
            GridRecord.objects.create(
                grid=grid,
                action='borrow',
                old_status=old_status,
                new_status=grid.status,
                Customer=grid.Customer,
                ProCode=grid.ProCode,
                CampalCode=grid.CampalCode,
                Brow_at=grid.Brow_at,
                BrowReson=grid.BrowReson,
                user=grid.user,
                phone=grid.phone,
                notes=grid.notes
            )
            return Response(CabinetGridSerializer(grid).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 类似实现以下操作类：
# - UserTakeOutView（用户取出）
# - UserCancelTakeOutView（用户取消取出）
# - UserReturnView（用户归还）
#获取柜体数据
class CabinetGridListView(APIView):
    """获取所有柜体数据（供前端初始化使用）"""
    # authentication_classes = [SessionAuthentication]  # 添加这一行
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        errMsg = ''
        is_admin = False
        online_user = ''
        data = []
        try:
            django_request = request._request
            # print(dict(django_request.session), request.session.session_key)

            # 添加用户权限信息
            online_user = django_request.session.get('account_pyvue', '')
            print(f"Session user: {online_user}")
            # print('init-get')
            cabinets = Cabinet.objects.all()
            data = []
            for cabinet in cabinets:
                cabinet_data = CabinetSerializer(cabinet).data
                cabinet_data['gridData'] = []

                # 按行分组柜格
                rows = {}
                for grid in cabinet.grids.all().order_by('row', 'col'):
                    if grid.row not in rows:
                        rows[grid.row] = []
                    rows[grid.row].append(CabinetGridSerializer(grid).data)

                # 转换为二维数组
                for row_index in sorted(rows.keys()):
                    cabinet_data['gridData'].append(rows[row_index])

                data.append(cabinet_data)

            # 添加用户权限信息
            online_user = request.session.get('account_pyvue', '')
            # print(online_user, "online_user")

            if online_user:
                user = UserInfo.objects.filter(account=online_user).first()
                # print(user)
                if user:
                    roles = user.role.values_list('name', flat=True)
                    # print(roles)
                    is_admin = any(role in ['管理员', 'CabinetManageAdmin'] for role in roles)
        except Exception as e:
            errMsg = str(e)

        # print(data)
        return Response({
            "errMsg": errMsg,
            'cabinets': data,
            'isAdmin': is_admin,
            'currentUser': {'name': online_user, 'phone': ''},
            'CustomerOptions': [choice[0] for choice in CabinetGrid.Customer_CHOICES]
        })