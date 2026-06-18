/**
 * AccessEase 2.0 — Main JavaScript
 * Accessibility + UI functionality
 */

"use strict";

// ══════════════════════════════════════════════════════════
// ACCESSIBILITY MANAGER
// ══════════════════════════════════════════════════════════
const AE = {
  fontSize: parseInt(localStorage.getItem("ae_font_size") || "16"),
  darkMode: localStorage.getItem("ae_dark") === "1",
  highContrast: localStorage.getItem("ae_contrast") === "1",
  ttsEnabled: false,

  init() {
    document.documentElement.style.setProperty("--font-size-base", this.fontSize + "px");
    document.body.style.fontSize = this.fontSize + "px";
    if (this.darkMode)     document.documentElement.setAttribute("data-theme", "dark");
    if (this.highContrast) document.documentElement.setAttribute("data-contrast", "high");
    this._syncBtns();
  },

  // ── Font size ──────────────────────────────────────────
  setFont(action) {
    if (action === "increase") this.fontSize = Math.min(this.fontSize + 2, 26);
    if (action === "decrease") this.fontSize = Math.max(this.fontSize - 2, 12);
    if (action === "reset")    this.fontSize = 16;
    document.body.style.fontSize = this.fontSize + "px";
    localStorage.setItem("ae_font_size", this.fontSize);
  },

  // ── Dark mode ──────────────────────────────────────────
  toggleDark() {
    this.darkMode = !this.darkMode;
    document.documentElement.setAttribute("data-theme", this.darkMode ? "dark" : "");
    localStorage.setItem("ae_dark", this.darkMode ? "1" : "0");
    this._syncBtns();
  },

  // ── High contrast ──────────────────────────────────────
  toggleContrast() {
    this.highContrast = !this.highContrast;
    document.documentElement.setAttribute("data-contrast", this.highContrast ? "high" : "");
    localStorage.setItem("ae_contrast", this.highContrast ? "1" : "0");
    this._syncBtns();
  },

  // ── Text-to-speech ────────────────────────────────────
  speak(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text || document.body.innerText);
    utt.lang = "en-US";
    utt.rate = 1;
    window.speechSynthesis.speak(utt);
  },

  stopSpeak() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  },

