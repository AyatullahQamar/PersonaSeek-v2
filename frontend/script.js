const defaultConfig = {
  main_title: 'PersonaSeek',
  welcome_message: 'Hello! How can I help you today?',
  input_placeholder: 'Message PersonaSeek',
  background_color: '#001a33',
  sidebar_color: '#000d1a',
  text_color: '#ececf1',
  accent_color: '#0059b3',
  secondary_surface: '#003d66'
};

const API_BASE = "https://personaseek-v2.onrender.com"; // change if your backend runs elsewhere

function parseQuery(text) {
  const m = text.match(/^\s*(.+?)\s*(?:in|near|at)\s+(.+)\s*$/i);
  if (m) return { profession: m[1].trim(), location: m[2].trim() };

  const parts = text.split(",").map(s => s.trim()).filter(Boolean);
  if (parts.length >= 2) return { profession: parts[0], location: parts.slice(1).join(", ") };

  return null;
}
function formatPeopleList(people) {
  // Escape user-provided fields to keep HTML safe
  const esc = (v) => String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
  
  
  const getDomain = (url) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');

  } catch {
    return '';
  }
};


  if (!Array.isArray(people) || people.length === 0) {
    return `<div class="text-gray-300">No results found. Try a different profession or location.</div>`;
  }

  const top = people.slice(0, 10);
let out = `<div class="results-wrap">`;
out += `<div class="results-head">Found ${people.length} results (showing top ${top.length}):</div>`;
out += `<div class="results-grid">`;   // ✅ ADD THIS LINE

  top.forEach((p, i) => {
    const name = p?.name || 'N/A';
    const address = p?.address || 'N/A';
    const contact = p?.phone || p?.contact || 'N/A';
    const website = p?.website || '';
    const domain = website ? getDomain(website) : '';
    const logoUrl = domain
  ? `https://www.google.com/s2/favicons?sz=64&domain=${encodeURIComponent(domain)}`
  : "";


    const rating = (p?.rating ?? 'N/A');

    const mapsUrl =
      address !== 'N/A'
        ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(String(name) + " " + String(address))}`
        : '';

    // Profile icon per result: first letter of name
    const letter = (name && name !== 'N/A') ? String(name).trim().charAt(0).toUpperCase() : '?';

    out += `
      <div class="result-card">
        <div class="result-avatar">
  ${logoUrl
    ? `<img src="${logoUrl}" alt="" onerror="this.style.display='none'">`
    : esc(letter)
  }
</div>


        <div class="result-body">
          <div class="result-title">
            
            <span class="result-name">${esc(name)}</span>
          </div>

          <div class="result-meta">
           
            <div><b>Contact:</b> ${esc(contact)}</div>
            <div><b>Rating:</b> ${esc(rating)}</div>
          </div>

          <div class="result-actions">
            ${mapsUrl ? `<a class="smart-link" href="${mapsUrl}" target="_blank" rel="noopener noreferrer">📍 Maps</a>` : ''}
            ${website ? `<a class="smart-link" href="${esc(website)}" target="_blank" rel="noopener noreferrer">🌐 Website</a>` : ''}
          </div>
        </div>
      </div>
    `;
  });
  out += `</div>`; // ✅ closes results-grid

  out += `</div>`;
  return out;
}




const messagesContainer = document.getElementById('messages-container');
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const sendButton = document.getElementById('send-button');

let allData = [];
let currentChatId = 'chat-' + Date.now();
let isProcessing = false;

const aiResponses = [
  "I'd be happy to help you with that. Let me provide some information on this topic.",
  "That's an interesting question. Here's what I can tell you about it.",
  "I understand what you're asking. Let me break this down for you.",
  "Great question! Here's my perspective on that.",
  "I can certainly help with that. Here's what you need to know.",
  "Thanks for asking. Let me explain this in detail.",
  "That's a thoughtful inquiry. Here's what I think about it.",
  "I appreciate you bringing this up. Let me share some insights."
];

// Auto-resize textarea + enable/disable send button
messageInput.addEventListener('input', function () {
  this.style.height = 'auto';
  const newHeight = Math.min(this.scrollHeight, 200);
  this.style.height = newHeight + 'px';

  sendButton.disabled = !this.value.trim() || isProcessing;
});

// Handle Enter (send) vs Shift+Enter (newline)
messageInput.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (this.value.trim() && !isProcessing) {
      chatForm.dispatchEvent(new Event('submit'));
    }
  }
});

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text ?? '';
  return div.innerHTML;
}

function renderMessages(data) {
  const currentMessages = data.filter(
    (item) => item.type === 'message' && item.chatId === currentChatId
  );

  messagesDiv.innerHTML = '';

  // Welcome message
  const welcomeDiv = document.createElement('div');
  welcomeDiv.className = 'message-assistant message-animate py-8 px-6';
  welcomeDiv.innerHTML = `
    <div class="flex gap-6">
      <div class="w-8 h-8 rounded-sm bg-gray-700 flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
      </div>
      <div class="flex-1 pt-1">
        <div class="markdown-content text-gray-100 text-base leading-7">
          <p id="welcome-text">${escapeHtml(window.elementSdk?.config?.welcome_message || defaultConfig.welcome_message)}</p>
        </div>
      </div>
    </div>
  `;
  messagesDiv.appendChild(welcomeDiv);

  const sortedMessages = [...currentMessages].sort((a, b) => a.timestamp - b.timestamp);

sortedMessages.forEach((msg) => {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message-animate py-8 px-6 ${
    msg.isUser ? 'message-user' : 'message-assistant'
  }`;

  // ✅ DEFINE ICON (THIS WAS MISSING)
  const icon = msg.isUser
    ? `<div class="w-8 h-8 rounded-sm bg-gray-600 flex items-center justify-center flex-shrink-0">
         <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
             d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
         </svg>
       </div>`
    : `<div class="w-8 h-8 rounded-sm bg-gray-700 flex items-center justify-center flex-shrink-0">
         <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
             d="M13 10V3L4 14h7v7l9-11h-7z"></path>
         </svg>
       </div>`;

  messageDiv.innerHTML = `
    <div class="flex gap-6">
      ${icon}
      <div class="flex-1 pt-1">
        <div class="markdown-content text-gray-100 text-base leading-7 whitespace-pre-line message-text"></div>
      </div>
    </div>
  `;

  // ✅ Render results as HTML cards, otherwise keep text safe
  const textEl = messageDiv.querySelector('.message-text');
  const raw = msg.content || '';

  if (!msg.isUser) {
  textEl.innerHTML = raw;
} else {

    const safe = escapeHtml(raw);
    // convert [Label](url) into <a>
    textEl.innerHTML = safe.replace(
      /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a class="smart-link" href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );
  }


  messagesDiv.appendChild(messageDiv);
});


  scrollToBottom();
}

