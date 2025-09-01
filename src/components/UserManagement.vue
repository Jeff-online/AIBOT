<template>
  <div class="modal">
    <div class="modal-content user-management-container">
      <div class="header">
        <h1>ユーザー管理</h1>
        <button class="close-modal" @click="hideUserManagement">&times;</button>
      </div>
      <div class="search-area">
        <div class="search-row">
          <div class="search-item">
            <label>ユーザーID</label>
            <input type="text" v-model="searchParams.id" placeholder="ユーザーIDを入力">
          </div>
          <div class="search-item">
            <label>ユーザー名</label>
            <input type="text" v-model="searchParams.name" placeholder="ユーザー名を入力">
          </div>
          <div class="search-item">
            <label>権限</label>
            <select v-model="searchParams.role">
              <option value="">すべて</option>
              <option value="admin">管理者</option>
              <option value="user">一般ユーザー</option>
            </select>
          </div>
          <div class="search-item">
            <label>状態</label>
            <select v-model="searchParams.status">
              <option value="">すべて</option>
              <option :value="true">有効</option>
              <option :value="false">無効</option>
            </select>
          </div>
          <div class="search-item">
            <button @click="searchUsers" style="width: 25%;margin-bottom: 0%;font-size: 13px;">検索</button>
          </div>
        </div>
      </div>
      <div class="add-user-container">
        <button @click="showUserEdit = true" style="width: 8%;">
          <span style="font-size: 13px;"><i class="el-icon-plus"></i>新規ユーザー</span>
        </button>
        <!-- <UserEdit v-if="showUserEdit" @close="showUserEdit = false" /> -->
      </div>
      <div class="users-table-container">
        <div class="table-header">
          <table>
            <thead>
              <tr>
                <th>ユーザーID</th>
                <th>ユーザー名</th>
                <th>権限</th>
                <th>状態</th>
                <th>操作</th>
              </tr>
            </thead>
          </table>
        </div>
        <div class="table-content">
          <table>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.nick_id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ formatPermission(user.permission) }}</td>
                <td>
                  <i v-if="user.user_status" class="status-active">有効</i>
                  <i v-else class="status-inactive">無効</i>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="unified-btn" @click="editUser(user)">編集</button>
                    <button class="unified-btn" @click="confirmDelete(user)">削除</button>
                    <button class="unified-btn" @click="handleResetPassword(user)">パスワードリセット</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <UserEdit 
        v-if="showUserEdit"
        :current-user="selectedUser"
        @submit="handleSaveUser"
        @close="closeEditor"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import UserEdit from './UserEdit.vue';
import { Notification, MessageBox } from 'element-ui';

const API_BASE = 'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api';
const USER_ENDPOINT = `${API_BASE}/user`;

