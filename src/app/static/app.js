(() => {
  const API = "/api/v1";
  const $ = (selector) => document.querySelector(selector);
  const messagesEl = $("#messages");
  const welcomeEl = $("#welcome");
  const composer = $("#composer");
  const messageInput = $("#messageInput");
  const imageInput = $("#imageInput");
  const uploadBtn = $("#uploadBtn");
  const sendBtn = $("#sendBtn");
  const cancelBtn = $("#cancelBtn");
  const preview = $("#preview");
  const previewImage = $("#previewImage");
  const previewName = $("#previewName");
  const toast = $("#toast");
  const conversation = $(".conversation");
  const scrollLatestBtn = $("#scrollLatestBtn");
  const charCount = $("#charCount");
  const connectionStatus = $("#connectionStatus");
  const newSessionDialog = $("#newSessionDialog");

  let selectedImage = null;
  let previewUrl = "";
  let activeController = null;
  let busy = false;
  let dragDepth = 0;
  let lastRequest = null;
  let threadId = localStorage.getItem("thread_id") || createId();
  const draftKey = `ai-chef-draft:${threadId}`;
  localStorage.setItem("thread_id", threadId);

  function createId() {
    return crypto.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  function escapeHtml(value = "") {
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    })[char]);
  }

  function safeMarkdown(value) {
    const lines = String(value).replace(/\r/g, "").split("\n");
    let html = "";
    let list = null;
    const closeList = () => { if (list) html += `</${list}>`; list = null; };
    for (let index = 0; index < lines.length; index += 1) {
      const raw = lines[index];
      const line = raw.trimEnd();
      const heading = line.match(/^(#{1,3})\s+(.+)/);
      const unordered = line.match(/^[-*]\s+(.+)/);
      const ordered = line.match(/^\d+[.)]\s+(.+)/);
      const tableRow = parseTableRow(line);
      const nextRow = parseTableRow(lines[index + 1] || "");
      if (tableRow && nextRow && nextRow.every((cell) => /^:?-{3,}:?$/.test(cell))) {
        closeList();
        html += "<div class=\"table-scroll\"><table><thead><tr>";
        html += tableRow.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join("");
        html += "</tr></thead><tbody>";
        index += 2;
        while (index < lines.length) {
          const cells = parseTableRow(lines[index]);
          if (!cells) break;
          html += `<tr>${cells.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("")}</tr>`;
          index += 1;
        }
        html += "</tbody></table></div>";
        index -= 1;
        continue;
      }
      if (heading) {
        closeList();
        const level = heading[1].length;
        html += `<h${level}>${inlineMarkdown(heading[2])}</h${level}>`;
      } else if (/^---+$/.test(line.trim())) {
        closeList();
        html += "<hr>";
      } else if (/^>\s?/.test(line)) {
        closeList();
        const quote = line.replace(/^>\s?/, "");
        if (quote) html += `<blockquote>${inlineMarkdown(quote)}</blockquote>`;
      } else if (unordered || ordered) {
        const nextList = unordered ? "ul" : "ol";
        if (list !== nextList) { closeList(); list = nextList; html += `<${list}>`; }
        html += `<li>${inlineMarkdown((unordered || ordered)[1])}</li>`;
      } else if (!line.trim()) {
        closeList();
      } else {
        closeList();
        html += `<p>${inlineMarkdown(line)}</p>`;
      }
    }
    closeList();
    return html;
  }

  function parseTableRow(line) {
    const trimmed = String(line).trim();
    if (!trimmed.startsWith("|") || !trimmed.endsWith("|")) return null;
    return trimmed.slice(1, -1).split("|").map((cell) => cell.trim());
  }

  function inlineMarkdown(value) {
    const tokens = [];
    const stash = (html) => {
      const token = `\uE000${tokens.length}\uE001`;
      tokens.push(html);
      return token;
    };
    let source = String(value);

    source = source.replace(/!\[([^\]]*)\]\((https?:\/\/[^\s)]+)(?:\s+"[^"]*")?\)/gi, (_match, alt, url) => {
      return stash(imagePreview(url, alt || "菜品预览图"));
    });

    source = source.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)(?:\s+"[^"]*")?\)/gi, (_match, label, url) => {
      if (isLikelyImage(url, label)) return stash(imagePreview(url, label));
      const safeUrl = safeExternalUrl(url);
      if (!safeUrl) return escapeHtml(label);
      return stash(`<a class="external-link" href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`);
    });

    source = source.replace(/(^|[\s(])((?:https?:\/\/)[^\s<>)]+\.(?:png|jpe?g|webp|gif|avif)(?:\?[^\s<>)]*)?)/gi, (_match, prefix, url) => {
      return `${prefix}${stash(imagePreview(url, "菜品预览图"))}`;
    });

    let rendered = escapeHtml(source)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/`(.+?)`/g, "<code>$1</code>");
    rendered = rendered.replace(/\uE000(\d+)\uE001/g, (_match, index) => tokens[Number(index)] || "");
    return rendered;
  }

  function safeExternalUrl(value) {
    try {
      const url = new URL(String(value));
      const blockedHosts = new Set(["example.com", "www.example.com"]);
      if (blockedHosts.has(url.hostname.toLowerCase())) return "";
      return ["http:", "https:"].includes(url.protocol) ? url.href : "";
    } catch {
      return "";
    }
  }

  function isLikelyImage(url, label = "") {
    return /\.(?:png|jpe?g|webp|gif|avif)(?:[?#]|$)/i.test(url)
      || /(图片|配图|参考图|预览图|成品图|image|photo)/i.test(label);
  }

  function imagePreview(url, label) {
    const safeUrl = safeExternalUrl(url);
    if (!safeUrl) return "";
    const safeSrc = escapeHtml(safeUrl);
    const safeLabel = escapeHtml(label || "菜品预览图");
    return `<span class="recipe-image"><img src="${safeSrc}" alt="${safeLabel}" loading="lazy" referrerpolicy="no-referrer"><span class="recipe-image-caption"><b>${safeLabel}</b><a href="${safeSrc}" target="_blank" rel="noopener noreferrer">打开原图 ↗</a></span></span>`;
  }

  function showToast(message, kind = "") {
    toast.textContent = message;
    toast.className = `toast show ${kind}`.trim();
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => { toast.className = "toast"; }, 2800);
  }

  messagesEl.addEventListener("error", (event) => {
    const image = event.target;
    if (!(image instanceof HTMLImageElement) || !image.closest(".recipe-image")) return;
    const card = image.closest(".recipe-image");
    image.remove();
    card.classList.add("image-failed");
  }, true);

  function hideWelcome() {
    if (welcomeEl?.isConnected) welcomeEl.remove();
  }

  function isNearBottom() {
    return messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 90;
  }

  function scrollToLatest(force = false) {
    if (!force && !isNearBottom()) {
      scrollLatestBtn.hidden = false;
      return;
    }
    requestAnimationFrame(() => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
      scrollLatestBtn.hidden = true;
    });
  }

  function addMessage(role, content = "", imageUrl = "") {
    hideWelcome();
    const item = document.createElement("article");
    item.className = `message ${role}`;
    item.innerHTML = `<div class="avatar" aria-hidden="true">${role === "user" ? "🙂" : "👨‍🍳"}</div><div class="message-body"><div class="bubble"></div><div class="message-actions"></div></div>`;
    const bubble = item.querySelector(".bubble");
    if (imageUrl) {
      const image = document.createElement("img");
      image.src = imageUrl;
      image.alt = "上传的食材";
      bubble.appendChild(image);
    }
    if (role === "assistant") bubble.insertAdjacentHTML("beforeend", safeMarkdown(content));
    else {
      const paragraph = document.createElement("p");
      paragraph.textContent = content;
      bubble.appendChild(paragraph);
    }
    messagesEl.appendChild(item);
    const message = { item, bubble, actions: item.querySelector(".message-actions") };
    if (role === "assistant" && content) addMessageActions(message, content);
    scrollToLatest(true);
    return message;
  }

  function addMessageActions(message, copyText, retry = false) {
    message.actions.replaceChildren();
    if (copyText) {
      const copyButton = document.createElement("button");
      copyButton.className = "message-action";
      copyButton.type = "button";
      copyButton.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>复制菜谱`;
      copyButton.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(copyText);
          copyButton.textContent = "已复制";
          showToast("菜谱已复制到剪贴板");
          setTimeout(() => { copyButton.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>复制菜谱`; }, 1600);
        } catch { showToast("复制失败，请手动选择文字", "error"); }
      });
      message.actions.appendChild(copyButton);
    }
    if (retry) {
      const retryButton = document.createElement("button");
      retryButton.className = "message-action";
      retryButton.type = "button";
      retryButton.textContent = "↻ 重新生成";
      retryButton.addEventListener("click", retryLastRequest);
      message.actions.appendChild(retryButton);
    }
  }

  function addThinkingMessage() {
    const message = addMessage("assistant");
    const startedAt = Date.now();
    const status = document.createElement("span");
    message.bubble.innerHTML = `<div class="thinking"><span class="thinking-dots" aria-hidden="true"><i></i><i></i><i></i></span></div>`;
    message.bubble.querySelector(".thinking").appendChild(status);
    const update = () => {
      const seconds = Math.floor((Date.now() - startedAt) / 1000);
      const phase = seconds < 6 ? "正在理解你的需求" : seconds < 16 ? "正在搜索和比较菜谱" : "正在整理步骤与营养建议";
      status.textContent = `${phase} · ${seconds}s`;
    };
    update();
    const timer = setInterval(update, 1000);
    message.stopThinking = () => clearInterval(timer);
    return message;
  }

  function setBusy(value) {
    busy = value;
    messagesEl.setAttribute("aria-busy", String(value));
    messageInput.disabled = value;
    uploadBtn.disabled = value;
    sendBtn.disabled = value || (!messageInput.value.trim() && !selectedImage);
    cancelBtn.hidden = !value;
  }

  function autoResize() {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 132)}px`;
    charCount.textContent = `${messageInput.value.length} / 1000`;
    charCount.classList.toggle("near-limit", messageInput.value.length >= 900);
  }

  function clearImage() {
    selectedImage = null;
    imageInput.value = "";
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = "";
    preview.hidden = true;
    updateSendState();
  }

  function updateSendState() {
    sendBtn.disabled = busy || (!messageInput.value.trim() && !selectedImage);
  }

  function selectImage(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) { showToast("请选择图片文件", "error"); return; }
    if (file.size > 10 * 1024 * 1024) { showToast("图片请不要超过 10MB", "error"); clearImage(); return; }
    selectedImage = file;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = URL.createObjectURL(file);
    previewImage.src = previewUrl;
    previewName.textContent = file.name || "粘贴的食材图片";
    preview.hidden = false;
    updateSendState();
    showToast("已添加食材图片");
  }

  function updateConnectionStatus() {
    const online = navigator.onLine;
    connectionStatus.classList.toggle("offline", !online);
    connectionStatus.querySelector("span:last-child").textContent = online
      ? "看食材，想菜谱，今晚吃得更简单"
      : "网络已断开，恢复后可继续生成";
  }

  async function uploadImage(file) {
    const extension = (file.name.split(".").pop() || "jpg").toLowerCase();
    const filename = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}.${extension}`;
    const presign = await fetch(`${API}/oss/presign?filename=${encodeURIComponent(filename)}`);
    if (!presign.ok) throw new Error("暂时无法准备图片上传");
    const { uploadUrl, accessUrl, contentType } = await presign.json();
    const upload = await fetch(String(uploadUrl).replace(/^["']|["']$/g, ""), {
      method: "PUT", body: file, headers: { "Content-Type": contentType }
    });
    if (!upload.ok) throw new Error("图片上传失败，请稍后再试");
    return String(accessUrl).replace(/^["']|["']$/g, "");
  }

  async function streamChat(message, imageUrl, onChunk) {
    activeController = new AbortController();
    const timeout = setTimeout(() => activeController?.abort("timeout"), 180000);
    try {
      const response = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, image_url: imageUrl || null, thread_id: threadId }),
        signal: activeController.signal
      });
      if (!response.ok) throw new Error("请求失败");
      if (!response.body) throw new Error("浏览器无法读取流式回复");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        onChunk(decoder.decode(value, { stream: true }));
      }
      onChunk(decoder.decode());
    } finally {
      clearTimeout(timeout);
      activeController = null;
    }
  }

  async function sendMessage() {
    const text = messageInput.value.trim();
    const file = selectedImage;
    const localImage = previewUrl;
    if (busy || (!text && !file)) return;

    addMessage("user", text || "帮我看看这些食材能做什么？", localImage);
    messageInput.value = "";
    sessionStorage.removeItem(draftKey);
    autoResize();
    setBusy(true);

    let remoteImage = "";
    if (file) {
      showToast("正在上传食材图片…");
      try { remoteImage = await uploadImage(file); }
      catch (error) {
        addMessage("assistant", `图片没有上传成功：${error.message}`);
        setBusy(false);
        clearImage();
        return;
      }
    }
    clearImage();

    lastRequest = {
      text: text || "这是我现有的食材，请推荐适合的菜谱。",
      imageUrl: remoteImage
    };
    await generateResponse(lastRequest.text, lastRequest.imageUrl);
  }

  async function generateResponse(text, remoteImage) {
    const pending = addThinkingMessage();
    let answer = "";
    let receivedFirstChunk = false;
    try {
      await streamChat(text, remoteImage, (chunk) => {
        if (!chunk) return;
        if (!receivedFirstChunk) {
          receivedFirstChunk = true;
          pending.stopThinking();
        }
        answer += chunk;
        pending.bubble.innerHTML = safeMarkdown(answer);
        scrollToLatest();
      });
      pending.stopThinking();
      if (!answer.trim()) {
        const emptyCopy = "暂时没有生成内容，请换一种描述再试一次。";
        pending.bubble.innerHTML = safeMarkdown(emptyCopy);
        addMessageActions(pending, emptyCopy, true);
      } else {
        addMessageActions(pending, answer);
      }
    } catch (error) {
      pending.stopThinking();
      const stopped = error.name === "AbortError";
      const copy = stopped ? "本次生成已停止。你可以精简食材描述后重新尝试。" : "连接 AI 私厨时出了点问题，请稍后再试。";
      pending.bubble.innerHTML = safeMarkdown(copy);
      addMessageActions(pending, copy, true);
      if (!stopped) showToast("生成失败，请稍后再试", "error");
    } finally {
      setBusy(false);
      messageInput.focus();
    }
  }

  async function retryLastRequest() {
    if (busy || !lastRequest) return;
    setBusy(true);
    await generateResponse(lastRequest.text, lastRequest.imageUrl);
  }

  async function loadHistory() {
    try {
      const response = await fetch(`${API}/chat/messages?thread_id=${encodeURIComponent(threadId)}`);
      if (!response.ok) return;
      const data = await response.json();
      for (const message of data.messages || []) {
        const content = typeof message.content === "string" ? message.content : JSON.stringify(message.content);
        addMessage(message.role === "user" ? "user" : "assistant", content);
      }
    } catch { /* Demo 可离线展示首页，不打扰用户。 */ }
  }

  messageInput.addEventListener("input", () => {
    autoResize();
    updateSendState();
    sessionStorage.setItem(draftKey, messageInput.value);
  });
  messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendMessage(); }
  });
  messageInput.addEventListener("paste", (event) => {
    const image = Array.from(event.clipboardData?.files || []).find((file) => file.type.startsWith("image/"));
    if (!image) return;
    event.preventDefault();
    selectImage(image);
  });
  composer.addEventListener("submit", (event) => { event.preventDefault(); sendMessage(); });
  uploadBtn.addEventListener("click", () => imageInput.click());
  imageInput.addEventListener("change", () => {
    selectImage(imageInput.files?.[0]);
  });
  $("#removeImageBtn").addEventListener("click", clearImage);
  cancelBtn.addEventListener("click", () => activeController?.abort("user"));

  messagesEl.addEventListener("scroll", () => {
    if (isNearBottom()) scrollLatestBtn.hidden = true;
    else if (messagesEl.scrollHeight > messagesEl.clientHeight) scrollLatestBtn.hidden = false;
  }, { passive: true });
  scrollLatestBtn.addEventListener("click", () => scrollToLatest(true));

  conversation.addEventListener("dragenter", (event) => {
    if (![...(event.dataTransfer?.types || [])].includes("Files")) return;
    event.preventDefault();
    dragDepth += 1;
    conversation.classList.add("dragging");
  });
  conversation.addEventListener("dragover", (event) => {
    if (![...(event.dataTransfer?.types || [])].includes("Files")) return;
    event.preventDefault();
  });
  conversation.addEventListener("dragleave", () => {
    dragDepth = Math.max(0, dragDepth - 1);
    if (!dragDepth) conversation.classList.remove("dragging");
  });
  conversation.addEventListener("drop", (event) => {
    event.preventDefault();
    dragDepth = 0;
    conversation.classList.remove("dragging");
    selectImage(Array.from(event.dataTransfer?.files || []).find((file) => file.type.startsWith("image/")));
  });

  $("#newSessionBtn").addEventListener("click", () => newSessionDialog.showModal());
  $("#cancelNewSessionBtn").addEventListener("click", () => newSessionDialog.close());
  $("#confirmNewSessionBtn").addEventListener("click", async () => {
    newSessionDialog.close();
    activeController?.abort("new-session");
    try { await fetch(`${API}/chat/messages?thread_id=${encodeURIComponent(threadId)}`, { method: "DELETE" }); } catch {}
    threadId = createId();
    localStorage.setItem("thread_id", threadId);
    location.reload();
  });
  document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", () => {
      messageInput.value = button.textContent.replace(/^\S+\s*/, "");
      sessionStorage.setItem(draftKey, messageInput.value);
      autoResize(); updateSendState(); messageInput.focus();
    });
  });

  const savedDraft = sessionStorage.getItem(draftKey);
  if (savedDraft) messageInput.value = savedDraft;
  autoResize();
  updateSendState();
  updateConnectionStatus();
  window.addEventListener("online", updateConnectionStatus);
  window.addEventListener("offline", updateConnectionStatus);
  loadHistory();
})();
