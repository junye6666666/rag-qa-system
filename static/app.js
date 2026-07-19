/* ============================================================
   RAG 知识库问答系统 - 前端交互逻辑
   ============================================================ */

// --- 状态 ---
const state = {
    isStreaming: false,
    chatHistory: [],
};

// --- DOM 元素 ---
const elements = {
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    fileUpload: document.getElementById('file-upload'),
    docList: document.getElementById('doc-list'),
    healthStatus: document.getElementById('health-status'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    topKSelect: document.getElementById('top-k-select'),
    streamMode: document.getElementById('stream-mode'),
};

// --- API 基础 ---
const API_BASE = '/api/v1';

async function api(method, path, body = null) {
    const opts = {
        method,
        headers: {},
    };
    if (body instanceof FormData) {
        opts.body = body;
    } else if (body) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(`${API_BASE}${path}`, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res;
}

// ============================================================
// 健康检查
// ============================================================

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        const dot = elements.healthStatus.querySelector('.dot');
        dot.className = 'dot connected';
        elements.healthStatus.innerHTML = '<span class="dot connected"></span> 服务正常';
        if (data.documents_count > 0) {
            elements.healthStatus.innerHTML += ` · ${data.documents_count} 个文档`;
        }
    } catch {
        const dot = elements.healthStatus.querySelector('.dot');
        dot.className = 'dot error';
        elements.healthStatus.innerHTML = '<span class="dot error"></span> 服务离线';
    }
}

// ============================================================
// 文档管理
// ============================================================

async function loadDocuments() {
    try {
        const res = await api('GET', '/documents');
        const data = await res.json();
        renderDocumentList(data.documents);
    } catch (e) {
        console.error('加载文档列表失败:', e);
    }
}

function renderDocumentList(docs) {
    if (!docs || docs.length === 0) {
        elements.docList.innerHTML = '<p class="empty-hint">暂无文档，上传一个试试吧</p>';
        return;
    }

    elements.docList.innerHTML = docs.map(doc => {
        const sizeStr = doc.size_bytes > 1024 * 1024
            ? `${(doc.size_bytes / (1024 * 1024)).toFixed(1)} MB`
            : doc.size_bytes > 1024
                ? `${(doc.size_bytes / 1024).toFixed(1)} KB`
                : `${doc.size_bytes} B`;
        return `
            <div class="doc-item">
                <div class="doc-item-info">
                    <div class="doc-item-name" title="${escapeHtml(doc.filename)}">
                        ${getFileIcon(doc.file_type)} ${escapeHtml(doc.filename)}
                    </div>
                    <div class="doc-item-meta">${sizeStr} · ${doc.chunk_count} 片段</div>
                </div>
                <button class="doc-item-delete" onclick="deleteDocument('${escapeHtml(doc.filename)}')" title="删除">
                    ✕
                </button>
            </div>
        `;
    }).join('');
}

function getFileIcon(ext) {
    const icons = { '.pdf': '📕', '.txt': '📄', '.md': '📝', '.docx': '📘' };
    return icons[ext] || '📎';
}

async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '上传失败');

        addSystemMessage(`✅ ${data.message}`);
        await loadDocuments();
        await checkHealth();
    } catch (e) {
        addSystemMessage(`❌ 上传失败: ${e.message}`);
    }
}

async function deleteDocument(filename) {
    if (!confirm(`确定要删除文档 "${filename}" 吗？\n该操作将从知识库中移除该文档的所有内容。`)) {
        return;
    }

    try {
        const res = await api('DELETE', `/documents/${encodeURIComponent(filename)}`);
        const data = await res.json();
        addSystemMessage(`🗑️ ${data.message}`);
        await loadDocuments();
        await checkHealth();
    } catch (e) {
        addSystemMessage(`❌ 删除失败: ${e.message}`);
    }
}

// ============================================================
// 聊天功能
// ============================================================

async function sendMessage() {
    const question = elements.chatInput.value.trim();
    if (!question || state.isStreaming) return;

    // 清空输入
    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';
    elements.sendBtn.disabled = true;

    // 隐藏欢迎消息
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    // 添加用户消息
    addUserMessage(question);

    // 添加 AI 消息占位
    const aiMsgId = addAssistantMessagePlaceholder();

    if (elements.streamMode.checked) {
        await streamChat(question, aiMsgId);
    } else {
        await syncChat(question, aiMsgId);
    }
}

async function syncChat(question, msgId) {
    try {
        const topK = parseInt(elements.topKSelect.value);
        const res = await api('POST', '/chat', { question, top_k: topK });
        const data = await res.json();

        updateAssistantMessage(msgId, data.answer, data.sources);
    } catch (e) {
        updateAssistantMessage(msgId, `❌ 出错了: ${e.message}`, []);
    } finally {
        elements.sendBtn.disabled = false;
        elements.chatInput.focus();
    }
}