export default {
  components: {
    UserEdit
  },
  data() {
    return {
      selectedUser: null,
      showUserEdit: false,
      isEditing: false,
      searchParams: {
        id: '',
        name: '',
        role: '',
        status: ''
      },
      users: []
    };
  },
  mounted() {
    this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      try {
        const token = sessionStorage.getItem('token');
        const params = {
          nick_id: this.searchParams.id,
          username: this.searchParams.name,
          permission: this.searchParams.role,
          user_status: this.searchParams.status
        };
        
        const response = await axios.get(USER_ENDPOINT,
          {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: params
          }
        );
        this.users = response.data.user_info;
      } catch (error) {
        Notification.error({
          title: 'ユーザー情報の取得に失敗しました',
          duration: 3000,
          offset: 60
        });
      }
    },
    hideUserManagement() {
      this.$emit('close', false);
    },
    searchUsers() {
      this.fetchUsers();
    },
    editUser(user) {
      this.selectedUser = { ...user };
      this.isEditing = true;
      this.showUserEdit = true;
    },
    async confirmDelete(user) {
      try {
        await MessageBox.confirm(
          `${user.username}を削除してもよろしいですか？`,
          'ユーザー削除確認',
          {
            confirmButtonText: '削除',
            cancelButtonText: 'キャンセル',
            type: 'warning',
            customClass: 'custom-confirm-box',
            showClose: false
          }
        )

        const token = sessionStorage.getItem('token')
        await axios.delete(USER_ENDPOINT, {
          headers: {
            Authorization: `Bearer ${token}`
          },
          params: { id: user.id }
        })

        this.fetchUsers()
        Notification.success({
          title: 'ユーザー削除',
          message: `${user.username}を削除しました`,
          duration: 3000,
          offset: 60
        })
      } catch (error) {
        if (error === 'cancel') {
          Notification.info({
            title: '操作キャンセル',
            message: '削除操作をキャンセルしました',
            duration: 2000,
            offset: 60
          })
        } else {
          Notification.error({
            title: 'ユーザー削除',
            message: error.response?.data?.message || '削除処理に失敗しました',
            duration: 3000,
            offset: 60
          })
        }
      }
    },
    async handleSaveUser(userData) {
      try {
        let titled, msg;
        const token = sessionStorage.getItem('token');
        const currentUserId = sessionStorage.getItem('userid');
        if (this.isEditing) {
          msg = "変更が成功しました"
          titled = "ユーザー変更。"
          await axios.put(USER_ENDPOINT, 
            userData,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          )
          if (userData.id === currentUserId) {
            this.$emit('username-updated', userData.username)
          }
        } else {
          msg = "正常に追加されました"
          titled = "ユーザーの新規追加。"
          await axios.post(USER_ENDPOINT, 
            userData,
            {
              headers: {
                Authorization: `Bearer ${token}`
              }
            }
          );
        }
        Notification.success({
          title: titled,
          message: `${userData.username} ${msg}。`,
          duration: 3000,
          offset: 60
        });
        this.fetchUsers();
        this.closeEditor();
      } catch (error) {
        if (error === 'cancel') {
          Notification.info({
            title: 'ユーザーエディタ',
            message: '編集がキャンセルされました',
            duration: 2000,
            offset: 60
          })
        } else {
          Notification.error({
            title: '保存エラー',
            message: error.response?.data?.message || '操作に失敗しました',
            duration: 3000,
            offset: 60
          });
        }
      }
    },
    closeEditor() {
      this.showUserEdit = false;
      this.selectedUser = null;
      this.isEditing = false;
    },
    async handleResetPassword(user) {
      try {
        await MessageBox.confirm(
          `${user.username}のパスワードを初期化しますか？`,
          'パスワードリセット確認',
          {
            confirmButtonText: '確認',
            cancelButtonText: 'キャンセル',
            type: 'warning',
            customClass: 'custom-confirm-box',
            showClose: false
          }
        )
        const token = sessionStorage.getItem('token')
        const response = await axios.get(
          `${API_BASE}/initialization`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: {
              id: user.id
            }
          }
        )

        if (response.data.code === 200) {
          Notification.success({
            title: 'パスワードのリセット',
            message: `${user.username}パスワードが初期化されました`,
            duration: 3000,
            offset: 60
          })
        } else {
          throw new Error(response.data.message)
        }
      } catch (error) {
        if (error === 'cancel') {
          Notification.info({
            title: '操作キャンセル',
            message: 'リセット操作をキャンセルしました',
            duration: 2000,
            offset: 60
          })
        } else {
          Notification.error({
            title: 'パスワードのリセット',
            message: error.response?.data?.message || 'パスワードリセットに失敗しました',
            duration: 3000,
            offset: 60
          })
        }
      }
    },
    formatPermission(permission) {
      const permissionMap = {
        admin: '管理者',
        user: '一般ユーザー'
      }
      return permissionMap[permission] || permission
    }
  }
};
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.unified-btn {
  background-color: #5bc0de;
  color: white;
  border: none;
  margin-bottom: 0px;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 13px;
  /* display: inline-flex; */
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.unified-btn:hover {
  background-color: #339abf;
}

.search-item .unified-btn {
  width: 100%;
}

.add-user-container .unified-btn {
  width: 25%;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
  margin: 0 -4px;
}

.action-buttons .unified-btn {
  flex: 1;
  /* padding: 8px 12px; */
}

.user-management-container {
  background: white;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 90%;
  max-width: 1400px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h1 {
  color: #555;
  margin: 0;
}

.close-modal {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  padding: 0 8px;
}

.close-modal:hover {
  color: #333;
}

.search-area {
  margin-bottom: 15px;
}

.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  background-color: #f9f9f9;
}

.search-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 150px;
  max-width: 300px;
  flex: 1;
}

.search-item:nth-child(3),
.search-item:nth-child(4) {
  width: 150px;
  flex: 0 0 auto;
}

.search-item label {
  font-weight: 500;
  color: #000;
  font-weight: 600;
}

.search-item input,
.search-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.add-user-container {
  margin-bottom: 15px;
}

.users-table-container {
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  overflow: auto;
  max-height: 60vh;
}

.table-header {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f4f4f4;
  padding: 12px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  box-sizing: border-box;
}

th:nth-child(1), td:nth-child(1) { width: 20%; }
th:nth-child(2), td:nth-child(2) { width: 25%; }
th:nth-child(3), td:nth-child(3) { width: 15%; }
th:nth-child(4), td:nth-child(4) { width: 15%; }
th:nth-child(5), td:nth-child(5) { width: 25%; }

.table-content tr {
  border-bottom: 1px solid #e0e0e0;
}

.table-content tr:hover {
  background-color: #f5f5f5;
}

/* スクロールバーのスタイル */
.users-table-container::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.users-table-container::-webkit-scrollbar-track {
  background: #e0e0e0;
  border-radius: 4px;
}

.users-table-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
  border: 2px solid #e0e0e0;
}

.users-table-container::-webkit-scrollbar-thumb:hover {
  background: #666;
}

.status-active,
.status-inactive {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.status-active {
  background-color: #e8f5e8;
  color: #2d662d;
}

.status-inactive {
  background-color: #f5e8e8;
  color: #662d2d;
}

@media (max-width: 768px) {
  .user-management-container {
    width: 95%;
    padding: 15px;
  }
  
  .search-item {
    min-width: 100%;
  }
  
  th, td {
    padding: 12px 8px;
  }
}
</style>