function renderChatList(data) {
  const chatList = document.getElementById('chat-list');

  const chats = data.filter((item) => item.type === 'chat');
  const sortedChats = [...chats].sort((a, b) => b.timestamp - a.timestamp);

  chatList.innerHTML = '';

  sortedChats.forEach((chat) => {
    const chatDiv = document.createElement('div');
    chatDiv.className = `nav-item px-3 py-2.5 rounded-lg text-white/70 text-sm flex items-center gap-3 ${
      chat.id === currentChatId ? 'bg-white/10' : ''
    }`;
    chatDiv.dataset.chatId = chat.id;

    chatDiv.innerHTML = `
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
        </path>
      </svg>

      <span class="truncate flex-1">${escapeHtml(chat.title)}</span>

      <div class="chat-menu" style="position:relative; margin-left:auto;">
        <button class="chat-menu-btn" title="More" aria-label="More" style="
          background:transparent; border:none; color:#9aa0a6; cursor:pointer;
          font-size:18px; line-height:1; padding:4px 6px; border-radius:8px;
        ">⋯</button>

        <div class="chat-menu-popover" style="
          position:absolute; right:0; top:28px;
          background:#0b1220; border:1px solid rgba(255,255,255,0.10);
          border-radius:10px; min-width:140px; padding:6px;
          box-shadow:0 10px 25px rgba(0,0,0,0.35);
          display:none; z-index:50;
        ">
          <button class="chat-menu-item danger" style="
            width:100%; text-align:left; background:transparent; border:none;
            color:#ff6b6b; padding:8px 10px; border-radius:8px;
            cursor:pointer; font-size:13px;
          ">Delete</button>
        </div>
      </div>
    `;

    // Open chat on click (but not when clicking menu)
    chatDiv.addEventListener('click', () => {
      currentChatId = chat.id;
      renderMessages(allData);
      renderChatList(allData);
    });

    // Menu logic
    const menuBtn = chatDiv.querySelector('.chat-menu-btn');
    const popover = chatDiv.querySelector('.chat-menu-popover');
    const delBtn = chatDiv.querySelector('.chat-menu-item.danger');

    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeAllChatMenus();
      popover.style.display = (popover.style.display === 'block') ? 'none' : 'block';
    });

    delBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeAllChatMenus();
      deleteChat(chat.id);
    });

    chatList.appendChild(chatDiv);
  });
}
function closeAllChatMenus() {
  document.querySelectorAll('.chat-menu-popover').forEach((p) => {
    p.style.display = 'none';
  });
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
  const insideMenu = e.target.closest('.chat-menu');
  if (!insideMenu) closeAllChatMenus();
});

