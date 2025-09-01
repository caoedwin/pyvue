<template>
  <div id="cabinet-app">
    <div class="cabinet-container">
      <div class="cabinet-main-header">
        <h1>智能柜管理系统</h1>
        <p>动态生成柜格布局，实时监控柜格状态</p>
      </div>

      <!-- 柜体管理栏 -->
      <div class="cabinets-bar">
        <el-button :loading="elbuttonloading" v-if="isAdmin" type="primary" icon="el-icon-plus" @click="openAddCabinetDialog">添加柜体</el-button>

        <div class="cabinets-tabs">
          <div v-for="(cabinet, index) in cabinets"
               :key="cabinet.id"
               class="cabinet-tab"
               :class="{active: currentCabinetId === cabinet.id}"
               @click="setActiveCabinet(cabinet.id)">
            {{ cabinet.name }}
            <!-- 柜体标签上的删除按钮 -->
            <span v-if="isAdmin" class="delete-cabinet-btn"
                  @click.stop="confirmRemoveCabinet(cabinet.id, cabinet.name)"
                  title="删除柜体">×</span>
          </div>
        </div>
      </div>

      <div class="control-panel" v-if="isAdmin_origin">
        <div class="control-row">
          <el-radio-group v-model="isAdmin" size="medium">
            <el-radio-button :label="true" style="padding: 8px 20px; border-radius: 20px;">管理员</el-radio-button>
            <el-radio-button :label="false" style="padding: 8px 20px; border-radius: 20px;">普通用户</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <!-- 柜体循环展示区 -->
      <div v-for="cabinet in cabinets" :key="cabinet.id" class="cabinet-section">
        <div class="cabinet-header">
          <h2>柜体 {{ cabinet.name }}</h2>
          <!-- 柜体详情中的删除按钮 -->
          <el-button
            v-if="isAdmin"
            type="text"
            icon="el-icon-delete"
            @click="confirmRemoveCabinet(cabinet.id, cabinet.name)"
            style="color: #f56c6c;">删除此柜体</el-button>
        </div>

        <div class="grid-container">
          <div class="grid-table-container" v-if="cabinet.gridData && cabinet.gridData.length">
            <el-table
              :data="transformGridData(cabinet.gridData)"
              v-loading="tableloading"
              class="grid-table"
              :show-header="false"
              border
              :row-style="{height: '120px'}"
              :cell-style="{padding: '0', textAlign: 'center', verticalAlign: 'middle'}">
              <el-table-column
                v-for="(col, colIndex) in cabinet.cols"
                :key="colIndex"
                :label="''"
                >
                <template slot-scope="scope">
                  <el-tooltip
                          :content="getTooltipContent(scope.row.cells[colIndex])"
                          effect="light"
                          placement="top"
                          popper-class="cell-tooltip"
                          :disabled="!hoverCell">
                      <!-- 只修改柜格单元格内部结构 -->
                      <div class="grid-cell" :class="[getStatusClass(scope.row.cells[colIndex].status), {'status-overdue': isOverdue(scope.row.cells[colIndex])}]"
                           @mouseover="hoverCell = scope.row.cells[colIndex]"
                           @mouseleave="hoverCell = null"
                           @click="handleCellClick(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">

                        <div class="cell-content-container">
                          <!-- 位置ID -->
                          <div class="position-id">{{ scope.row.cells[colIndex].position }}</div>

                          <!-- 操作按钮区域（右上角） -->
                          <div class="cell-actions">
                            <!-- 取消预约按钮 -->
                            <div v-if="!isAdmin && scope.row.cells[colIndex].status === 2 && scope.row.cells[colIndex].user === currentUser.name"
                                 class="action-button cancel-reserve-btn"
                                 @click.stop="confirmCancelReserve(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">
                              ×
                            </div>

                            <!-- 取出按钮 -->
                            <div v-if="!isAdmin && scope.row.cells[colIndex].status === 1 && scope.row.cells[colIndex].user === currentUser.name"
                                 class="action-button take-out-btn"
                                 @click.stop="takeOutCell(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">
                              →
                            </div>

                            <!-- 归还按钮 -->
                            <div v-if="!isAdmin && scope.row.cells[colIndex].status === 1 && scope.row.cells[colIndex].user === currentUser.name"
                                 class="action-button return-btn"
                                 @click.stop="confirmReturnCell(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">
                              ↻
                            </div>

                            <!-- 取消保留按钮 -->
                            <div v-if="!isAdmin && scope.row.cells[colIndex].status === 3 && scope.row.cells[colIndex].user === currentUser.name"
                                 class="action-button cancel-taken-btn"
                                 @click.stop="cancelTakenReserve(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">
                              ×
                            </div>

                            <!-- 管理员确认借出按钮 -->
                            <div v-if="isAdmin && scope.row.cells[colIndex].status === 2"
                                 class="action-button confirm-borrow-btn"
                                 @click.stop="confirmBorrow(cabinet.id, scope.row.cells[colIndex], scope.$index, colIndex)">
                              ✓
                            </div>
                          </div>

                          <!-- 状态和用户信息 -->
                          <div class="status-user-row">
                            <div class="status-text" :class="{'overdue-date': isReserveOverdue(scope.row.cells[colIndex])}">
                              {{ scope.row.cells[colIndex].statusText }}
                            </div>
                            <div v-if="scope.row.cells[colIndex].user" class="user-info">
                              {{ scope.row.cells[colIndex].user }}
                            </div>
                          </div>

                          <!-- 日期信息 -->
                          <div class="date-row">
                            <div v-if="scope.row.cells[colIndex].Brow_at" class="date-info" :class="{'overdue-date': isOverdue(scope.row.cells[colIndex])}">
                              借: {{ formatCompactDate(scope.row.cells[colIndex].Brow_at) }}
                            </div>
                            <div v-if="scope.row.cells[colIndex].Back_at" class="date-info" :class="{'overdue-date': isReserveOverdue(scope.row.cells[colIndex])}">
                              保: {{ formatCompactDate(scope.row.cells[colIndex].Back_at) }}
                            </div>
                            <div v-if="scope.row.cells[colIndex].Take_at" class="date-info">
                              取: {{ formatCompactDate(scope.row.cells[colIndex].Take_at) }}
                            </div>
                          </div>
                        </div>
                      </div>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-empty v-else description="请添加柜体配置" :image-size="200"></el-empty>

          <div class="legend">
            <div class="legend-item">
              <div class="legend-color legend-free"></div>
              <span>空闲</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-in-use"></div>
              <span>使用中</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-reserved"></div>
              <span>预定中</span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-taken-reserved"></div>
              <span>取出保留</span>
            </div>
            <div class="legend-item">
              <div class="legend-color status-overdue"></div>
              <span>超期</span>
            </div>
          </div>
        </div>

        <div class="statistics">
          <div class="stat-card">
            <div class="stat-value">{{ getTotalCells(cabinet) }}</div>
            <div class="stat-label">总柜格数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ getFreeCells(cabinet) }}</div>
            <div class="stat-label">空闲柜格</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ getInUseCells(cabinet) }}</div>
            <div class="stat-label">使用中柜格</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ getReservedCells(cabinet) }}</div>
            <div class="stat-label">预定中柜格</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ getTakenCells(cabinet) }}</div>
            <div class="stat-label">取出保留</div>
          </div>
        </div>
      </div>

      <div class="cabinet-footer">
        <p>智能柜管理系统 © 2023 | 基于 Vue.js 和 Element UI 构建</p>
      </div>
    </div>

    <!-- 添加柜体配置对话框 -->
    <el-dialog title="添加新柜体" :visible.sync="dialogAddVisible" width="500px">
      <el-form :model="newCabinetForm" label-width="100px">
        <el-form-item label="柜体名称">
          <el-input v-model="newCabinetForm.name" placeholder="请输入柜体名称"></el-input>
        </el-form-item>
        <el-form-item label="柜体位置">
          <el-input v-model="newCabinetForm.location" placeholder="请输入柜体位置"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newCabinetForm.description" placeholder="请输入柜体描述"></el-input>
        </el-form-item>
        <el-form-item label="行数">
          <el-input-number v-model="newCabinetForm.rows" :min="1" :max="20"></el-input-number>
        </el-form-item>
        <el-form-item label="列数">
          <el-input-number v-model="newCabinetForm.cols" :min="1" :max="20"></el-input-number>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogAddVisible = false">取 消</el-button>
        <el-button type="primary" @click="addCabinet">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 单元格信息弹窗（管理员） -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogAdminVisible" width="500px">
      <div v-if="currentCell">
        <el-form :model="currentCell" label-width="100px" class="dialog-form">
          <el-form-item label="位置编号">
            <el-input v-model="currentCell.position"></el-input>
          </el-form-item>
          <el-form-item label="当前状态">
            <el-select v-model="currentCell.status">
              <el-option label="空闲" :value="0"></el-option>
              <el-option label="使用中" :value="1"></el-option>
              <el-option label="预定中" :value="2"></el-option>
              <el-option label="取出保留" :value="3"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="使用者">
            <el-input v-model="currentCell.user"></el-input>
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="currentCell.phone"></el-input>
          </el-form-item>
          <el-form-item label="Customer" prop="Customer" style="width: 100%;">
                <el-select v-model="currentCell.Customer" placeholder="请选择">
                      <el-option
                        v-for="item in CustomerOptions"
                        :key="item"
                        :label="item"
                        :value="item">
                      </el-option>
                </el-select>
              </el-form-item>
          <el-form-item label="ProCode">
            <el-input v-model="currentCell.ProCode"></el-input>
          </el-form-item>
          <el-form-item label="CampalCode">
            <el-input v-model="currentCell.CampalCode"></el-input>
          </el-form-item>
          <el-form-item label="留样日期(放回)">
            <el-date-picker
              v-model="currentCell.Brow_at"
              type="date"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
              placeholder="选择日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="留样原因">
            <el-input type="textarea" v-model="currentCell.BrowReson"></el-input>
          </el-form-item>
          <el-form-item label="取出日期">
            <el-date-picker
              v-model="currentCell.Take_at"
              type="date"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
              placeholder="选择日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="取出保留原因">
            <el-input type="textarea" v-model="currentCell.TakeReson"></el-input>
          </el-form-item>
          <el-form-item label="保留日期">
            <el-date-picker
              v-model="currentCell.Back_at"
              type="date"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
              placeholder="选择日期">
            </el-date-picker>
          </el-form-item>
          <el-form-item label="备注信息">
            <el-input type="textarea" v-model="currentCell.notes"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogAdminVisible = false">取 消</el-button>
        <el-button type="primary" @click="saveCellInfo">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 普通用户借用对话框 -->
    <el-dialog title="柜格借用" :visible.sync="dialogUserBorrowVisible" width="500px">
      <div v-if="currentCell">
        <el-form :model="borrowForm" label-width="100px">
          <el-form-item label="位置编号">
            <el-input v-model="currentCell.position" disabled></el-input>
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="borrowForm.phone"></el-input>
          </el-form-item>
          <el-form-item label="Customer" prop="Customer" style="width: 100%;">
                <el-select v-model="borrowForm.Customer" placeholder="请选择">
                      <el-option
                        v-for="item in CustomerOptions"
                        :key="item"
                        :label="item"
                        :value="item">
                      </el-option>
                </el-select>
              </el-form-item>
          <el-form-item label="ProCode">
            <el-input v-model="borrowForm.ProCode"></el-input>
          </el-form-item>
          <el-form-item label="CampalCode">
            <el-input v-model="borrowForm.CampalCode"></el-input>
          </el-form-item>
          <el-form-item label="留样原因">
            <el-input type="textarea" v-model="borrowForm.BrowReson"></el-input>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogUserBorrowVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleBorrow">借 用</el-button>
      </span>
    </el-dialog>

    <!-- 取出保留确认对话框 -->
    <el-dialog title="取出保留" :visible.sync="dialogTakeOutVisible" width="400px">
      <div v-if="currentCell">
        <p>确定要将柜格 <strong>{{ currentCell.position }}</strong> 设置为取出保留状态吗？</p>
        <el-form :model="takeoutForm" label-width="100px">
          <el-form-item label="取出保留原因">
            <el-input type="textarea" v-model="takeoutForm.TakeReson"></el-input>
          </el-form-item>
          <el-form-item label="保留日期（放回）">
            <el-date-picker
              v-model="takeoutForm.Back_at"
              type="date"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
              :picker-options="Back_atOptions"
              placeholder="选择日期">
            </el-date-picker>
          </el-form-item>
        </el-form>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogTakeOutVisible = false">取 消</el-button>
        <el-button type="primary" @click="confirmTakeOut">确 定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import * as cabinetApi from '@/api/cabinet'

