# VEIL Browser

<div align="center">
  <img src="resources/assets/logo.png" alt="VEIL Logo" width="200" height="200" />
  <h3>A Fast, Privacy-Focused, and Highly Customizable Python Desktop Browser</h3>
</div>

## Overview

**VEIL** is a modern, modular desktop web browser built entirely in Python using **PySide6** and **Qt WebEngine**. Designed with privacy, customization, and user control at its core, VEIL provides a sleek, futuristic UI backed by powerful engine-level controls.

It features persistent local SQLite storage, comprehensive tracker blocking, multi-profile support, and an advanced security architecture—all without relying on heavy telemetry or external sync services.

---

## Key Features

### 🛡️ Privacy & Security
- **Tracker & Ad Blocking:** Integrated filtering engine using standard EasyList syntax to block analytics and intrusive ads at the network request level.
- **Cookie Control:** Granular control over cookies, allowing strict session-only modes or custom persistence.
- **Site Permissions Manager:** Intercepts and controls dangerous API requests (Geolocation, Media, Notifications) via native UI infobars.
- **Security Indicators:** Real-time SSL/TLS validation with native UI warnings for unencrypted (`HTTP`) or invalid certificates.
- **Private Browsing (Incognito):** Isolated `QWebEngineProfile` support that leaves no trace on disk.

### 🌐 Core Browsing Experience
- **Multi-Tab Architecture:** Smooth tab management with loading indicators, title syncing, and robust navigation controls.
- **Multi-Profile Support:** Keep work, personal, and private browsing states entirely isolated.
- **Native Download Manager:** Full `QWebEngineDownloadRequest` integration to intercept, pause, resume, and track local file downloads.
- **Bookmark & History Management:** Fast, SQLite-backed persistent storage for all your navigation data.

### 🎨 Design & Customization
- **Futuristic Interface:** A stunning, abstract "New Tab" page featuring a glowing cyber-aesthetic, dynamic theme toggling, and integrated search.
- **Persistent Theming:** Seamless Dark, Light, and System theme integration across both the browser UI and internal web pages via `QWebEngineSettings`.
- **Customizable Search Engines:** Easily switch between DuckDuckGo (default), Google, Bing, or custom URLs via the Settings pane.

---

## Installation

VEIL requires Python 3.8+ and uses `uv` for dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aryankpandey/veil-browser.git
   cd veil-browser
   ```

2. **Install dependencies:**
   Due to specific environment constraints, PySide6 should be installed system-wide via `uv`:
   ```bash
   uv pip install --system PySide6
   ```

3. **Run the browser:**
   ```bash
   python main.py
   ```

---

## Architecture Overview

The project is structured modularly for easy extension and debugging:

```text
VEIL/
├── browser/          # Core Qt WebEngine wrappers (Tabs, Profile logic)
├── storage/          # SQLite database managers (History, Bookmarks, Settings)
├── privacy/          # Tracker blocker and cookie jar interceptors
├── ui/               # Custom PyQt widgets (Toolbar, Settings window, Infobars)
├── resources/        # HTML assets (New Tab page), Icons, and Stylesheets
├── test_site/        # Local HTTP server files for testing browser features
└── main.py           # Application entry point
```

---

## Testing

VEIL includes a built-in local test suite to verify features (Downloads, Permissions, Security UI).

1. Start the local test server:
   ```bash
   python -m http.server 8000
   ```
2. Open VEIL and navigate to `http://localhost:8000/`.

---

## Developer

**Developed by Aryan Kumar Pandey**

* 🐙 **GitHub:** [github.com/aryankpandey](https://github.com/aryankpandey)
* 💼 **LinkedIn:** [linkedin.com/in/aryankpandey](https://linkedin.com/in/aryankpandey)
* 📸 **Instagram:** [@aryanpandeyyy](https://instagram.com/aryanpandeyyy)
* 🌐 **Portfolio:** [aryankpandey.lovable.app](https://aryankpandey.lovable.app)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