// Close menu on ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeAllChatMenus();
});

function deleteChat(chatId) {
  if (!confirm("Delete this chat?")) return;

  // remove the chat record from sidebar source
  allData = allData.filter(item => !(item.type === 'chat' && item.id === chatId));

  // remove messages belonging to this chat
  allData = allData.filter(item => item.chatId !== chatId);

  // if you are using localStorage anywhere, save it here (optional)
  // localStorage.setItem("messages", JSON.stringify(allData));

  // if deleted current chat → start a fresh chat
  if (currentChatId === chatId) {
    currentChatId = 'chat-' + Date.now();
    renderMessages(allData);
    renderChatList(allData);
    return;
  }

  // refresh UI
  renderChatList(allData);
  renderMessages(allData);
}



function showTypingIndicator() {
  const typingDiv = document.createElement('div');
  typingDiv.id = 'typing-indicator';
  typingDiv.className = 'message-assistant message-animate py-8 px-6';
  typingDiv.innerHTML = `
    <div class="flex gap-6">
      <div class="w-8 h-8 rounded-sm bg-gray-700 flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
      </div>
      <div class="flex-1 pt-1">
        <div class="flex gap-1">
          <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
        </div>
      </div>
    </div>
  `;
  messagesDiv.appendChild(typingDiv);
  scrollToBottom();
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) indicator.remove();
}

function getRandomResponse() {
  return aiResponses[Math.floor(Math.random() * aiResponses.length)];
}

chatForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const message = messageInput.value.trim();

  if (!message || isProcessing) return;

  isProcessing = true;
  sendButton.disabled = true;

  // Data SDK is required for persistence. If not available, fall back to in-memory.
  const hasDataSdk = !!window.dataSdk;

  if (allData.length >= 999) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    errorDiv.textContent = 'Maximum limit of 999 items reached. Please start a new chat.';
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
    isProcessing = false;
    sendButton.disabled = !messageInput.value.trim();
    return;
  }

  // Create chat on first message
  const currentChatMessages = allData.filter(
    (item) => item.type === 'message' && item.chatId === currentChatId
  );

  if (currentChatMessages.length === 0) {
    const chatTitle = message.length > 30 ? message.substring(0, 30) + '...' : message;
    const chatRecord = { id: currentChatId, type: 'chat', title: chatTitle, timestamp: Date.now() };

    if (hasDataSdk) {
      const chatResult = await window.dataSdk.create(chatRecord);
      if (!chatResult.isOk) {
        alert('Failed to create chat. Please try again.');
        isProcessing = false;
        sendButton.disabled = !messageInput.value.trim();
        return;
      }
    } else {
      allData.push(chatRecord);
      renderChatList(allData);
    }
  }

  // User message
  const userMsg = {
    id: `user-${Date.now()}`,
    type: 'message',
    content: message,
    isUser: true,
    timestamp: Date.now(),
    chatId: currentChatId
  };

  if (hasDataSdk) {
    const createResult = await window.dataSdk.create(userMsg);
    if (!createResult.isOk) {
      alert('Failed to send message. Please try again.');
      isProcessing = false;
      sendButton.disabled = !messageInput.value.trim();
      return;
    }
  } else {
    allData.push(userMsg);
    renderMessages(allData);
  }

  // Clear input
  messageInput.value = '';
  messageInput.style.height = 'auto';

  showTypingIndicator();

  // Call backend (FastAPI) for real results
  try {
    const parsed = parseQuery(message);

    // ✅ If user typed "profession in city" (old functionality), keep using /search
    if (parsed) {
      const url = `${API_BASE}/search?profession=${encodeURIComponent(parsed.profession)}&location=${encodeURIComponent(parsed.location)}`;
      const res = await fetch(url);
      if (!res.ok) {
        let detail = "";
        try { detail = (await res.json())?.detail || ""; } catch (_) {}
        throw new Error(`API ${res.status}${detail ? `: ${detail}` : ""}`);
      }

      const people = await res.json();

      removeTypingIndicator();
      const aiMsg = {
        id: `ai-${Date.now()}`,
        type: "message",
        content: formatPeopleList(people),
        isUser: false,
        timestamp: Date.now(),
        chatId: currentChatId
      };

      allData.push(aiMsg);
      renderMessages(allData);
      isProcessing = false;
      sendButton.disabled = !messageInput.value.trim();
      return;
    }

    // ✅ NEW functionality: problem → AI description → ask city → results
    const chatRes = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chatId: currentChatId, message })
    });

    if (!chatRes.ok) {
      let detail = "";
      try { detail = (await chatRes.json())?.detail || ""; } catch (_) {}
      throw new Error(`API ${chatRes.status}${detail ? `: ${detail}` : ""}`);
    }

    const chatData = await chatRes.json();

    removeTypingIndicator();

    // First, show the AI reply (description / question / heading)
    allData.push({
      id: `ai-${Date.now()}`,
      type: "message",
      content: chatData.reply || "OK.",
      isUser: false,
      timestamp: Date.now(),
      chatId: currentChatId
    });

    // If results are included, show them using existing formatter
    if (Array.isArray(chatData.results)) {
      allData.push({
        id: `ai-${Date.now()}-results`,
        type: "message",
        content: formatPeopleList(chatData.results),
        isUser: false,
        timestamp: Date.now(),
        chatId: currentChatId
      });
    }

    renderMessages(allData);

    isProcessing = false;
    sendButton.disabled = !messageInput.value.trim();
    return;
  } catch (err) {
    removeTypingIndicator();
    const aiMsg = {
      id: `ai-${Date.now()}`,
      type: "message",
      content: `Failed to call backend. ${err.message}

Make sure backend is running on ${API_BASE}.`,
      isUser: false,
      timestamp: Date.now(),
      chatId: currentChatId
    };
    allData.push(aiMsg);
    renderMessages(allData);
  } finally {
    isProcessing = false;
    sendButton.disabled = !messageInput.value.trim();
  }
});

// New chat
document.getElementById('new-chat-btn').addEventListener('click', () => {
  currentChatId = 'chat-' + Date.now();
  renderMessages(allData);
  renderChatList(allData);
  messageInput.focus();
});

// Data SDK Handler
const dataHandler = {
  onDataChanged(data) {
    allData = data;
    renderMessages(data);
    renderChatList(data);
  }
};

// Initialize Data SDK (if present)
async function initializeApp() {
  if (!window.dataSdk) {
    // No SDK; just render empty UI
    renderMessages(allData);
    renderChatList(allData);
    return;
  }
  const initResult = await window.dataSdk.init(dataHandler);
  if (!initResult.isOk) {
    console.error('Failed to initialize data SDK');
  }
}

initializeApp();