export default {
  name: 'SmartCabinet',
  data() {
    return {
      currentCabinetId: null,
      isAdmin_origin: true,
      isAdmin: true,
      currentUser: {},
      CustomerOptions: [],
      tableloading: false,
      elbuttonloading: false,
      errMsg: '',

      // 对话框相关
      dialogAdminVisible: false,
      dialogUserBorrowVisible: false,
      dialogAddVisible: false,
      dialogTakeOutVisible: false,

      currentCell: null,
      currentCabinetIdInDialog: null,
      currentRowIndex: null,
      currentColIndex: null,
      originalCellStatus: null,

      // 借用表单
      borrowForm: {
        phone: '',
        Customer: '',
        ProCode: '',
        CampalCode: '',
        Brow_at: null,
        BrowReson: '',
      },

      // 取出保留表单
      takeoutForm: {
        TakeReson: '',
        Back_at: '',
      },

      // 添加柜体表单
      newCabinetForm: {
        name: '新柜体',
        location: '',
        description: '',
        rows: 5,
        cols: 6
      },

      hoverCell: null,
      tooltipVisible: false,
      statusMap: [
        { text: '空闲', class: 'status-free' },
        { text: '使用中', class: 'status-in-use' },
        { text: '预定中', class: 'status-reserved' },
        { text: '取出保留', class: 'status-taken-reserved' }
      ],
      nextCabinetId: 1,

      // 保留日期选择限制
      Back_atOptions: {
        disabledDate(time) {
          const maxDate = new Date();
          maxDate.setFullYear(maxDate.getFullYear() + 2);
          return time.getTime() > maxDate.getTime();
        }
      }
    }
  },
  computed: {
    ...mapState('cabinet', ['cabinets']),

    currentCabinet() {
      return this.cabinets.find(cab => cab.id === this.currentCabinetId) || {};
    },

    dialogTitle() {
      if (!this.currentCell) return '柜格信息';
      return `柜格信息 - ${this.currentCell.position}`;
    },
  },
  mounted() {
    this.getdata("first");
    this.borrowForm.user = this.currentUser.name;
    this.borrowForm.phone = this.currentUser.phone;
  },
  methods: {
    ...mapActions('cabinet', [
      'fetchCabinets',
      'addCabinetAction',
      'deleteCabinetAction',
      'updateGrid'
    ]),

    async getdata(e) {
      this.elbuttonloading = true;
      this.tableloading = true;

      try {
        const response = await cabinetApi.getCabinetData({ isGetData: e });

        this.$store.commit('cabinet/SET_CABINETS', response.data);
        this.isAdmin = response.data.isAdmin;
        this.isAdmin_origin = response.data.isAdmin;
        this.currentUser = response.data.currentUser;
        this.CustomerOptions = response.data.CustomerOptions;
        this.errMsg = response.data.errMsg;

        if (this.errMsg) {
          this.$alert(this.errMsg, '提示', { type: 'warning' });
        } else {
          this.$message({ message: '获取成功', type: 'success' });
        }
      } catch (error) {
        console.error('获取数据失败:', error);
        this.$message.error('获取数据失败');
      } finally {
        this.elbuttonloading = false;
        this.tableloading = false;
      }
    },

    openAddCabinetDialog() {
      if (!this.isAdmin) {
        this.$message.warning('只有管理员可以添加柜体');
        return;
      }

      this.dialogAddVisible = true;
      this.newCabinetForm = {
        name: `柜体${this.nextCabinetId}`,
        location: '',
        description: '',
        rows: 5,
        cols: 6
      };
    },

    async addCabinet() {
      const newCabinetId = this.nextCabinetId++;
      const newCabinet = {
        id: newCabinetId,
        name: this.newCabinetForm.name,
        location: this.newCabinetForm.location,
        description: this.newCabinetForm.description,
        rows: this.newCabinetForm.rows,
        cols: this.newCabinetForm.cols,
        gridData: []
      };

      this.generateGrid(newCabinet);

      try {
        const response = await cabinetApi.addCabinetAction(newCabinet);
        this.errMsg = response.data.errMsg;
        console.log('this.errMsg', this.errMsg, response.data.errMsg)

        if (this.errMsg) {
          //errMsg是对象{name: [...]}不是字符串
          const errorMsg = this.errMsg.name?.[0] || "柜体名称重复";

          // 修复2: 显示可读错误并中断流程
          this.$alert(errorMsg, '提示', { type: 'warning' });
          return; // 关键！中断后续操作
        } else {
          this.$message({ message: '获取成功', type: 'success' });
        }
        // +++ 新增关键代码 +++
        // 选项1：直接更新Vuex store（推荐）
        //this.$store.commit('cabinet/ADD_CABINET', newCabinet);
        //此时对应的// store/modules/cabinet.js，如下，没有与后端请求，否则就重复添加了
        //ADD_CABINET(state, newCabinet) {
          //state.cabinets.push(newCabinet);
        //}

        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
        this.currentCabinetId = newCabinetId;
        this.dialogAddVisible = false;
        this.$message.success(`柜体${newCabinetId}添加成功`);
      } catch (error) {
        console.error('添加柜体失败:', error);
        this.$alert(error, '提示', { type: 'warning' });
        this.$message.error('添加柜体失败');
      }
    },

    confirmRemoveCabinet(cabinetId, cabinetName) {
      if (!this.isAdmin) {
        this.$message.warning('只有管理员可以删除柜体');
        return;
      }

      this.$confirm(`确定要删除柜体 "${cabinetName}" 吗? 此操作不可恢复。`, '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.removeCabinet(cabinetId);
      }).catch(() => {});
    },

    async removeCabinet(cabinetId) {
      if (!this.isAdmin) {
        this.$message.warning('只有管理员可以删除柜体');
        return;
      }

      if (this.cabinets.length <= 1) {
        this.$message.error('不能删除最后一个柜体');
        return;
      }

      try {
        const response = await cabinetApi.deleteCabinetAction(cabinetId)
        // 选项2：重新获取所有数据（确保数据最新）
        this.errMsg = response.data.errMsg
        if(this.errMsg){
          this.$alert(this.errMsg, '提示', { type: 'warning' });
        }else{
          await this.getdata("update");
          this.$message.success('删除成功');
        }

      } catch (error) {
        console.error('删除柜体失败:', error);
        this.$message.error('删除柜体失败');
      }
    },

    confirmCancelReserve(cabinetId, cell, rowIndex, colIndex) {
      this.$confirm(`确定要取消柜格 ${cell.position} 的预约吗?`, '取消预约', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.cancelReserve(cabinetId, cell.id, rowIndex, colIndex);
      }).catch(() => {});
    },

    async cancelReserve(cabinetId, gridid, rowIndex, colIndex) {
      const cabinetIndex = this.cabinets.findIndex(cab => cab.id === cabinetId);
      if (cabinetIndex === -1) return;

      const cabinet = this.cabinets[cabinetIndex];
      const cell = cabinet.gridData[rowIndex][colIndex];

      if (cell.status === 2) {
        try {
          const response = await cabinetApi.cancelReservation(gridid,{
            cabinetId,
            rowIndex,
            colIndex,
            gridId: gridid,
            cellData: {
              ...cell,
              status: 0,
              user: '',
              phone: '',
              Customer: '',
              ProCode: '',
              CampalCode: '',
              notes: '',
              Brow_at: null,
              BrowReson: '',
              Back_at: null,
              Take_at: null,
              TakeReson: '',
            },
            action: "cancelReserve"
          });
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
          this.$message.success(`柜格 ${cell.position} 的预约已取消`);
        } catch (error) {
          console.error('取消预约失败:', error);
          this.$message.error('取消预约失败');
        }
      } else {
        this.$message.warning(`柜格 ${cell.position} 的预约状态已变更`);
      }
    },

    async cancelTakenReserve(cabinetId, cell, rowIndex, colIndex) {
      try {
        const response = await cabinetApi.updateGrid(cell.id, {
          cabinetId,
          rowIndex,
          colIndex,
          cellData: {
            ...cell,
            Back_at: null,
            Take_at: null,
            TakeReson: '',
            status: 1
          },
          action: "cancelTakenReserve"
        });
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
        this.$message.success(`柜格 ${cell.position} 的保留状态已取消`);
      } catch (error) {
        console.error('取消保留失败:', error);
        this.$message.error('取消保留失败');
      }
    },

    confirmReturnCell(cabinetId, cell, rowIndex, colIndex) {
      this.$confirm(`确定要归还柜格 ${cell.position} 吗?`, '归还确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.returnCell(cabinetId, cell, rowIndex, colIndex);
      }).catch(() => {});
    },

    async returnCell(cabinetId, cell, rowIndex, colIndex) {
      try {
        const response = await cabinetApi.updateGrid(cell.id, {
          cabinetId,
          rowIndex,
          colIndex,
          cellData: {
            ...cell,
            status: 0,
            user: '',
            phone: '',
            Customer: '',
            ProCode: '',
            CampalCode: '',
            notes: '',
            Brow_at: null,
            BrowReson: '',
            Back_at: null,
            Take_at: null,
            TakeReson: '',
          },
          action: "returnCell"
        });
        this.$message.success(`柜格 ${cell.position} 已成功归还`);
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
      } catch (error) {
        console.error('归还柜格失败:', error);
        this.$message.error('归还柜格失败');
      }
    },

    //取出保留，普通用户
    takeOutCell(cabinetId, cell, rowIndex, colIndex) {
      this.currentCabinetIdInDialog = cabinetId;
      this.currentCell = {...cell};
      this.currentRowIndex = rowIndex;
      this.currentColIndex = colIndex;
      this.dialogTakeOutVisible = true;
      this.takeoutForm.Back_at = '';
    },

    async confirmTakeOut() {
      if (!this.takeoutForm.Back_at) {
        this.$message.warning('请选择保留日期');
        return;
      }

      try {
        const response = await cabinetApi.updateGrid(this.currentCell.id, {
          cabinetId: this.currentCabinetIdInDialog,
          rowIndex: this.currentRowIndex,
          colIndex: this.currentColIndex,
          cellData: {
            ...this.currentCell,
            status: 3,
            Back_at: this.formatDateToISO(this.takeoutForm.Back_at),
            Take_at: this.formatDateToISO(new Date().toISOString().split('T')[0]),
            TakeReson: this.takeoutForm.TakeReson
          },
          action: 'confirmTakeOut'
        });

        this.dialogTakeOutVisible = false;
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
        this.$message.success(`柜格 ${this.currentCell.position} 已设为取出保留状态`);
      } catch (error) {
        console.error('取出保留操作失败:', error);
        this.$message.error('取出保留操作失败');
      }
    },

    setActiveCabinet(cabinetId) {
      this.currentCabinetId = cabinetId;
    },

    generateGrid(cabinet) {
      cabinet.gridData = [];
      for (let i = 0; i < cabinet.rows; i++) {
        const row = [];
        const rowChar = String.fromCharCode(65 + i);

        for (let j = 0; j < cabinet.cols; j++) {
          const status = 0;
          const statusObj = this.statusMap[status];
          const cell = {
            rowIndex: i,
            colIndex: j,
            position: `${rowChar}${j + 1}`,
            status: status,
            statusText: statusObj.text,
            statusClass: statusObj.class,
            user: '',
            Customer: '',
            ProCode: '',
            CampalCode: '',
            phone: '',
            notes: '',
            Brow_at: null,
            BrowReson: '',
            Back_at: null,
            Take_at: null,
            TakeReson: '',
          };
          row.push(cell);
        }
        cabinet.gridData.push(row);
      }
    },

    transformGridData(gridData) {
      const transformedData = gridData.map((row, rowIndex) => ({
                        id: `row-${rowIndex}`,
                        cells: [...row]
                    }));

                    // 在这里打印转换后的数据（开发调试用）
                    console.log('转换后的表格数据:', transformedData);

                    return transformedData;
    },

    handleCellClick(cabinetId, cell, rowIndex, colIndex) {
      this.currentCabinetIdInDialog = cabinetId;
      this.currentCell = {
        ...cell,
        rowIndex: rowIndex,
        colIndex: colIndex
      };
      this.currentRowIndex = rowIndex;
      this.currentColIndex = colIndex;
      this.originalCellStatus = cell.status;

      if (this.isAdmin) {
        this.dialogAdminVisible = true;
      } else {
        if (cell.status === 0) {
          this.borrowForm = {
            user: this.currentUser.name,
            phone: this.currentUser.phone
          };
          this.dialogUserBorrowVisible = true;
        } else if (cell.status === 2 && cell.user === this.currentUser.name) {
          // 取消预约按钮已显示，不需要额外处理
        } else if (cell.status === 1 && cell.user === this.currentUser.name) {
          // 取出保留按钮已显示，不需要额外处理
        } else {
          this.$message.info(`柜格 ${cell.position} 当前不可操作`);
        }
      }
    },

    //普通用户点击，借用
    async handleBorrow() {
      if (!this.dialogUserBorrowVisible || !this.currentCell) return;

      if (!this.borrowForm.phone.trim()) {
        this.$message.warning('请输入联系电话');
        return;
      }

      const cabinetId = this.currentCabinetIdInDialog;
      const rowIndex = this.currentRowIndex;
      const colIndex = this.currentColIndex;

      if (!cabinetId || rowIndex === null || colIndex === null) {
        this.$message.error('操作失败：无法确定柜格位置');
        return;
      }

      try {
        const response = await cabinetApi.reserveCell(this.currentCell.id,{
          cabinetId,
          rowIndex,
          colIndex,
          gridId: this.currentCell.id, // 使用柜格ID
          cellData: {
            ...this.currentCell,
            status: 2,
            phone: this.borrowForm.phone,
            Customer: this.borrowForm.Customer,
            ProCode: this.borrowForm.ProCode,
            CampalCode: this.borrowForm.CampalCode,
            BrowReson: this.borrowForm.BrowReson
          },
          action: "UserBorrow"
        });

        this.dialogUserBorrowVisible = false;
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
        this.$message.success(`柜格 ${this.currentCell.position} 已预约成功，等待管理员确认`);
      } catch (error) {
        console.error('借用操作失败:', error);
        this.$message.error('借用操作失败');
      }
    },

    async saveCellInfo() {
      if (!this.currentCabinetIdInDialog ||
          this.currentRowIndex === null ||
          this.currentColIndex === null ||
      !this.currentCell.id) {
        this.dialogAdminVisible = false;
        return;
      }

      // 如果状态从预定中(2)变为使用中(1)，设置借用日期
      if (this.originalCellStatus === 2 && this.currentCell.status === 1) {
        this.currentCell.Brow_at = new Date().toISOString().split('T')[0];
      }

      // 如果状态从使用中(1)变为空闲(0)，清除所有信息
      if (this.originalCellStatus === 1 && this.currentCell.status === 0) {
        this.currentCell.user = '';
        this.currentCell.phone = '';
        this.currentCell.Customer = '';
        this.currentCell.ProCode = '';
        this.currentCell.CampalCode = '';
        this.currentCell.notes = '';
        this.currentCell.Brow_at = null;
        this.currentCell.BrowReson = '';
        this.currentCell.Take_at = null;
        this.currentCell.TakeReson = '';
        this.currentCell.Back_at = null;
      }


      try {
        const response = await cabinetApi.updateGrid(this.currentCell.id, {cellData: {
            ...this.currentCell}});

        this.dialogAdminVisible = false;
        this.$message.success('柜格信息已更新');
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
      } catch (error) {
        console.error('保存柜格信息失败:', error);
        this.$message.error('保存柜格信息失败');
      }
    },

    async confirmBorrow(cabinetId, cell, rowIndex, colIndex) {
      this.$confirm(`确定要确认柜格 ${cell.position} 的借用吗?`, '确认借出', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await cabinetApi.confirmBorrow(cell.id,{
            cabinetId,
            rowIndex,
            colIndex,
            gridId: cell.id, // 使用柜格ID
            cellData: {
              ...cell,
              status: 1
            },
            action: "confirmBorrow"
          });
        // 选项2：重新获取所有数据（确保数据最新）
        await this.getdata("update");
          this.$message.success(`柜格 ${cell.position} 已确认借出`);
        } catch (error) {
          console.error('确认借出失败:', error);
          this.$message.error('确认借出失败');
        }
      }).catch(() => {});
    },

    formatCompactDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return `${date.getMonth()+1}/${date.getDate()}`; // 简化为 月/日 格式
    },

    formatDateToISO(dateString) {
      if (!dateString) return null;
      // 如果已经是ISO格式（包含T），则直接返回
      if (dateString.includes('T')) {
        return dateString;
      }
      // 否则，假设是YYYY-MM-DD格式，转换为ISO格式
      return dateString + 'T00:00:00';
    },

    isOverdue(cell) {
      if (!cell.Brow_at) return false;

      const Brow_at = new Date(cell.Brow_at);
      const now = new Date();
      const twoYearsAgo = new Date();
      twoYearsAgo.setFullYear(now.getFullYear() - 2);

      return Brow_at < twoYearsAgo;
    },

    isReserveOverdue(cell) {
      if (!cell.Back_at) return false;

      const Back_at = new Date(cell.Back_at);
      const now = new Date();
      return Back_at < now;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },

    getTooltipContent(cell) {
      let content = `柜格 ${cell.position} 信息\n`;
      content += `状态: ${cell.statusText}\n`;

      if (cell.user) content += `借用人: ${cell.user}\n`;
      if (cell.phone) content += `电话: ${cell.phone}\n`;

      if (cell.Brow_at) {
        const overdue = this.isOverdue(cell);
        content += `借用日期: ${this.formatDate(cell.Brow_at)}`;
        if (overdue) content += ` (超期)`;
        content += `\n`;
      }

      if (cell.Back_at) {
        const overdue = this.isReserveOverdue(cell);
        content += `保留日期: ${this.formatDate(cell.Back_at)}`;
        if (overdue) content += ` (超期)`;
        content += `\n`;
      }

      if (cell.Take_at) {
        content += `取出日期: ${this.formatDate(cell.Take_at)}\n`;
      }

      if (this.isOverdue(cell)) {
        content += `警告: 已超期超过2年!\n`;
      }

      return content;
    },

    getTotalCells(cabinet) {
      return cabinet.rows * cabinet.cols;
    },

    getFreeCells(cabinet) {
      return this.countCellsByStatus(cabinet, 0);
    },

    getInUseCells(cabinet) {
      return this.countCellsByStatus(cabinet, 1);
    },

    getReservedCells(cabinet) {
      return this.countCellsByStatus(cabinet, 2);
    },

    getTakenCells(cabinet) {
      return this.countCellsByStatus(cabinet, 3);
    },

    countCellsByStatus(cabinet, status) {
      if (!cabinet.gridData || !cabinet.gridData.length) return 0;

      let count = 0;
      cabinet.gridData.forEach(row => {
        row.forEach(cell => {
          if (cell.status === status) count++;
        });
      });
      return count;
    },

    getStatusClass(status) {
      switch (status) {
        case 0: return 'status-free';
        case 1: return 'status-in-use';
        case 2: return 'status-reserved';
        case 3: return 'status-taken-reserved';
        default: return 'status-free';
      }
    },
  }
}
</script>

