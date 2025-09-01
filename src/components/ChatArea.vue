<template>
  <div class="chat-area">
    <div class="messages" id="messageContainer">
      <div v-if="showInitialPrompt" class="initial-prompt">
        何かご用ですか？
      </div>
      <div v-for="message in messages" :key="message.id">
        <!-- プッシュボタン・フロント -->
        <div v-if="message.type == 'user'" style="display: flex;">
          <div :class="`message ${message.type}`">{{ message.text }}</div>
        </div>
        <!-- プッシュボタン・バック -->
        <div v-if="message.type == 'ai'" style="display: flex;">
          <div class="airesp markdown-content" v-html="renderMarkdown(message.text)"></div>
          <div style="margin-top: 1.5%;display: flex;">
            <button class="message-action-btn" title="コピー" @click="copy">
              <img src="../assets/copy.png" alt="Copy">
            </button>&nbsp;&nbsp;
            <button class="message-action-btn" title="テキストファイルに保存" @click="save">
              <img src="../assets/save.png" alt="Save">
            </button>
          </div>
        </div>
      </div>
      <div v-if="isLoading" class="loading-text">応答待ち...</div>
      <div v-if="isUploading" class="uploading-message">
        <span class="loading-spinner"></span> アップロード中...
      </div>
    </div>
    <div class="resizer" id="dragHandle"></div>
    <div class="chat-input-container">
      <div class="file-display-area">
        <div v-if="promptName" class="file-item">
          <span class="file-name">{{ promptName }}</span>
          <button class="delete-btn" @click="deleteFile(promptName)">&times;</button>
        </div>
        <div v-if="attachmentName" class="file-item">
          <span class="file-name">{{ attachmentName }}</span>
          <button class="delete-btn" @click="deleteFile(attachmentName)">&times;</button>
        </div>
      </div>
      <textarea id="messageInput" placeholder="メッセージを入力..." v-model="message" @keydown.enter="handleEnter"></textarea>
      <div class="button-group">
        <button class="history-btn" title="会話履歴をダウンロード" @click="downloadHistory">
          <img src="../assets/download.png" alt="Download" width="20px" height="20px">
        </button>
        <label class="save-btn" title="プロンプト">
          <img src="../assets/tip.png" alt="Save" class="tip-icon">
          <input type="file" id="tipInput" @change="saveMessage" style="display: none;">
        </label>
        <label class="file-label" title="添付ファイル">
          <img src="../assets/fileicon.png" alt="Attachment" class="file-icon">
          <input type="file" id="fileInput" @change="uploadFile" style="display: none;">
        </label>
        <button id="sendBtn" @click="sendMessage">送信</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import katex from 'katex';
import { marked } from 'marked';
import hljs from 'highlight.js';
import DOMPurify from 'dompurify';
import { Notification } from 'element-ui';

