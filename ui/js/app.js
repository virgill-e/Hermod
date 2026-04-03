/**
 * PyPost — app.js
 * Logique principale Alpine.js
 */

function pypost() {
  return {
    // ── État global ────────────────────────────────────────────────────────
    tabs: [],
    activeTab: 0,
    sidebarTab: 'collections',
    requestTab: 'Params',
    responseTab: 'Body',

    collections: [],
    environments: [],
    history: [],
    activeEnv: '',

    loading: false,
    response: null,
    error: null,

    // ── Tab courant (computed-like via getter) ─────────────────────────────
    get currentTab() {
      return this.tabs[this.activeTab] || this.defaultTab();
    },

    // ── Init ───────────────────────────────────────────────────────────────
    init() {
      this.newTab();
      this.loadHistory();
      this.loadCollections();
      this.loadEnvironments();

      // Highlight.js auto-apply après chaque réponse
      this.$watch('response', () => {
        this.$nextTick(() => {
          const el = document.getElementById('response-body');
          if (el) { el.removeAttribute('data-highlighted'); hljs.highlightElement(el); }
        });
      });
    },

    // ── Onglets ─────────────────────────────────────────────────────────────
    defaultTab() {
      return {
        id: crypto.randomUUID(),
        name: 'Sans titre',
        method: 'GET',
        url: '',
        params: [],
        headers: [],
        bodyType: 'none',
        body: '',
        authType: 'none',
        authToken: '',
        authUser: '',
        authPass: '',
        dirty: false,
      };
    },

    newTab() {
      const tab = this.defaultTab();
      this.tabs.push(tab);
      this.activeTab = this.tabs.length - 1;
      this.response = null;
      this.error = null;
    },

    closeTab(i) {
      if (this.tabs.length === 1) { this.tabs[0] = this.defaultTab(); return; }
      this.tabs.splice(i, 1);
      this.activeTab = Math.min(this.activeTab, this.tabs.length - 1);
    },

    openRequest(req) {
      const tab = {
        ...this.defaultTab(),
        name: req.name,
        method: req.method,
        url: req.url,
        headers: req.headers || [],
        params: req.params || [],
        body: req.body?.raw || '',
        bodyType: req.body?.type || 'none',
        authType: req.auth?.type || 'none',
        authToken: req.auth?.token || '',
      };
      this.tabs.push(tab);
      this.activeTab = this.tabs.length - 1;
    },

    loadFromHistory(entry) {
      const tab = { ...this.defaultTab(), method: entry.method, url: entry.url, name: entry.url };
      this.tabs.push(tab);
      this.activeTab = this.tabs.length - 1;
      this.response = null;
      this.error = null;
    },

    // ── Requête HTTP ────────────────────────────────────────────────────────
    async sendRequest() {
      const tab = this.currentTab;
      if (!tab.url) return;

      this.loading = true;
      this.response = null;
      this.error = null;

      try {
        const payload = {
          method: tab.method,
          url: tab.url,
          headers: (tab.headers || []).filter(h => h.enabled && h.key),
          params:  (tab.params  || []).filter(p => p.enabled && p.key),
          body:    tab.bodyType !== 'none' ? tab.body : null,
          body_type: tab.bodyType,
          auth: { type: tab.authType, token: tab.authToken, username: tab.authUser, password: tab.authPass },
        };

        const res = await fetch('/api/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (!res.ok || data.error) {
          this.error = data.error || `Erreur HTTP ${res.status}`;
        } else {
          this.response = data;
          this.responseTab = 'Body';
          this.addToHistory({ method: tab.method, url: tab.url, status: data.status_code });
        }
      } catch (err) {
        this.error = err.message || 'Erreur réseau inconnue';
      } finally {
        this.loading = false;
      }
    },

    // ── Historique ──────────────────────────────────────────────────────────
    addToHistory(entry) {
      this.history.unshift({ ...entry, id: crypto.randomUUID(), ts: new Date().toISOString() });
      if (this.history.length > 200) this.history.pop();
      localStorage.setItem('pypost_history', JSON.stringify(this.history));
    },

    loadHistory() {
      try { this.history = JSON.parse(localStorage.getItem('pypost_history') || '[]'); } catch { this.history = []; }
    },

    // ── Collections & Environnements (stubs — chargés depuis l'API plus tard) ──
    async loadCollections() {
      try {
        const res = await fetch('/api/collections');
        if (res.ok) this.collections = await res.json();
      } catch { /* API pas encore dispo */ }
    },

    async loadEnvironments() {
      try {
        const res = await fetch('/api/environments');
        if (res.ok) this.environments = await res.json();
      } catch { /* API pas encore dispo */ }
    },

    // ── Utilitaires ─────────────────────────────────────────────────────────
    prettyBody(body) {
      if (!body) return '';
      try { return JSON.stringify(JSON.parse(body), null, 2); } catch { return body; }
    },

    formatBytes(bytes) {
      if (!bytes) return '0 B';
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    },

    async copyBody() {
      if (this.response?.body) {
        await navigator.clipboard.writeText(this.prettyBody(this.response.body));
      }
    },

    // ── Resize sidebar ──────────────────────────────────────────────────────
    startResize(e) {
      const sidebar = document.getElementById('sidebar');
      const handle  = document.getElementById('resize-handle');
      const startX  = e.clientX;
      const startW  = sidebar.offsetWidth;

      handle.classList.add('dragging');

      const onMove = (ev) => {
        const newW = Math.min(400, Math.max(160, startW + ev.clientX - startX));
        sidebar.style.width = newW + 'px';
      };
      const onUp = () => {
        handle.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      };

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    },
  };
}