<style scoped>
/* 全局重置 - 确保所有元素遵循相同盒模型 */
*,
*:before,
*:after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 系统主体布局 */
.cabinet-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
  background-color: #f5f7fa;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
}

.cabinet-main-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(66, 133, 244, 0.25);
  color: white;
}

.cabinet-main-header h1 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  letter-spacing: 1px;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.cabinet-main-header p {
  font-size: 1.1rem;
  opacity: 0.92;
}

/* 柜体管理导航 */
.cabinets-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  flex-wrap: wrap;
}

.cabinets-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.cabinet-tab {
  padding: 8px 20px;
  background: #ecf5ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #dcdfe6;
}

.cabinet-tab.active {
  background: #1a73e8;
  color: white;
  border-color: transparent;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
}

.delete-cabinet-btn {
  margin-left: 10px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #dcdfe6;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  transition: all 0.3s;
}

.cabinet-tab.active .delete-cabinet-btn {
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.delete-cabinet-btn:hover {
  background: #f56c6c;
  color: white;
  border-color: #f56c6c;
  transform: rotate(90deg);
}

/* 控制面板 */
.control-panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.control-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.role-btn {
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  border: 1px solid #dcdfe6;
  background: #f5f7fa;
}

.role-btn.active {
  background: #1a73e8;
  color: white;
  border-color: transparent;
}

/* 柜体主视图 - 核心样式 */
.cabinet-section {
  position: relative;
  margin-bottom: 35px;
  padding: 25px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cabinet-section:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.cabinet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eaeaea;
}

.cabinet-header h2 {
  font-size: 1.8rem;
  font-weight: 500;
  color: #1a73e8;
  letter-spacing: 0.5px;
}

.delete-btn {
  padding: 7px 15px;
  background: #fef0f0;
  color: #f56c6c;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.delete-btn:hover {
  background: #f56c6c;
  color: white;
}

/* 网格视图 - 关键样式 */
.grid-container {
  background: white;
  border-radius: 8px;
  margin-bottom: 30px;
  padding: 20px;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.03);
  background-color: #f9fafc;
}

