from django.contrib import admin
from backend01.models import Books
# Register your models here.
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