export default {
  props: {
    sessionId: {
      type: String,
      required: true
    },
    isNewSession: Boolean
  },
  data() {
    return {
      message: '',
      messages: [],
      promptName: '',
      attachmentName: '',
      session_id: null,
      isUploading: false,
      uploadedFiles: [],
      isLoading: false,
      hasSentMessage: false,
      showInitialPrompt: false
    };
  },
  watch: {
    sessionId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchChatHistory(newVal);
          this.promptName = '';
          this.attachmentName = '';
        } else {
          this.messages = [];
          this.promptName = '';
          this.attachmentName = '';
        }
      },

    },
    messages() {
      this.$nextTick(this.scrollToBottom);
    },
    isLoading(newVal) {
      if (newVal) this.$nextTick(this.scrollToBottom);
    },
    isNewSession(newVal) {
      if (newVal) {
        this.showInitialPrompt = true;
      }
    }
  },
  mounted(){
    this.initResizer();
  },
  created() {
    this.initMarkdownRenderer();
  },
  methods: {
    async save(event){
        try {
          const messageInput =  event.target.closest('.message-action-btn').parentElement.previousElementSibling;

          // 設定ファイル保存オプション
          const options = {
              suggestedName: 'chat.txt',
              types: [{
                  description: 'Text file',
                  accept: { 'text/plain': ['.txt'] }
              }]
            };

            // システムのファイル保存ダイアログボックスを開く
            const handle =  await window.showSaveFilePicker(options);
            
            // 書き込みストリームの作成
            const writable =  await handle.createWritable();
            
            // コンテンツを書く
            await writable.write(messageInput.innerText);
            
            // 書き込みストリームをオフにする
            await writable.close();
        } catch (err) {
            if (err.name !== 'AbortError') {
                // console.error('ファイル保存時のエラー:', err);
            }
        }
    },
    copy(event){
      const messageInput = event.target.closest('.message-action-btn').parentElement.previousElementSibling;
      navigator.clipboard.writeText(messageInput.innerText);
    },
    initResizer() {
    const resizer = document.getElementById('dragHandle');
    const chatInputContainer = document.querySelector('.chat-input-container');
    let startY;
    let startHeight;

      function startDragging(e) {
          startY = e.clientY;
          startHeight = parseInt(getComputedStyle(chatInputContainer).height, 10);
          document.documentElement.classList.add('dragging');
          resizer.classList.add('dragging');
          
          document.addEventListener('mousemove', onDragging);
          document.addEventListener('mouseup', stopDragging);
      }
      function onDragging(e) {
          const deltaY = startY - e.clientY;
          const newHeight = Math.max(160, Math.min(400, startHeight + deltaY));
          chatInputContainer.style.height = `${newHeight}px`;
      }
      function stopDragging() {
          document.documentElement.classList.remove('dragging');
          resizer.classList.remove('dragging');
          document.removeEventListener('mousemove', onDragging);
          document.removeEventListener('mouseup', stopDragging);
      }

      resizer.addEventListener('mousedown', startDragging);
    },
    scrollToBottom() {
      const container = document.getElementById('messageContainer');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    handleEnter(event) {
      if (!event.shiftKey) {
        event.preventDefault();
        this.sendMessage();
      }
    },
    async sendMessage() {
      this.showInitialPrompt = false;
      const message = this.message.trim();
      if (!message) return;
      try {
        this.isLoading = true;
        this.error = null;
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');

        this.messages.push({ id: Date.now(), text: message, type: 'user' });
        this.message = '';

        const requestBody = {
          session_id: this.sessionId,
          username: username,
          content: message,
        };

        if (this.promptName) requestBody.prompt_name = this.promptName;
        if (this.attachmentName) requestBody.attachment_name  = this.attachmentName;

        const response = await axios.put(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/session_management',
          requestBody,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        if (response.data.code === 200) {
          this.attachmentName = '';
          this.messages.push({
            id: Date.now(),
            text: response.data.session_info.response_ai,
            type: 'ai'
          });

          if (this.isNewSession && !this.hasSentMessage) {
            this.$emit('first-message-sent');
            this.hasSentMessage = true;
          }
          
        } else {
          this.error = 'AIの応答生成に失敗しました';
        }
      } catch (error) {
        // console.error(error.response?.data?.message)
      } finally {
        this.isLoading = false;
      }
    },
    async fetchChatHistory(sessionId) {
      try {
        if (this.isNewSession) return;
        this.isLoading = true;
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');

        const response = await axios.get(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/session_management',
          {
            headers: {
              Authorization: `Bearer ${token}`
            },
            params: {
              session_id: sessionId,
              username: username
            }
          }
        );

        if (response.data.code === 200) {
          const contentData = response.data.content_data.content || [];
          this.messages = []

          contentData.forEach(([userMsg, aiMsg], index) => {
            this.messages.push({
              id: `${sessionId}_user_${index}`,
              text: userMsg,
              type: 'user'
            });
          
            this.messages.push({
              id: `${sessionId}_ai_${index}`,
              text: aiMsg,
              type: 'ai'
            });
          });
        }
      } catch (error) {
        this.error = '履歴の取得に失敗しました';
      } finally {
        this.isLoading = false;
      }
    },
    uploadFile(event) {
      const files = event.target.files;
      if (!files) return;

      const file = files[0]

      // 許可された拡張子
      const allowedExtensions = [
        '.xlsx', '.xls', '.txt', 
        '.pdf', '.docx', '.json',
        '.jpg', '.jpeg', '.png'
      ];

      // チェックサムファイルの種類
      const fileExt = file.name.toLowerCase().split('.').pop();
      if (!allowedExtensions.includes('.' + fileExt)) {
        Notification.error({
          title: 'ファイルフォーマット',
          message: `許可されていないファイル形式です（${allowedExtensions.join(', ')}）`,
          duration: 3000,
          offset: 60
        })
        event.target.value = '';
        return;
      }

       // 校正ファイルサイズ (5MB)
      if (file.size > 5 * 1024 * 1024) {
        Notification.error({
          title: '添付ファイル',
          message: '添付ファイルのサイズは5MBを超えません',
          duration: 3000,
          offset: 60
        })
        event.target.value = '';
        return;
      }

      this.uploadFileToServer(file, 'attachment');
      event.target.value = '';
    },
    saveMessage(event) {
      const files = event.target.files;

      if (!files) return;

      const file = files[0]
      // チェックサムファイルの種類
      const fileName = file.name.toLowerCase();
      if (!fileName.endsWith('.txt')) {
        Notification.error({
          title: 'ファイルフォーマット',
          message: 'プロンプトファイルは .txt のみ許可されています',
          duration: 3000,
          offset: 60
        })
        event.target.value = '';
        return;
      }

      // 校正ファイルサイズ (1MB)
      if (file.size > 1024 * 1024) {
        Notification.error({
          title: 'エラー',
          message: 'プロンプトファイルのサイズは1MBを超えないでください',
          duration: 3000,
          offset: 60
        })
        event.target.value = '';
        return;
      }

      this.uploadFileToServer(file, 'prompt');
      event.target.value = '';
    },
    async uploadFileToServer(file, type) {
      try {
        this.isUploading = true;
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        const formData = new FormData();
        formData.append('file', file);
        formData.append('username', username);

        await axios.post(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/upload_file',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (type === 'prompt') {
          this.promptName = file.name;
          Notification.success({
            title: 'プロンプトファイルをアップロードしました',
            message: 'ファイルのアップロードに成功',
            duration: 3000,
            offset: 60
          })
        } else if (type === 'attachment') {
          this.attachmentName = file.name;
          Notification.success({
            title: '添付ファイルをアップロードしました',
            message: 'ファイルのアップロードに成功',
            duration: 3000,
            offset: 60
          })
        }

        
      } catch (error) {
        Notification.error({
          title: 'ファイルのアップロード',
          message: error.response?.status === 413 
          ? 'ファイルサイズが制限を超えています' 
          : 'ファイルのアップロードに失敗しました',
          duration: 3000,
          offset: 60
        })
      } finally {
        this.isUploading = false;
      }
    },
    downloadHistory() {
      let content = '';
      this.messages.forEach(msg => {
        if (msg.type === 'user') {
          content += `ユーザー: ${msg.text}\n\n`;
        } else if (msg.type === 'ai') {
          const text = this.convertHtmlToText(msg.text);
          content += `AI: ${text}\n\n`;
        }
      });
      
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_history_${this.sessionId || new Date().getTime()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    convertHtmlToText(html) {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = html;
      return tempDiv.textContent.replace(/\n\s*\n/g, '\n').trim();
    },
    async deleteFile(filename) {
      try {
        const token = sessionStorage.getItem('token');
        const username = sessionStorage.getItem('username');
        
        const response = await axios.delete(
          'https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/upload_file',
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            params: {
              username: username,
              filename: filename,
            }
          }
        );

        if (response.data.code === 200) {
          if (this.promptName === filename) {
            this.promptName = '';
          } else if (this.attachmentName === filename) {
            this.attachmentName = '';
          }
          Notification.success({
            title: 'ファイルの削除',
            message: 'ファイルを削除しました',
            duration: 3000,
            offset: 60
          })
        }
      } catch (error) {
        Notification.error({
          title: 'ファイルの削除',
          message: error.response?.status === 404 
          ? 'ファイルは既に削除されています' 
          : 'ファイル削除に失敗しました',
          duration: 3000,
          offset: 60
        })
      }
    },
    initMarkdownRenderer() {
      marked.setOptions({
        highlight: (code, language) => {
          const validLang = hljs.getLanguage(language) ? language : 'plaintext';
          return hljs.highlight(code, { language: validLang }).value;
        },
        breaks: true,
        gfm: true
      });

      marked.use({
        extensions: [{
          name: 'katex',
          level: 'block',
          start(src) { return src.indexOf('$'); },
          tokenizer(src) {
            const match = src.match(/^\$\$([\s\S]+?)\$\$/);
            if (match) return { type: 'katex', raw: match[0], text: match[1].trim() };
          },
          renderer(token) {
            return katex.renderToString(token.text, { displayMode: true });
          }
        }]
      });
    },
    renderMarkdown(content) {
      const rawHtml = marked(content);
      const cleanHtml = DOMPurify.sanitize(rawHtml, {
        ADD_TAGS: ['iframe'],
        ADD_ATTR: ['allowfullscreen', 'frameborder', 'scrolling']
      });

      return cleanHtml;
    },
  }
};
</script>

<style scoped>
.airesp {
  background: linear-gradient(145deg, #f8fff8, #e8f5e8);
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  word-wrap: break-word;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  white-space: pre-wrap;
  flex-grow: 1;
}
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.message {
  padding: 12px 16px;
  margin: 8px 0;
  border-radius: 8px;
  max-width: 80%;
  word-wrap: break-word;
  white-space: pre-wrap;
}
.user {
  background: linear-gradient(145deg, #f0f8ff, #e3f2fd);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-left: auto;
}
.ai-message-container {
  display: flex;
  align-items: flex-start;
  width: 100%;
  margin: 8px 0;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
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
.button-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}
.resizer {
  height: 5px;
  cursor: ns-resize;
}
.chat-input-container {
  padding: 10px;
  position: relative;
  padding: 16px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
}
.airesp strong {
  font-weight: 600;
  color: #2c3e50;
}
.initial-prompt {
  background-color: #f0f4f8;
  color: #666;
  padding: 12px 20px;
  border-radius: 8px;
  margin: 16px auto;
  text-align: center;
  max-width: 80%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.uploading-message {
  background-color: #2196F3;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  margin: 16px auto;
  text-align: center;
  max-width: 80%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

.history-btn{
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  background-color: #f5f5f5;
  border: 1px solid var(--border-color);
  padding: 0;
}

.file-display-area {
  margin-bottom: 8px;
}

.file-item {
  display: inline-flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 4px 8px;
  margin: 2px;
}

.file-name {
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9em;
}

.delete-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  margin-left: 4px;
  padding: 0 4px;
  font-size: 1.2em;
  line-height: 1;
  
  &:hover {
    color: #ff4444;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>