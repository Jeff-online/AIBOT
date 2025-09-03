<template>
  <div class="login-container" :class="{ 'shake': errorMessage }">
    <!-- <h1>PILOT</h1> -->
    <div class="title-wrapper">
      <h1 class="gradient-title">
        <i class="iconfont icon-drone"></i>
        PILOT
      </h1>
      <div class="title-decoration"></div>
    </div>
    <form @submit.prevent="handleLogin">
      <input type="text" v-model="username" placeholder="ユーザーID" required />
      <input type="password" v-model="password" placeholder="パスワード" required />
      <button type="submit" :disabled="loading">
        {{ loading ? "ログイン中..." : "ログイン" }}
      </button>
    </form>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",
      errorMessage: "",
      loading: false
    };
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.errorMessage = "ユーザーIDとパスワードを入力してください";
        return;
      }

      this.loading = true;
      this.errorMessage = "";

      try {
        // ログインリクエストを送信する
        const response = await axios.post("https://ailab-webapp3-d9hhbadcdnaxewek.japaneast-01.azurewebsites.net/dev-api/login", {
          username: this.username,
          password: this.password
        });
        // ログインに成功した場合
        if (response.data.success) {

          sessionStorage.setItem("permission", response.data.permission);
          sessionStorage.setItem("userid", response.data.UserId);
          sessionStorage.setItem("token", response.data.token);
          sessionStorage.setItem("username", this.username);

          this.$router.push("/"); // ログイン成功後のジャンプ
        } else if(response.data.success === 410) {
          this.errorMessage = "ユーザーがロックアウトされました 管理者に連絡してください";
        } else {
          this.errorMessage = "ユーザーIDまたはパスワードが間違っています";
        }
      } catch (error) {
        this.errorMessage = "ログインに失敗しました。後でもう一度お試しください。";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
body {
margin: 0;
padding: 0;
font-family: Arial, sans-serif;
background-color: var(--bg-light);
height: 100vh;
display: flex;
align-items: center;
justify-content: center;
}

.login-container {
  --primary-color: #5bc0de;
  --error-color: #ff4444;
  --success-color: #00C851;
  background: white;
  padding: 40px;
  border-radius: 5px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 360px;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
}

.login-container.shake {
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translate(-50%, -50%); }
  25% { transform: translate(-55%, -50%); }
  75% { transform: translate(-45%, -50%); }
}

h1 {
color: var(--text-color);
text-align: center;
margin-bottom: 30px;
font-size: 24px;
}

form {
display: flex;
flex-direction: column;
gap: 16px;
}

.input-group {
position: relative;
}

input {
width: 100%;
padding: 10px;
border: 1px solid var(--border-color);
border-radius: 5px;
font-size: 16px;
box-sizing: border-box;
}

input:focus {
outline: none;
border-color: var(--primary-color);
}

button {
width: 100%;
background-color: var(--primary-color);
color: white;
padding: 10px;
border: none;
border-radius: 5px;
font-size: 16px;
cursor: pointer;
transition: background-color 0.2s;
}

button:hover {
background-color: var(--primary-hover);
}

.error-message {
color: var(--error-color);
font-size: 14px;
margin-top: 4px;
}

.success-message {
color: var(--success-color);
font-size: 14px;
margin-top: 4px;
} 

.title-wrapper {
  position: relative;
  margin-bottom: 40px;
}

.gradient-title {
  font-size: 32px;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  z-index: 2;
  text-shadow: 0 2px 4px rgba(76, 175, 254, 0.3);
}

.icon-drone {
  margin-right: 12px;
  font-size: 28px;
  vertical-align: middle;
}

.title-decoration {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, transparent, #4facfe, transparent);
  opacity: 0.8;
}

.login-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 
    0 8px 32px rgba(31, 38, 135, 0.15),
    inset 0 0 12px rgba(255, 255, 255, 0.3);
  padding: 40px 30px;
  border-radius: 16px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

input {
  transition: all 0.3s ease;
  background: rgba(245, 248, 250, 0.8);
}

input:focus {
  box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
}

button {
  position: relative;
  overflow: hidden;
}

button:disabled::after {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 200%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 25%,
    rgba(255,255,255,0.3) 50%,
    transparent 75%
  );
  animation: loading 1.5s infinite;
}


</style>