// ── Voice commands ────────────────────────────────────
startVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SR) {
    AE_Toast.show(
      "Voice recognition is not supported. Use Google Chrome or Edge.",
      "warning"
    );
    return;
  }

  try {
    const rec = new SR();

    rec.lang = "en-US";
    rec.continuous = false;
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    AE_Toast.show("🎤 Listening... Speak now", "info");

    rec.onstart = () => {
      console.log("Voice recognition started");
    };

    rec.onresult = (e) => {
      const cmd = e.results[0][0].transcript.toLowerCase().trim();

      console.log("Voice Command:", cmd);

      AE_Toast.show(`Command: "${cmd}"`, "success");

      this._handleVoiceCmd(cmd);
    };

    rec.onerror = (event) => {
      console.error("Voice Error:", event.error);

      let msg = "Voice recognition failed";

      switch (event.error) {
        case "not-allowed":
          msg = "Microphone permission denied";
          break;
        case "audio-capture":
          msg = "No microphone found";
          break;
        case "network":
          msg = "Network error";
          break;
        case "no-speech":
          msg = "No speech detected";
          break;
        case "aborted":
          msg = "Voice recognition stopped";
          break;
        default:
          msg = `Voice Error: ${event.error}`;
      }

      AE_Toast.show(msg, "danger");
    };

    rec.onend = () => {
      console.log("Voice recognition ended");
    };

    rec.start();

  } catch (err) {
    console.error(err);
    AE_Toast.show("Could not start voice recognition.", "danger");
  }
},

  _handleVoiceCmd(cmd) {
    const go = (url) => { window.location.href = url; };
    if (cmd.includes("home"))           go("/");
    else if (cmd.includes("cart"))      go("/cart");
    else if (cmd.includes("orders"))    go("/orders");
    else if (cmd.includes("login"))     go("/login");
    else if (cmd.includes("signup"))    go("/signup");
    else if (cmd.includes("mobile"))    go("/mobile");
    else if (cmd.includes("laptop"))    go("/laptop");
    else if (cmd.includes("watch"))     go("/watch");
    else if (cmd.includes("earbud"))    go("/earbuds");
    else if (cmd.includes("speaker"))   go("/speaker");
    else if (cmd.includes("search")) {
      const inp = document.querySelector(".navbar-search input");
      if (inp) { inp.focus(); AE_Toast.show("Search bar focused.", "info"); }
    }
    else if (cmd.includes("dark mode"))     this.toggleDark();
    else if (cmd.includes("contrast"))      this.toggleContrast();
    else if (cmd.includes("increase font")) this.setFont("increase");
    else if (cmd.includes("decrease font")) this.setFont("decrease");
    else if (cmd.includes("read page"))     this.speak();
    else if (cmd.includes("stop"))          this.stopSpeak();
    else if (cmd.includes("scroll down"))   window.scrollBy({ top: window.innerHeight, behavior: "smooth" });
    else if (cmd.includes("scroll up"))     window.scrollBy({ top: -window.innerHeight, behavior: "smooth" });
    else AE_Toast.show(`Unknown command: "${cmd}"`, "warning");
  },

  _syncBtns() {
    const d = document.getElementById("btn-dark-mode");
    const c = document.getElementById("btn-contrast");
    if (d) d.classList.toggle("active", this.darkMode);
    if (c) c.classList.toggle("active", this.highContrast);
  },

  // ── Keyboard shortcuts ─────────────────────────────────
  initKeyboard() {
    document.addEventListener("keydown", (e) => {
      if (!e.altKey) return;
      switch (e.key) {
        case "h": e.preventDefault(); window.location.href = "/"; break;
        case "c": e.preventDefault(); window.location.href = "/cart"; break;
        case "s": e.preventDefault(); window.location.href = "/login"; break;
        case "i": e.preventDefault();
          const inp = document.querySelector(".navbar-search input");
          if (inp) inp.focus(); break;
        case "+": e.preventDefault(); AE.setFont("increase"); break;
        case "-": e.preventDefault(); AE.setFont("decrease"); break;
        case "0": e.preventDefault(); AE.setFont("reset"); break;
        case "d": e.preventDefault(); AE.toggleDark(); break;
        case "k": e.preventDefault(); AE.toggleContrast(); break;
        case "r": e.preventDefault(); AE.speak(); break;
        case "x": e.preventDefault(); AE.stopSpeak(); break;
        case "z": e.preventDefault(); AE.startVoice(); break;
        case "?": e.preventDefault(); AE._showShortcutsHelp(); break;
      }
    });
  },

  _showShortcutsHelp() {
    alert(
      "⌨️ Keyboard Shortcuts (Alt + key)\n\n" +
      "H  — Home\n" +
      "C  — Cart\n" +
      "S  — Login/Signup\n" +
      "I  — Focus search\n" +
      "+  — Increase font\n" +
      "-  — Decrease font\n" +
      "0  — Reset font\n" +
      "D  — Toggle dark mode\n" +
      "K  — Toggle high contrast\n" +
      "R  — Read page aloud\n" +
      "X  — Stop reading\n" +
      "Z  — Start voice commands\n" +
      "?  — Show this help"
    );
  }
};


// ══════════════════════════════════════════════════════════
// TOOLBAR TOGGLE
// ══════════════════════════════════════════════════════════
function initToolbar() {
  const toggle = document.getElementById("ae-toolbar-toggle");
  const panel  = document.getElementById("ae-toolbar-panel");
  if (!toggle || !panel) return;
  toggle.addEventListener("click", () => {
    panel.classList.toggle("open");
    toggle.setAttribute("aria-expanded", panel.classList.contains("open"));
  });
}


// ══════════════════════════════════════════════════════════
// TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════
const AE_Toast = {
  show(msg, type = "info", duration = 3500) {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }
    const icons = { success: "fa-check-circle", danger: "fa-times-circle",
                    info: "fa-info-circle", warning: "fa-exclamation-triangle" };
    const toast = document.createElement("div");
    toast.className = `ae-toast ${type}`;
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}" style="color:var(--${type === 'danger' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'})"></i> ${msg}`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = "slideInRight 0.3s ease reverse";
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
};

// Flash messages from server → toast
function showFlashToasts() {
  document.querySelectorAll(".server-flash").forEach(el => {
    AE_Toast.show(el.dataset.msg, el.dataset.type || "info");
  });
}


// ══════════════════════════════════════════════════════════
// SEARCH SUGGESTIONS
// ══════════════════════════════════════════════════════════
function initSearch() {
  const input = document.getElementById("main-search");
  const box   = document.getElementById("search-suggestions");
  if (!input || !box) return;

  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) { box.classList.remove("show"); return; }
    timer = setTimeout(() => fetchSuggestions(q, box), 280);
  });

  document.addEventListener("click", (e) => {
    if (!input.contains(e.target) && !box.contains(e.target)) {
      box.classList.remove("show");
    }
  });
}

