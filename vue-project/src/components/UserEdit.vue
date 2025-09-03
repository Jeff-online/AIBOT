<template>
  <div class="modal">
    <div class="modal-content user-edit-container">
      <div class="header">
        <h2>{{ isEditing ? 'ユーザー編集' : '新規ユーザー作成' }}</h2>
        <button class="close-modal" @click="hideUserEdit">&times;</button>
      </div>
      <div class="form-content">
        <div class="form-item">
          <label for="editNickId">ユーザーID</label>
          <input 
            type="text" 
            ref="editNickId" 
            v-model="formData.nick_id"
            :readonly="isEditing"
            required
          >
        </div>
        <div class="form-item">
          <label for="editUserName">ユーザー名</label>
          <input 
            type="text" 
            ref="editUserName" 
            v-model="formData.username"
            required
          >
        </div>
        <div class="form-item">
          <label for="editRole">権限</label>
          <select id="editRole" v-model="formData.permission">
            <option value="admin">管理者</option>
            <option value="user">一般ユーザー</option>
          </select>
        </div>
        <div class="form-item">
          <label for="editStatus">状態</label>
          <select id="editStatus" v-model="formData.user_status">
            <option :value="true">有効</option>
            <option :value="false">無効</option>
          </select>
        </div>
        <div class="button-group">
          <button class="cancel-btn"   @click="hideUserEdit">キャンセル</button>
          <button class="confirm-btn"  @click="handleSubmit">確認</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Notification } from 'element-ui'
export default {
  props: {
    currentUser: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      isEditing: false,
      formData: {
        nick_id: '',
        username: '',
        permission: 'user',
        user_status: 'true'
      },
    };
  },
  watch: {
    currentUser: {
      immediate: true,
      handler(val) {
        if (val) {
          this.isEditing = true
          this.formData = {
            nick_id: val.nick_id,
            username: val.username,
            permission: val.permission,
            user_status: val.user_status
          }
        } else {
          this.isEditing = false
          this.resetForm()
        }
      }
    }
  },
  methods: {
    hideUserEdit() {
      this.$emit('close', false);
    },
    resetForm() {
      this.formData = {
        nick_id: '',
        username: '',
        permission: 'user',
        user_status: true
      }
    },
    validateForm() {
      if (!this.formData.nick_id) {
        Notification.error({
          title: '入力エラー',
          message: 'ユーザーIDを入力してください',
          duration: 3000,
          offset: 60
        })
        return false
      }
      if (!this.formData.username) {
        Notification.error({
          title: '入力エラー',
          message: 'ユーザー名を入力してください',
          duration: 3000,
          offset: 60
        })
        return false
      }
      return true
    },
    handleSubmit() {
      if (!this.validateForm()) return
      
      const payload = { ...this.formData }
      if (this.isEditing) {
        // 編集時はIDを追加
        payload.id = this.currentUser.id
        // パスワード未入力時は削除
      }
      
      this.$emit('submit', payload)
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
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.form-item {
  margin-bottom: 15px;
}

.form-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

button {
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.confirm-btn {
  background-color: #5bc0de;
  color: white;
  border: none;
}

.confirm-btn:hover {
  background-color: #339abf;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #555;
  border: 1px solid #e0e0e0;
}

.cancel-btn:hover {
  background-color: #e5e5e5;
}

.close-modal {
  font-size: 24px;
  background: none;
  border: none;
  padding: 0;
  line-height: 1;
  color: #666;
}

.close-modal:hover {
  color: #333;
}

.user-edit-container h2 {
  font-size: 18px;
  margin: 0 0 20px 0;
  color: #555;
}
</style>