// Element SDK config wiring (if present)
async function onConfigChange(cfg) {
  const baseSize = cfg.font_size || 16;
  const customFont = cfg.font_family || 'Inter';
  const fontStack = `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`;

  document.getElementById('chat-title').textContent = cfg.main_title || defaultConfig.main_title;

  const welcomeText = document.getElementById('welcome-text');
  if (welcomeText) {
    welcomeText.textContent = cfg.welcome_message || defaultConfig.welcome_message;
  }

  document.getElementById('message-input').placeholder =
    cfg.input_placeholder || defaultConfig.input_placeholder;

  // Apply font
  document.body.style.fontFamily = `${customFont}, ${fontStack}`;

  // Apply font sizes
  document.getElementById('chat-title').style.fontSize = `${baseSize * 1.125}px`;
  document.querySelectorAll('.markdown-content').forEach((el) => {
    el.style.fontSize = `${baseSize}px`;
  });
  document.getElementById('message-input').style.fontSize = `${baseSize}px`;
  document.querySelectorAll('.text-sm').forEach((el) => {
    el.style.fontSize = `${baseSize * 0.875}px`;
  });
  document.querySelectorAll('.text-xs').forEach((el) => {
    el.style.fontSize = `${baseSize * 0.75}px`;
  });

  // Apply colors
  document.querySelector('.main-wrapper').style.background = cfg.background_color || defaultConfig.background_color;
  document.querySelector('.chat-area').style.background = cfg.background_color || defaultConfig.background_color;
  document.querySelector('.chat-header').style.background = cfg.background_color || defaultConfig.background_color;

  document.querySelectorAll('.message-user').forEach((el) => {
    el.style.background = cfg.background_color || defaultConfig.background_color;
  });
  document.querySelectorAll('.message-assistant').forEach((el) => {
    el.style.background = cfg.background_color || defaultConfig.background_color;
  });

  document.querySelector('.sidebar').style.background = cfg.sidebar_color || defaultConfig.sidebar_color;

  const sendBtn = document.querySelector('.send-button');
  if (sendBtn) sendBtn.style.background = cfg.accent_color || defaultConfig.accent_color;

  document.querySelectorAll('.markdown-content').forEach((el) => {
    el.style.color = cfg.text_color || defaultConfig.text_color;
  });
  document.getElementById('message-input').style.color = cfg.text_color || defaultConfig.text_color;
}

function mapToCapabilities(cfg) {
  return {
    recolorables: [
      {
        get: () => cfg.background_color || defaultConfig.background_color,
        set: (value) => {
          cfg.background_color = value;
          window.elementSdk.setConfig({ background_color: value });
        }
      },
      {
        get: () => cfg.secondary_surface || defaultConfig.secondary_surface,
        set: (value) => {
          cfg.secondary_surface = value;
          window.elementSdk.setConfig({ secondary_surface: value });
        }
      },
      {
        get: () => cfg.text_color || defaultConfig.text_color,
        set: (value) => {
          cfg.text_color = value;
          window.elementSdk.setConfig({ text_color: value });
        }
      },
      {
        get: () => cfg.accent_color || defaultConfig.accent_color,
        set: (value) => {
          cfg.accent_color = value;
          window.elementSdk.setConfig({ accent_color: value });
        }
      },
      {
        get: () => cfg.sidebar_color || defaultConfig.sidebar_color,
        set: (value) => {
          cfg.sidebar_color = value;
          window.elementSdk.setConfig({ sidebar_color: value });
        }
      }
    ],
    borderables: [],
    fontEditable: {
      get: () => cfg.font_family || 'Inter',
      set: (value) => {
        cfg.font_family = value;
        window.elementSdk.setConfig({ font_family: value });
      }
    },
    fontSizeable: {
      get: () => cfg.font_size || 16,
      set: (value) => {
        cfg.font_size = value;
        window.elementSdk.setConfig({ font_size: value });
      }
    }
  };
}

function mapToEditPanelValues(cfg) {
  return new Map([
    ['main_title', cfg.main_title || defaultConfig.main_title],
    ['welcome_message', cfg.welcome_message || defaultConfig.welcome_message],
    ['input_placeholder', cfg.input_placeholder || defaultConfig.input_placeholder]
  ]);
}

if (window.elementSdk) {
  window.elementSdk.init({
    defaultConfig,
    onConfigChange,
    mapToCapabilities,
    mapToEditPanelValues
  });
}