async function fetchSuggestions(q, box) {
  try {
    const res  = await fetch(`/search-api/suggestions?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    if (!data.length) { box.classList.remove("show"); return; }
    box.innerHTML = data.map(p => `
      <a class="suggestion-item" href="/product/${p.id}">
        <img src="${p.image_url || 'https://via.placeholder.com/38'}" alt="${p.name}" loading="lazy">
        <div>
          <div class="sug-name">${p.name}</div>
          <div class="sug-price">₹${Number(p.price).toLocaleString("en-IN")}</div>
        </div>
      </a>`).join("");
    box.classList.add("show");
  } catch {}
}


// ══════════════════════════════════════════════════════════
// CART — QUANTITY CONTROLS
// ══════════════════════════════════════════════════════════
function initQtyControls() {
  document.querySelectorAll(".qty-minus").forEach(btn => {
    btn.addEventListener("click", () => {
      const inp = btn.closest(".qty-control").querySelector("input");
      const v = Math.max(1, parseInt(inp.value) - 1);
      inp.value = v;
      inp.dispatchEvent(new Event("change"));
    });
  });
  document.querySelectorAll(".qty-plus").forEach(btn => {
    btn.addEventListener("click", () => {
      const inp = btn.closest(".qty-control").querySelector("input");
      const max = parseInt(inp.max) || 99;
      const v = Math.min(max, parseInt(inp.value) + 1);
      inp.value = v;
      inp.dispatchEvent(new Event("change"));
    });
  });
}


// ══════════════════════════════════════════════════════════
// WISHLIST TOGGLE (AJAX)
// ══════════════════════════════════════════════════════════
function initWishlist() {
  document.querySelectorAll(".wishlist-toggle").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const pid = btn.dataset.pid;
      if (!pid) return;
      try {
        const res  = await fetch(`/wishlist/toggle/${pid}`, { method: "POST", headers: { "X-Requested-With": "XMLHttpRequest" } });
        const data = await res.json();
        btn.classList.toggle("active", data.in_wishlist);
        btn.querySelector("i").className = data.in_wishlist ? "fas fa-heart" : "far fa-heart";
        AE_Toast.show(data.message, data.in_wishlist ? "success" : "info");
      } catch { AE_Toast.show("Please login to use wishlist.", "warning"); }
    });
  });
}


// ══════════════════════════════════════════════════════════
// STAR RATING (REVIEW FORM)
// ══════════════════════════════════════════════════════════
function initStarRating() {
  document.querySelectorAll(".star-rating").forEach(wrap => {
    const stars = wrap.querySelectorAll("button");
    const input = wrap.querySelector("input[type='hidden']");
    stars.forEach((star, idx) => {
      star.addEventListener("click", () => {
        input.value = idx + 1;
        stars.forEach((s, i) => {
          s.classList.toggle("active", i <= idx);
          s.querySelector("i").className = i <= idx ? "fas fa-star" : "far fa-star";
        });
      });
      star.addEventListener("mouseenter", () => {
        stars.forEach((s, i) => {
          s.querySelector("i").className = i <= idx ? "fas fa-star" : "far fa-star";
        });
      });
      star.addEventListener("mouseleave", () => {
        const val = parseInt(input.value) || 0;
        stars.forEach((s, i) => {
          s.querySelector("i").className = i < val ? "fas fa-star" : "far fa-star";
        });
      });
    });
  });
}


// ══════════════════════════════════════════════════════════
// CHATBOT
// ══════════════════════════════════════════════════════════
const Chatbot = {
  faq: [
    { q: ["hello", "hi", "hey"], a: "Hello! 👋 Welcome to AccessEase. How can I help you today?" },
    { q: ["track", "order status", "where is my order"], a: "You can track your order from <a href='/orders'>My Orders</a> page. Each order has a live tracking timeline." },
    { q: ["return", "refund"], a: "We offer 7-day easy returns. Contact support@accessease.com for return requests." },
    { q: ["payment", "pay"], a: "We accept Cash on Delivery (COD), UPI, Credit/Debit cards, and Net Banking." },
    { q: ["delivery", "shipping"], a: "Free shipping on orders above ₹500. Standard delivery takes 3–7 business days." },
    { q: ["warranty"], a: "All electronics come with manufacturer warranty (1–2 years). Check product details for specifics." },
    { q: ["laptop", "best laptop"], a: "Check our <a href='/products?category=laptops'>Laptops</a> section for top picks from Lenovo, HP, ASUS, and Acer." },
    { q: ["mobile", "phone", "smartphone"], a: "Browse the latest smartphones in our <a href='/products?category=mobiles'>Mobiles</a> section." },
    { q: ["earbuds", "headphones", "earphones"], a: "True wireless earbuds from Sony, boAt, OnePlus and more — see <a href='/products?category=earbuds'>Earbuds</a>." },
    { q: ["speaker", "bluetooth speaker"], a: "Portable Bluetooth speakers from JBL, Sony, boAt — visit <a href='/products?category=speakers'>Speakers</a>." },
    { q: ["accessibility", "disability"], a: "AccessEase is built for everyone! Use the ♿ toolbar (bottom right) for dark mode, text resize, voice commands, screen reader, and high contrast." },
    { q: ["contact", "support", "help"], a: "Reach us at support@accessease.com or call 1800-123-4567 (Mon–Sat, 9am–6pm)." },
    { q: ["cancel"], a: "To cancel an order, go to <a href='/orders'>My Orders</a> and select the order. Cancellation is available before it is shipped." },
  ],

  respond(msg) {
    const lower = msg.toLowerCase();
    for (const item of this.faq) {
      if (item.q.some(k => lower.includes(k))) return item.a;
    }
    return `I'm not sure about that. Try asking about tracking orders, returns, payment, or browse <a href='/products'>products</a>. Or email support@accessease.com.`;
  },

  addMsg(text, role) {
    const msgs = document.getElementById("chatbot-messages");
    if (!msgs) return;
    const div = document.createElement("div");
    div.className = `chat-msg ${role}`;
    div.innerHTML = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }
};

function initChatbot() {
  const btn    = document.getElementById("chatbot-btn");
  const win    = document.getElementById("chatbot-window");
  const close  = document.getElementById("chatbot-close");
  const input  = document.getElementById("chatbot-text");
  const send   = document.getElementById("chatbot-send");
  if (!btn || !win) return;

  let opened = false;
  btn.addEventListener("click", () => {
    win.classList.toggle("open");
    if (!opened) {
      Chatbot.addMsg("Hi! 👋 I'm AccessBot. How can I help you today?", "bot");
      Chatbot.addMsg("Try: <em>track order</em>, <em>return policy</em>, <em>best laptop</em>", "bot");
      opened = true;
    }
  });
  if (close) close.addEventListener("click", () => win.classList.remove("open"));

  const sendMsg = () => {
    const txt = (input.value || "").trim();
    if (!txt) return;
    Chatbot.addMsg(txt, "user");
    input.value = "";
    setTimeout(() => Chatbot.addMsg(Chatbot.respond(txt), "bot"), 600);
  };

  if (send) send.addEventListener("click", sendMsg);
  if (input) input.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMsg(); });
}


