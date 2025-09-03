<template>
  <div class="modal">
    <div class="modal-content user-edit-container">
      <h2>パスワード変更</h2>
      <!-- <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div> -->
      <div class="form-content">
        <div class="form-item">
          <label for="editId">新しいパスワード</label>
          <input type="password" id="editId" v-model="user.newPassWord" >
        </div>
        <div class="form-item">
          <label for="editUserName">新しいパスワード（確認）</label>
          <input type="password" id="editUserName" v-model="user.PassWordConfirm">
        </div>
        <div class="button-group">
          <button class="cancel-btn"   @click="hideUserEdit">キャンセル</button>
          <button class="confirm-btn"  @click="saveUser">確認</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Notification, MessageBox } from 'element-ui'

export default {
  data() {
    return {
      user: {
        newPassWord: '',
        PassWordConfirm: '',
      },
    };
  },
  methods: {
    hideUserEdit() {
      Notification.closeAll();
      this.$emit('close');
    },
    async saveUser() {
      // 入力検証
      if (!this.user.newPassWord || !this.user.PassWordConfirm) {
        Notification.error({
          title: 'エラー',
          message: 'パスワードを入力してください。',
          duration: 3000
        });
        return;
      }
      if (this.user.newPassWord !== this.user.PassWordConfirm) {
        Notification.error({
          title: 'エラー',
          message: 'パスワードが一致しません。',
          duration: 3000
        });
        return;
      }

      try {
        await MessageBox.confirm('パスワードを変更しますか？', '確認', {
          confirmButtonText: '確認',
          cancelButtonText: 'キャンセル',
          type: 'warning',
          customClass: 'custom-confirm-box',
          showClose: false
        });

        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        
        const response = await axios.post(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/user_update',
          {
            username: username,
            new_password: this.user.newPassWord
          },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        if (response.data.code === 200) {
          this.hideUserEdit();
          Notification.success({
            title: 'パスワードの更新',
            message: 'パスワードが正常に変更されました！',
            duration: 3000,
            offset: 60
          });
        }
      } catch (error) {
        if (error === 'cancel') {
          Notification.info({
            title: '操作キャンセル',
            message: 'パスワード変更キャンセル',
            duration: 2000,
            offset: 60
          })
        } else {
          Notification.error({
            title: 'パスワードの更新',
            message: error.response?.data?.message || 'パスワードの変更に失敗しました',
            duration: 3000,
            offset: 60
          });
        }
      }
    },
    loadUser() {
      if (this.userId) {
        const user = this.$parent.users.find(u => u.id === this.userId);
        if (user) {
          this.user = { ...user };
        }
      }
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
.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
  max-width: 90%;
  height: 33%;
}
.close-modal {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}
.form-item {
  margin-bottom: 15px;
}
.form-item label {
  display: block;
  margin-bottom: 5px;
}
.form-item input, .form-item select {
  width: 100%;
  padding: 8px;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
}
.button-group {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}
.button-group button {
  margin-left: 10px;
  padding: 8px 70px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.button-group .cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid var(--border-color);
  height: 35px;
}
.button-group .confirm-btn {
  background-color: var(--primary-color);
  color: white;
  height: 35px;
}
.error-message {
  color: #ff4444;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ff4444;
  border-radius: 4px;
  text-align: center;
}
</style>