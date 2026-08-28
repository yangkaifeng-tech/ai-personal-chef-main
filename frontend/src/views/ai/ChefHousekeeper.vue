<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import { Delete, Plus, UploadFilled } from '@element-plus/icons-vue'
import {
  clearConversation,
  fetchConversationMessages,
  fetchConversations,
  streamChat,
  uploadImage,
} from '../../api/chat'
import type { ChatMessage, ConversationInfo } from '../../types/api'

const markdown = new MarkdownIt({ breaks: true, linkify: true })
const conversations = ref<ConversationInfo[]>([])
const activeConversationId = ref<string | null>(null)
const messages = ref<ChatMessage[]>([])
const input = ref('这是我现有的食材，请推荐适合的菜谱。')
const imageFile = ref<File | null>(null)
const imagePreview = ref('')
const sending = ref(false)
const messagePanel = ref<HTMLElement>()

const activeConversation = computed(() =>
  conversations.value.find((item) => item.id === activeConversationId.value),
)

function renderMarkdown(content: string) {
  return DOMPurify.sanitize(markdown.render(content))
}

async function scrollBottom() {
  await nextTick()
  if (messagePanel.value) {
    messagePanel.value.scrollTop = messagePanel.value.scrollHeight
  }
}

async function loadConversations() {
  const data = await fetchConversations()
  conversations.value = data.conversations
  if (!activeConversationId.value && data.conversations[0]) {
    await selectConversation(data.conversations[0].id)
  }
}

async function selectConversation(id: string) {
  activeConversationId.value = id
  const data = await fetchConversationMessages(id)
  messages.value = data.messages
  await scrollBottom()
}

function newConversation() {
  activeConversationId.value = null
  messages.value = []
  input.value = '这是我现有的食材，请推荐适合的菜谱。'
}

function onFileChange(file: File) {
  imageFile.value = file
  if (imagePreview.value) {
    URL.revokeObjectURL(imagePreview.value)
  }
  imagePreview.value = URL.createObjectURL(file)
}

function clearImage() {
  imageFile.value = null
  if (imagePreview.value) {
    URL.revokeObjectURL(imagePreview.value)
  }
  imagePreview.value = ''
}

async function sendMessage() {
  if (!input.value.trim() && !imageFile.value) {
    ElMessage.warning('请输入内容或上传图片')
    return
  }
  sending.value = true
  try {
    let imageUrl: string | null = null
    if (imageFile.value) {
      imageUrl = await uploadImage(imageFile.value)
    }
    const userText = input.value.trim() || '这是我现有的食材，请推荐适合的菜谱。'
    messages.value.push({ role: 'user', content: userText, image_url: imageUrl })
    messages.value.push({ role: 'assistant', content: '' })
    input.value = ''
    clearImage()
    await scrollBottom()

    await streamChat(
      {
        message: userText,
        image_url: imageUrl,
        conversation_id: activeConversationId.value,
      },
      (event) => {
        if (event.event === 'conversation') {
          activeConversationId.value = event.payload.conversation_id
        }
        if (event.event === 'status') {
          const assistant = messages.value[messages.value.length - 1]
          assistant.status_content = event.payload.content
          void scrollBottom()
        }
        if (event.event === 'message') {
          const assistant = messages.value[messages.value.length - 1]
          assistant.status_content = ''
          assistant.content += event.payload.content
          void scrollBottom()
        }
      },
    )
    await loadConversations()
  } finally {
    sending.value = false
  }
}

async function removeCurrentConversation() {
  if (!activeConversationId.value) {
    return
  }
  await ElMessageBox.confirm('确认清空当前 AI 管家会话？', '清空确认', { type: 'warning' })
  await clearConversation(activeConversationId.value)
  messages.value = []
  await loadConversations()
  ElMessage.success('会话已清空')
}

onMounted(loadConversations)
</script>

<template>
  <div class="chef-page">
    <aside class="conversation-list page-card">
      <div class="conversation-header">
        <strong>私厨会话</strong>
        <el-button :icon="Plus" size="small" @click="newConversation">新会话</el-button>
      </div>
      <div class="conversation-items">
        <button
          v-for="conversation in conversations"
          :key="conversation.id"
          class="conversation-item"
          :class="{ active: conversation.id === activeConversationId }"
          type="button"
          @click="selectConversation(conversation.id)"
        >
          <span>{{ conversation.title }}</span>
          <small>{{ new Date(conversation.updated_at).toLocaleString() }}</small>
        </button>
      </div>
    </aside>

    <section class="chat-panel page-card">
      <div class="chat-header">
        <div>
          <h2>私厨管家</h2>
          <p class="muted">{{ activeConversation?.title ?? '上传食材图片或输入食材，让 AI 推荐菜谱。' }}</p>
        </div>
        <el-button :icon="Delete" :disabled="!activeConversationId" @click="removeCurrentConversation">清空会话</el-button>
      </div>

      <div ref="messagePanel" class="messages">
        <el-empty v-if="messages.length === 0" description="暂无消息，开始一次菜谱推荐。" />
        <article v-for="(message, index) in messages" :key="`${message.role}-${index}`" class="message" :class="message.role">
          <div class="message-role">{{ message.role === 'user' ? '我' : 'AI 私厨' }}</div>
          <div class="bubble">
            <img v-if="message.image_url" :src="message.image_url" alt="上传食材" class="uploaded-image" />
            <div
              v-if="message.role === 'assistant'"
              v-html="renderMarkdown(message.content || message.status_content || '正在生成...')"
            />
            <p v-else>{{ message.content }}</p>
          </div>
        </article>
      </div>

      <div class="composer">
        <div v-if="imagePreview" class="preview">
          <img :src="imagePreview" alt="待上传食材" />
          <el-button size="small" @click="clearImage">移除</el-button>
        </div>
        <el-input
          v-model="input"
          type="textarea"
          :rows="3"
          placeholder="输入你想吃什么，或上传冰箱食材图片。"
          resize="none"
        />
        <div class="composer-actions">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="(file: UploadFile) => file.raw && onFileChange(file.raw)"
          >
            <el-button :icon="UploadFilled">上传图片</el-button>
          </el-upload>
          <el-button type="primary" :loading="sending" @click="sendMessage">发送</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.chef-page {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  height: calc(100vh - 104px);
}

.conversation-list,
.chat-panel {
  min-height: 0;
}

.conversation-header,
.chat-header,
.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chat-header {
  padding-bottom: 14px;
  border-bottom: 1px solid #e2e8f0;
}

.chat-header h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.chat-header p {
  margin: 0;
}

.conversation-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 14px;
}

.conversation-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  color: #0f172a;
  text-align: left;
  cursor: pointer;
}

.conversation-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.conversation-item small {
  color: #64748b;
}

.chat-panel {
  display: grid;
  grid-template-rows: auto 1fr auto;
}

.messages {
  min-height: 0;
  overflow: auto;
  padding: 16px 0;
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
}

.message-role {
  margin-bottom: 6px;
  color: #64748b;
  font-size: 12px;
}

.bubble {
  display: inline-block;
  max-width: 78%;
  padding: 12px 14px;
  border-radius: 12px;
  background: #f1f5f9;
  text-align: left;
  line-height: 1.7;
}

.user .bubble {
  background: #2563eb;
  color: #fff;
}

.uploaded-image,
.preview img {
  max-width: 220px;
  max-height: 160px;
  border-radius: 8px;
  object-fit: cover;
}

.composer {
  display: grid;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}

.preview {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}
</style>