// ══════════════════════════════════════════════════════════
// IMAGE ZOOM (product detail)
// ══════════════════════════════════════════════════════════
function initImageGallery() {
  const mainImg = document.getElementById("product-main-img");
  document.querySelectorAll(".product-thumb").forEach(thumb => {
    thumb.addEventListener("click", () => {
      if (mainImg) mainImg.src = thumb.dataset.src;
      document.querySelectorAll(".product-thumb").forEach(t => t.classList.remove("active"));
      thumb.classList.add("active");
    });
  });
}


// ══════════════════════════════════════════════════════════
// ADMIN SIDEBAR TOGGLE (mobile)
// ══════════════════════════════════════════════════════════
function initAdminSidebar() {
  const toggle = document.getElementById("admin-sidebar-toggle");
  const sidebar = document.querySelector(".admin-sidebar");
  if (!toggle || !sidebar) return;
  toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
}


// ══════════════════════════════════════════════════════════
// PRICE RANGE (filter page)
// ══════════════════════════════════════════════════════════
function initPriceRange() {
  const range = document.getElementById("price-range-slider");
  const disp  = document.getElementById("price-range-display");
  const inp   = document.getElementById("max-price-input");
  if (!range) return;
  range.addEventListener("input", () => {
    if (disp) disp.textContent = `₹0 – ₹${Number(range.value).toLocaleString("en-IN")}`;
    if (inp)  inp.value = range.value;
  });
}


// ══════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════
function fmt(n) {
  return "₹" + Number(n).toLocaleString("en-IN");
}

function discount(orig, curr) {
  if (!orig || orig <= curr) return 0;
  return Math.round(((orig - curr) / orig) * 100);
}


// ══════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  AE.init();
  AE.initKeyboard();
  initToolbar();
  initSearch();
  initQtyControls();
  initWishlist();
  initStarRating();
  initChatbot();
  initImageGallery();
  initAdminSidebar();
  initPriceRange();
  showFlashToasts();
});


