<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>
<script>
export default {
  name: 'App',
  components: {}
}
</script>

<style>
.custom-confirm-box {
  width: 450px !important;
  border-radius: 8px !important;
}

.custom-confirm-box .el-message-box__header {
  background: #f8f8f8;
  padding: 15px;
  border-radius: 8px 8px 0 0;
}

.custom-confirm-box .el-message-box__title {
  font-size: 18px;
  color: #333;
}

.custom-confirm-box .el-message-box__content {
  padding: 20px 15px;
  font-size: 16px;
}

.custom-confirm-box .el-message-box__btns {
  padding: 15px;
  margin-left: 0px;
  justify-content: flex-end;
}

.custom-confirm-box .el-message-box__btns button:nth-child(2) {
  margin-left: 0px;
}

.custom-confirm-box .el-button {
  padding: 8px 20px;
  margin-bottom: 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.custom-confirm-box .el-button--primary {
  background-color: #66B1FF;
  border-color: #66B1FF;
}

.custom-confirm-box .el-button--primary:hover {
  background-color: #ff7875;
  border-color: #ff7875;
}

.markdown-content pre {
  background: #f5f5f5 !important;
  border-radius: 8px !important;
  padding: 16px !important;
  margin: 12px 0 !important;
  overflow-x: auto !important;
}

.markdown-content code {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
}

.markdown-content pre code.hljs {
  background: transparent;
  padding: 0;
}

/* Katex 数学の公式スタイル */
.katex { 
  font-size: 1.1em;
  padding: 0 4px;
}

.katex-display {
  margin: 1em 0;
  overflow-x: auto;
  overflow-y: hidden;
}
</style>

