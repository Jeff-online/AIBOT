<template>
  <div class="container">
    <Sidebar 
    @new-session="handleNewSession" 
    @load-chat="handleLoadChat" 
    @clear-current-session="handleClearSession"
    @show-user-management="showUserManagement = true" 
    @show-user-edit="showUserEdit = true"
    ref="sidebar"/>
    <ChatArea 
      v-if="currentSessionId" 
      :session-id="currentSessionId" 
      :key="currentSessionId"
      :is-new-session="isNewSession"
      @first-message-sent="handleFirstMessage"
    />
    <div v-else class="empty-prompt">
      <div class="prompt-container">
        <div class="prompt-icon">💬</div>
        <h3>新しい会話を始めましょう</h3>
        <p>左の「新規チャット」ボタンで会話を開始できます</p>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './Sidebar.vue';
import ChatArea from './ChatArea.vue';

export default {
  name: 'Home',
  components: {
    Sidebar,
    ChatArea,
  },
  data() {
    return {
      showUserManagement: false,
      showUserEdit: false,
      currentSessionId: "",
      hasHistorySessions: false,
      hasSessions: false,
      isNewSession: false
    };
  },
  mounted() {
    this.checkLoginStatus(); // mounted」でログイン状態を確認する
  },
  methods: {
    handleClearSession() {
      this.currentSessionId = "";
    },
    handleLoadChat(sessionId) {
      this.currentSessionId = sessionId;
      this.hasHistorySessions = true;
      this.hasSessions = true;
      this.isNewSession = false; 
    },
    handleNewSession(sessionId) {
      this.currentSessionId = sessionId;
      this.hasHistorySessions = true;
      this.hasSessions = true;
      this.isNewSession = true; 
    },
    handleFirstMessage() {
      if (this.isNewSession) {
        this.$refs.sidebar.fetchSessionData(); // サイドバー更新のトリガー
        this.isNewSession = false; // リセット状態
      }
    },
    checkLoginStatus() {
      const token = sessionStorage.getItem('token');
      if (!token) {
        this.$router.replace('/login'); // 🚀 ログインしていない場合はログインページへ
      }
    }
  }
};
</script>

<style scoped>
.empty-prompt {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  min-height: 60vh;
}

.prompt-container {
  text-align: center;
  max-width: 400px;
  padding: 20px;
}

.prompt-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

h3 {
  color: #2c3e50;
  margin-bottom: 12px;
}

p {
  color: #7f8c8d;
  line-height: 1.6;
}
</style>