.grid-table-container {
  width: 100%;
  overflow: auto;
  margin-bottom: 20px;
}

.grid-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.grid-table td {
  position: relative;
  height: 100px;
  text-align: center;
  vertical-align: middle;
  border: 1px solid transparent;
  padding: 0;
}

.grid-cell {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  transition: all 0.25s ease;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.grid-cell:hover {
  transform: scale(1.03);
  z-index: 10;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
}

/* 状态背景色 - 关键修复 */
.status-free {
  background-color: #f5f7fa;
  border: 1px solid #e0e6ed !important;
}

.status-in-use {
  background-color: #e1f3e1;
  background: linear-gradient(145deg, #d8f3d9, #e1f3e1);
  border: none !important;
}

/* 修改保留状态为黄色 */
.status-reserved {
  background-color: #fff8e1;
  background: linear-gradient(145deg, #ffecb3, #fff8e1);
  border: none !important;
}

/* 新增：取出保留状态 */
.status-taken-reserved {
  background-color: #ffecd5;
  background: linear-gradient(145deg, #ffe2c0, #ffecd5);
  border: none !important;
}

.position-id {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}

.status-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 超期日期样式 */
.overdue-date {
  color: #ff4d4f !important;
  font-weight: 600;
}

.user-info {
  font-size: 12px;
  color: #5a5e66;
  background: rgba(255, 255, 255, 0.4);
  padding: 2px 6px;
  border-radius: 3px;
  margin-top: 5px;
}

.cancel-reserve-btn {
  margin-top: 10px;
  padding: 5px 12px;
  font-size: 13px;
  border-radius: 4px;
  background: #f56c6c;
  color: white;
  cursor: pointer;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.cancel-reserve-btn:hover {
  background: #ff7875;
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 取出按钮样式 */
.take-out-btn {
  margin-top: 10px;
  padding: 5px 12px;
  font-size: 13px;
  border-radius: 4px;
  background: #ff9d00;
  color: white;
  cursor: pointer;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.take-out-btn:hover {
  background: #ffa940;
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 取消保留按钮样式 */
.cancel-taken-btn {
  margin-top: 10px;
  padding: 5px 12px;
  font-size: 13px;
  border-radius: 4px;
  background: #ff9d00;
  color: white;
  cursor: pointer;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.cancel-taken-btn:hover {
  background: #ffa940;
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 归还按钮样式 */
.return-btn {
  margin-top: 10px;
  padding: 5px 12px;
  font-size: 13px;
  border-radius: 4px;
  background: #1a73e8;
  color: white;
  cursor: pointer;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.return-btn:hover {
  background: #1669d6;
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 图例说明 */
.legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px dashed #eaeaea;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-free {
  background-color: #f5f7fa;
  border: 1px solid #e0e6ed;
}

.legend-in-use {
  background: linear-gradient(145deg, #d8f3d9, #e1f3e1);
}

.legend-reserved {
  background: linear-gradient(145deg, #ffecb3, #fff8e1);
}

/* 新增：取出保留状态图例 */
.legend-taken-reserved {
  background: linear-gradient(145deg, #ffe2c0, #ffecd5);
}

/* 统计区域 */
.statistics {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  background: linear-gradient(135deg, #f5f7fa 0%, #f9fafc 100%);
  border: 1px solid #e0e6ed;
}

.stat-card {
  text-align: center;
  padding: 15px 25px;
  min-width: 150px;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: bold;
  margin: 10px 0;
  color: #1a73e8;
  font-family: 'Arial', sans-serif;
}

.stat-label {
  font-size: 1rem;
  color: #5a5e66;
  font-weight: 500;
}

/* 超期状态背景 */
.status-overdue {
  background: linear-gradient(145deg, #ffd7d7, #ffbfbf) !important;
}

/* 页脚 */
.cabinet-footer {
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  color: #8c98ae;
  font-size: 0.9rem;
  border-top: 1px solid #eaeaea;
}

/* 添加确认借出按钮样式 */
.confirm-borrow-btn {
  margin-top: 10px;
  padding: 5px 12px;
  font-size: 13px;
  border-radius: 4px;
  background: #4caf50;
  color: white;
  cursor: pointer;
  display: inline-block;
  transition: all 0.3s;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  border: none;
}

.confirm-borrow-btn:hover {
  background: #66bb6a;
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 添加柜体按钮样式 */
.el-button--primary {
  background: #1a73e8;
  border-color: #1a73e8;
  transition: all 0.3s;
  font-weight: 500;
}

.el-button--primary:hover {
  background: #1669d6;
  border-color: #1669d6;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
}

.el-button--primary:active {
  transform: translateY(0);
  box-shadow: none;
}

/* 悬浮提示样式 */
.cell-tooltip {
  max-width: 300px;
  padding: 10px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  white-space: pre-line; /* 确保换行显示 */
}

.tooltip-overdue {
  color: #ff4d4f;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cabinet-section {
    padding: 15px;
  }

  .grid-table td {
    height: 85px;
  }

  .position-id {
    font-size: 16px;
  }

  .status-text {
    font-size: 12px;
  }

  .legend {
    gap: 15px;
  }

  .stat-card {
    padding: 10px;
    min-width: 130px;
  }

  .stat-value {
    font-size: 1.8rem;
  }
}

@media (max-width: 480px) {
  .position-id {
    font-size: 14px;
  }

  .cancel-reserve-btn {
    padding: 4px 8px;
    font-size: 12px;
  }

  .take-out-btn {
    padding: 4px 8px;
    font-size: 12px;
  }

  .return-btn {
    padding: 4px 8px;
    font-size: 12px;
  }

  .stat-card {
    padding: 8px;
    min-width: 100px;
  }

  .stat-value {
    font-size: 1.6rem;
  }
}

* {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
            color: #333;
            line-height: 1.35;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 20px;
            padding: 12px;
        }

        h1 {
            font-size: 1.7rem;
            margin-bottom: 6px;
            color: #2c3e50;
            font-weight: 600;
        }

        .subtitle {
            color: #5a6a7f;
            font-size: 0.9rem;
            max-width: 600px;
            margin: 0 auto;
        }

        .device-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            padding: 14px;
            margin-bottom: 16px;
            transition: transform 0.2s ease;
        }

        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #f0f0f0;
        }

        .device-name {
            font-size: 1.1rem;
            font-weight: 600;
            color: #3498db;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 70%;
        }

        .device-id {
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            color: #5a6a7f;
            white-space: nowrap;
        }

        .info-container {
            display: flex;
            flex-direction: column;
        }

        .status-row {
            display: flex;
            gap: 8px;
            margin-bottom: 7px;
            padding: 6px 0;
            flex-wrap: wrap;
        }

        .date-row {
            display: flex;
            gap: 10px;
            padding: 6px 0;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }

        .status-text {
            font-weight: 600;
            font-size: 0.82rem;
            padding: 3px 8px;
            border-radius: 3px;
            background: #eaf6ff;
            display: flex;
            align-items: center;
            white-space: nowrap;
        }

        .status-text i {
            margin-right: 4px;
            font-size: 0.75rem;
        }

        .overdue-date {
            color: #e74c3c !important;
            background: #fdeded !important;
        }

        .user-info {
            padding: 3px 8px;
            border-radius: 3px;
            background: #e8f4ea;
            color: #27ae60;
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            white-space: nowrap;
        }

        .user-info i {
            margin-right: 4px;
            font-size: 0.75rem;
        }

        .date-info {
            padding: 3px 8px;
            border-radius: 3px;
            background: rgba(52, 152, 219, 0.08);
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            min-width: 140px;
        }

        .date-info i {
            margin-right: 5px;
            font-size: 0.7rem;
            color: #5a6a7f;
        }

        .date-label {
            font-weight: 500;
            color: #5a6a7f;
            margin-right: 3px;
            font-size: 0.8rem;
        }

        .controls {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 25px 0;
        }

        .btn {
            padding: 7px 15px;
            border: none;
            border-radius: 5px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            background: #3498db;
            color: white;
            box-shadow: 0 2px 4px rgba(52, 152, 219, 0.2);
            display: flex;
            align-items: center;
            white-space: nowrap;
        }

        .btn i {
            margin-right: 5px;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(52, 152, 219, 0.25);
        }

        .btn-today {
            background: #2ecc71;
            box-shadow: 0 2px 4px rgba(46, 204, 113, 0.2);
        }

        .btn-full-width {
            width: 100%;
            justify-content: center;
            padding: 8px;
        }

        .explanation {
            background: white;
            padding: 16px;
            border-radius: 6px;
            margin-top: 25px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        }

        .explanation h2 {
            font-size: 1.2rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }

        .explanation h2 i {
            margin-right: 8px;
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 12px;
            border-radius: 5px;
            margin: 12px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.82rem;
            overflow-x: auto;
        }

        @media (max-width: 600px) {
            .date-info {
                min-width: calc(50% - 15px);
                font-size: 0.78rem;
            }

            .status-text, .user-info {
                font-size: 0.8rem;
            }
        }

        @media (max-width: 480px) {
            .date-info {
                min-width: 100%;
            }

            .status-row, .date-row {
                flex-direction: column;
                gap: 6px;
            }

            .device-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 6px;
            }

            .device-name, .device-id {
                max-width: 100%;
            }
        }

        .date-value {
            white-space: nowrap;
        }

        .action-button {
            margin-top: 5px;
            padding: 4px 8px;
            font-size: 0.75rem;
            background: #e67e22;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            display: flex;
            align-items: center;
        }

        .footer-note {
            text-align: center;
            font-size: 0.78rem;
            color: #7f8c8d;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }
    /* 保持原有样式不变 */
    .grid-cell {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      transition: all 0.25s ease;
      border-radius: 4px;
      cursor: pointer;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      padding: 8px;
      overflow: hidden;
    }

    /* 新增/修改的样式 */
    .cell-content-container {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      position: relative;
    }

    .position-id {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      text-align: center;
      margin-bottom: 6px;
    }

    .status-user-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: center;
      margin-bottom: 6px;
    }

    .status-text {
      font-size: 12px;
      padding: 2px 6px;
      border-radius: 3px;
      background: rgba(0, 0, 0, 0.05);
      white-space: nowrap;
    }

    .user-info {
      font-size: 11px;
      color: #5a5e66;
      background: rgba(255, 255, 255, 0.4);
      padding: 2px 6px;
      border-radius: 3px;
      white-space: nowrap;
    }

    .date-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      justify-content: center;
    }

    .date-info {
      font-size: 10px;
      padding: 2px 4px;
      border-radius: 2px;
      background: rgba(0, 0, 0, 0.05);
      white-space: nowrap;
    }

    .cell-actions {
      position: absolute;
      top: 4px;
      right: 4px;
      display: flex;
      gap: 4px;
      z-index: 10;
    }

    .action-button {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      font-size: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      border: none;
    }

    .cancel-reserve-btn {
      background: #f56c6c;
      color: white;
    }

    .take-out-btn {
      background: #ff9d00;
      color: white;
    }

    .return-btn {
      background: #1a73e8;
      color: white;
    }

    .cancel-taken-btn {
      background: #ff9d00;
      color: white;
    }

    .confirm-borrow-btn {
      background: #4caf50;
      color: white;
    }

    .overdue-date {
      color: #ff4d4f !important;
      font-weight: 600;
    }

    /* 原有样式保留 */
    .status-free {
      background-color: #f5f7fa;
      border: 1px solid #e0e6ed !important;
    }

    .status-in-use {
      background-color: #e1f3e1;
      background: linear-gradient(145deg, #d8f3d9, #e1f3e1);
      border: none !important;
    }

    .status-reserved {
      background-color: #fff8e1;
      background: linear-gradient(145deg, #ffecb3, #fff8e1);
      border: none !important;
    }

    .status-taken-reserved {
      background-color: #ffecd5;
      background: linear-gradient(145deg, #ffe2c0, #ffecd5);
      border: none !important;
    }
</style>