async function streamChat(question, msgId) {
    state.isStreaming = true;

    try {
        const topK = parseInt(elements.topKSelect.value);
        const res = await fetch(`${API_BASE}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, top_k: topK }),
        });

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let sources = [];
        let answer = '';
        let buffer = '';
        let initialized = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event: sources')) continue;

                if (line.startsWith('event: error')) continue;

                if (line.startsWith('data: ')) {
                    const data = line.slice(6);

                    if (data === '[DONE]') break;

                    // 尝试解析为 JSON（sources 事件）
                    if (!initialized && line.includes('[{')) {
                        try {
                            // 找到 sources 数据 - 在后续的 data 行中
                            const sourcesMatch = line.match(/data: (\[.*\])/);
                            if (sourcesMatch) {
                                sources = JSON.parse(sourcesMatch[1]);
                                initialized = true;
                                continue;
                            }
                        } catch {}
                    }

                    if (data !== '[DONE]') {
                        answer += data;
                        updateAssistantMessageContent(msgId, answer);
                    }
                }
            }
        }

        // 最终更新（带来源）
        updateAssistantMessage(msgId, answer, sources);
    } catch (e) {
        updateAssistantMessage(msgId, `❌ 出错了: ${e.message}`, []);
    } finally {
        state.isStreaming = false;
        elements.sendBtn.disabled = false;
        elements.chatInput.focus();
    }
}

// --- 消息渲染 ---

function addUserMessage(text) {
    const msg = createMessageElement('user', text);
    elements.chatMessages.appendChild(msg);
    scrollToBottom();
    return msg.id;
}

function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'system-message';
    div.style.cssText = 'text-align:center;padding:8px;font-size:0.8rem;color:#64748b;';
    div.textContent = text;
    elements.chatMessages.appendChild(div);
    scrollToBottom();
}

function addAssistantMessagePlaceholder() {
    const id = 'msg-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant';
    msgDiv.dataset.id = id;
    msgDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    elements.chatMessages.appendChild(msgDiv);
    scrollToBottom();
    return id;
}

function updateAssistantMessageContent(msgId, text) {
    const msgDiv = document.querySelector(`.message[data-id="${msgId}"]`);
    if (!msgDiv) return;

    const bubble = msgDiv.querySelector('.message-bubble');
    bubble.innerHTML = renderMarkdown(text);
    scrollToBottom();
}

function updateAssistantMessage(msgId, text, sources) {
    const msgDiv = document.querySelector(`.message[data-id="${msgId}"]`);
    if (!msgDiv) return;

    const bubble = msgDiv.querySelector('.message-bubble');
    let html = renderMarkdown(text);

    if (sources && sources.length > 0) {
        html += `
            <div class="sources-section">
                <button class="sources-toggle" onclick="toggleSources(this)">
                    📚 查看引用来源 (${sources.length})
                </button>
                <div class="sources-list">
                    ${sources.map((s, i) => `
                        <div class="source-item">
                            <div class="source-name">📄 ${escapeHtml(s.source)}</div>
                            <div class="source-content">${escapeHtml(s.content.substring(0, 200))}...</div>
                            <div class="source-score">相关度: ${(s.score * 100).toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    bubble.innerHTML = html;
    scrollToBottom();
}

function createMessageElement(role, text) {
    const id = 'msg-' + Date.now();
    const avatar = role === 'user' ? '👤' : '🤖';
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.dataset.id = id;
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-bubble">${renderMarkdown(text)}</div>
    `;
    return div;
}

function toggleSources(btn) {
    const list = btn.nextElementSibling;
    list.classList.toggle('open');
    btn.textContent = list.classList.contains('open')
        ? '📚 收起引用来源'
        : `📚 查看引用来源`;
}

// --- 简单 Markdown 渲染 ---
function renderMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`{3}(\w*)\n?([\s\S]*?)`{3}/g, '<pre><code>$2</code></pre>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>')
        .replace(/^\- (.+)$/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// ============================================================
// 事件监听
// ============================================================

// 发送按钮
elements.sendBtn.addEventListener('click', sendMessage);

// Enter 发送，Shift+Enter 换行
elements.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 自动调整输入框高度
elements.chatInput.addEventListener('input', () => {
    elements.chatInput.style.height = 'auto';
    elements.chatInput.style.height = Math.min(elements.chatInput.scrollHeight, 120) + 'px';
});

// 文件上传
elements.fileUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadDocument(file);
        elements.fileUpload.value = '';
    }
});

// 清空对话
elements.clearChatBtn.addEventListener('click', () => {
    if (confirm('确定要清空当前对话吗？')) {
        elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🤖</div>
                <h3>欢迎使用 RAG 知识库问答系统</h3>
                <p>上传文档到知识库，然后向我提问，我会基于文档内容为你解答。</p>
                <div class="quick-actions">
                    <p>💡 <strong>快速开始：</strong></p>
                    <ol>
                        <li>在左侧上传你的文档（PDF、Word、Markdown 等）</li>
                        <li>等待文档处理完成</li>
                        <li>在下方输入框中提问</li>
                    </ol>
                </div>
            </div>
        `;
    }
});

// ============================================================
// 初始化
// ============================================================

async function init() {
    await checkHealth();
    await loadDocuments();
    setInterval(checkHealth, 30000); // 每 30 秒检查健康状态
}

init();
