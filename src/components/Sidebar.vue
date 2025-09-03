<template>
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <div class="user-info">
        <img src="../assets/avatar.png" alt="アバター" id="userAvatar">
        <span id="userName">{{ userName }}</span>   <!-- ダイナミックユーザー名 -->
      </div>
      <button class="toggle-sidebar" id="toggleSidebar" @click="toggleSidebar">
        <img src="../assets/sidebar.png" alt="サイドバー切り替え" class="sidebar-icon">
      </button>
    </div>

    <!-- ロード・ステータスとエラー・アラート --> 
    <div v-if="loading" class="loading-text">データ読み込み中...</div>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="chat-history">
      <ul id="historyList">
        <li v-for="chat in chatHistory" :key="chat.session_id" @click="loadChat(chat.session_id)">
          <span>{{ chat.title }}</span>
          <button class="delete-btn" @click.stop="confirmDeleteChat(chat.session_id)">
            <img src="../assets/delete.png" alt="サイドバートグル" class="sidebar-icon">
          </button>
        </li>
      </ul>
    </div>
    <div class="sidebar-buttons">

      <div class="left-buttons">
          <button id="newChatBtn" class="icon-button" title="新規チャット" @click="createNewChat">
              <img src="../assets/new_chat.png" alt="新規チャット">
          </button>
      </div>
      <div class="right-buttons">
          <button id="settingBtn" class="icon-button" title="設定" @click="showSettingMenu">
              <img src="../assets/setting.png" alt="設定">
          </button>
          <button id="logoutBtn" class="icon-button" title="ログアウト" @click="logout">
              <img src="../assets/logout.png" alt="ログアウト">
          </button>
      </div>

      <!-- ドロップダウンメニューの設定 -->
      <div id="settingMenu" class="setting-menu" v-if="settingMenu">
        <div 
          v-if="permission"
          class="menu-item"
          id="userManageBtn"
          @click="handleUserManagementClick"
        >
          ユーザー管理
        </div>
        <div class="menu-item" id="changePasswordBtn" @click="handlePasswordChangeClick">パスワード変更</div>
      </div>

      <UserManagement v-if="showUserManagement" @close="showUserManagement = false" @username-updated="updateUsername" />
      <PassWord v-if="showUserPassWord" @close="showUserPassWord = false" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import PassWord from './passWord.vue';
import UserManagement from './UserManagement.vue';
import { MessageBox, Notification } from 'element-ui'; 

export default {
  components: {
    UserManagement,
    PassWord,
},
  data()  {
    return {
      showUserManagement: false,
      showUserPassWord: false,
      settingMenu: false,
      loading: false,
      errorMessage: '',
      userName: '',
      permission: false,
      chatHistory: [],
    };
  },
  mounted() {
    this.userName = sessionStorage.getItem('username') || 'ゲストユーザー';
    this.fetchSessionData();
  },
  methods: {
    async fetchSessionData() {
      const token = sessionStorage.getItem('token');
      const username = sessionStorage.getItem('username');

      if (!token) return;
      
      this.loading = true;
      this.errorMessage = '';
      
      try {
        const response = await axios.get(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/session_management',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            params: {
              username: username
            }
          }
        );

        if (response.data.code === 200) {
          // インターフェース・データの解析
          const data = response.data;
          this.chatHistory = data.session_data || [];
          this.chatHistory.reverse();
          // this.userName = username || 'ゲストユーザー';
          this.permission = sessionStorage?.getItem('permission') === 'admin';
        } else {
          this.errorMessage = 'データの取得に失敗しました';
        }
      } catch (error) {
        this.errorMessage = 'データ取得に失敗しました';
      } finally {
        this.loading = false;
      }
    },
    async confirmDeleteChat(chatId) {
      try {
        await MessageBox.confirm(
          'このチャット履歴を削除してもよろしいですか？',
          '確認',
          {
            confirmButtonText: '確認',
            cancelButtonText: 'キャンセル',
            type: 'warning',
            customClass: 'custom-confirm-box',
            showClose: false
          }
        )

        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        await axios.delete(
          `https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/session_management`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: {
              session_id: chatId,
              username: username
            }
          }
        );
        Notification.success({
          title: 'セッションの削除',
          message: 'セッションが正常に削除されました',
          duration: 3000,
          offset: 60
        })
        if (this.$parent.currentSessionId === chatId) {
          this.$emit('clear-current-session');
        }
        await this.fetchSessionData();
        if (this.chatHistory.length === 0) {
          this.$emit('no-sessions');
        }
      } catch (error) {
        if (error !== 'cancel') {
          Notification.error({
            title: 'セッションの削除',
            message: error.response?.data?.message || '削除に失敗しました',
            duration: 3000,
            offset: 60
          })
        }
      }
    },
    async createNewChat() {
      try {
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        const response = await axios.post(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/session_management',
          {username: username},
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
        this.$emit('new-session', response.data.session_info.session_id);
        await this.fetchSessionData();
      } catch (error) {
        Notification.error({
          title: '新しい会話を作成',
          message: error.response?.data?.message || '新規チャットの作成に失敗しました',
          duration: 3000,
          offset: 60
        })
      }
    },
    toggleSidebar() {
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.toggle('collapsed');
    },
    loadChat(chatId) {
      this.$emit('load-chat', chatId);
    },
    showSettingMenu() {
      this.settingMenu = !this.settingMenu;
    },
    handleUserManagementClick() {
      this.showUserManagement = true;
      this.settingMenu = false;
    },
    handlePasswordChangeClick() {
      this.showUserPassWord = true;
      this.settingMenu = false;
    },
    updateUsername(newName) {
      this.userName = newName || 'ゲストユーザー';
      sessionStorage.setItem('username', this.userName);
    },
    async logout() {
      const token = sessionStorage.getItem('token');
      const username = sessionStorage.getItem('username');
      try {
        await axios.delete(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/upload_file',
          {
              headers: {
                Authorization: `Bearer ${token}`
              },
              params: {
                username: username
              }
            }
        );
      } catch(error) {
        // console.error(error.response?.data?.message)
      }finally {
        sessionStorage.clear();
        this.$router.replace('/login');
      }
    }
  }
};
</script>

<style scoped>
.loading-text {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error-message {
  color: #ff4444;
  padding: 10px;
  margin: 10px;
  border: 1px solid #ff4444;
  border-radius: 4px;
  text-align: center;
}

.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  position: relative;
}
.sidebar.collapsed {
  width: 50px;
}
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background-color: #666;
}
</style>