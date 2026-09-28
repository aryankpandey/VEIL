from PySide6.QtWidgets import QMainWindow, QMenu, QInputDialog, QApplication
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
import os
from browser.browser_tab import BrowserTab
from ui.toolbar import BrowserToolBar
from ui.tab_bar import BrowserTabBar
from ui.history_window import HistoryWindow
from storage.history import HistoryManager
from ui.bookmark_sidebar import BookmarkSidebar
from storage.bookmarks import BookmarkManager
from storage.profiles import ProfileManager
from ui.privacy_center import PrivacyCenter
from privacy.tracker_blocker import TrackerBlocker
from ui.download_window import DownloadWindow
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEnginePage
from storage.permissions import PermissionManager
from ui.permission_bar import PermissionInfoBar
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from storage.settings import SettingsManager
from ui.settings_window import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self, profile_id="default", is_private=False):
        super().__init__()
        self.setWindowTitle("VEIL")
        self.resize(1024, 768)

        self.history_window = None
        self.privacy_center = None
        self.download_window = None
        self.history_manager = HistoryManager()
        self.bookmark_manager = BookmarkManager()
        self.profile_manager = ProfileManager()
        self.permission_manager = PermissionManager()
        self.settings_manager = SettingsManager()
        self.is_private_session = is_private
        
        if self.is_private_session:
            self.current_profile_id = "private"
            self.web_profile = QWebEngineProfile(self) # Off-the-record profile
        else:
            self.current_profile_id = profile_id
            data_path = self.profile_manager.get_profile_data_path(self.current_profile_id)
            self.web_profile = QWebEngineProfile(self.current_profile_id, self)
            self.web_profile.setPersistentStoragePath(os.path.join(data_path, "storage"))
            self.web_profile.setCachePath(os.path.join(data_path, "cache"))

        self.tracker_blocker = TrackerBlocker(self)
        self.web_profile.setUrlRequestInterceptor(self.tracker_blocker)
        self.tracker_blocker.request_blocked.connect(self.on_request_blocked)

        self.known_cookies = set()
        self.cookie_store = self.web_profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.on_cookie_added)
        
        self.web_profile.downloadRequested.connect(self.on_download_requested)

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        
        self.infobar_area = QVBoxLayout()
        self.central_layout.addLayout(self.infobar_area)

        self.tabs = BrowserTabBar(self)
        self.central_layout.addWidget(self.tabs)
        self.setCentralWidget(self.central_widget)

        self.bookmark_sidebar = BookmarkSidebar(self.current_profile_id, self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.bookmark_sidebar)
        self.bookmark_sidebar.open_url_requested.connect(self.navigate_to_url)
        self.bookmark_sidebar.hide()

        self.toolbar = BrowserToolBar(self)
        self.addToolBar(self.toolbar)
        self.populate_profile_menu()
        self.toolbar.privacy_btn.clicked.connect(self.show_privacy_center)
        self.toolbar.download_btn.clicked.connect(self.show_downloads)
        self.toolbar.settings_btn.clicked.connect(self.show_settings)

        self.toolbar.url_changed.connect(self.navigate_to_url)
        self.toolbar.back_requested.connect(self.navigate_back)
        self.toolbar.forward_requested.connect(self.navigate_forward)
        self.toolbar.reload_requested.connect(self.reload_page)
        self.toolbar.stop_requested.connect(self.stop_loading)
        self.toolbar.home_requested.connect(self.navigate_home)

        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setup_shortcuts()
        
        self.apply_theme()
        
        startup_behavior = self.settings_manager.get_setting(self.current_profile_id, "startup_behavior", "Open New Tab Page")
        if startup_behavior == "Restore Previous Session":
            self.restore_last_session()
        else:
            self.add_new_tab()

    def show_settings(self):
        settings_dialog = SettingsWindow(self.current_profile_id, self)
        if settings_dialog.exec():
            self.apply_theme()

    def apply_theme(self):
        theme_setting = self.settings_manager.get_setting(self.current_profile_id, "theme", "System")
        
        is_dark = False
        if theme_setting == "Dark":
            is_dark = True
        elif theme_setting == "System":
            app = QApplication.instance()
            if hasattr(app.styleHints(), 'colorScheme'):
                is_dark = app.styleHints().colorScheme() == Qt.ColorScheme.Dark

        if is_dark:
            self.setStyleSheet('''
                QMainWindow, QDialog, QDockWidget, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QToolBar {
                    background: #202020;
                    border: none;
                    border-bottom: 1px solid #444;
                }
                QLineEdit {
                    background: #333333;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTabBar::tab {
                    background: #1a1a1a;
                    color: #aaa;
                    padding: 8px 15px;
                    border: 1px solid #333;
                    border-bottom: none;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background: #2b2b2b;
                    color: white;
                    border-top: 2px solid #7b5ab0;
                }
                QScrollArea, QTableWidget {
                    background-color: #222;
                    color: white;
                    border: 1px solid #444;
                }
                QHeaderView::section {
                    background-color: #333;
                    color: white;
                    border: 1px solid #444;
                }
            ''')
            self.web_profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, True)
        else:
            self.setStyleSheet("")
            self.web_profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, False)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            if self.is_private_session:
                new_tab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'private_new_tab.html'))
            else:
                new_tab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'new_tab.html'))
            qurl = QUrl.fromLocalFile(new_tab_path)
            label = "New Tab"
        
        browser_tab = BrowserTab(self.web_profile, self)
        browser_tab.permission_requested.connect(self.handle_permission_request)
        browser_tab.setUrl(qurl)
        
        index = self.tabs.addTab(browser_tab, label)
        self.tabs.setCurrentIndex(index)
        
        browser_tab.titleChanged.connect(lambda title, browser=browser_tab: self.update_tab_title(browser, title))
        browser_tab.iconChanged.connect(lambda icon, browser=browser_tab: self.update_tab_icon(browser, icon))
        browser_tab.urlChanged.connect(lambda url, browser=browser_tab: self.update_tab_url(browser, url))
        browser_tab.loadStarted.connect(lambda browser=browser_tab: self.update_loading_state(browser, True))
        browser_tab.loadFinished.connect(lambda ok, browser=browser_tab: self.on_page_load_finished(browser, ok))
        
        return browser_tab

    def current_tab_changed(self, index):
        current_browser = self.tabs.widget(index)
        if current_browser:
            url_string = current_browser.url().toString()
            if url_string.startswith("file://") and ("new_tab.html" in url_string or "private_new_tab.html" in url_string):
                self.toolbar.update_url("")
            else:
                self.toolbar.update_url(url_string)
            prefix = "🕵️ " if self.is_private_session else ""
            self.setWindowTitle(f"{prefix}{current_browser.title()} - VEIL")

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title)
            if self.tabs.currentIndex() == index:
                prefix = "🕵️ " if self.is_private_session else ""
                self.setWindowTitle(f"{prefix}{title} - VEIL")

    def update_tab_icon(self, browser, icon):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def update_tab_url(self, browser, qurl):
        index = self.tabs.indexOf(browser)
        if index != -1 and self.tabs.currentIndex() == index:
            url_string = qurl.toString()
            if url_string.startswith("file://") and ("new_tab.html" in url_string or "private_new_tab.html" in url_string):
                self.toolbar.update_url("")
            else:
                self.toolbar.update_url(url_string)

    def update_loading_state(self, browser, is_loading):
        pass

    def on_page_load_finished(self, browser, ok):
        self.update_loading_state(browser, False)
        if ok:
            url = browser.url().toString()
            title = browser.title()
            if url:
                self.history_manager.add_entry(url, title, self.current_profile_id, self.is_private_session)

    def navigate_to_url(self, url_string):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            if not url_string.startswith("http://") and not url_string.startswith("https://"):
                if "." in url_string and " " not in url_string:
                    url_string = "https://" + url_string
                else:
                    search_engine = self.settings_manager.get_setting(self.current_profile_id, "search_engine", "DuckDuckGo")
                    search_urls = {
                        "DuckDuckGo": "https://duckduckgo.com/?q=",
                        "Google": "https://www.google.com/search?q=",
                        "Bing": "https://www.bing.com/search?q="
                    }
                    search_url = search_urls.get(search_engine, "https://duckduckgo.com/?q=")
                    url_string = f"{search_url}{url_string.replace(' ', '+')}"
            current_browser.setUrl(QUrl(url_string))

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def stop_loading(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.stop()

    def navigate_home(self):
        self.add_new_tab()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+Shift+T"), self).activated.connect(self.reopen_closed_tab)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.focus_address_bar)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.reload_page)
        QShortcut(QKeySequence("Alt+Left"), self).activated.connect(self.navigate_back)
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(self.navigate_forward)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.bookmark_page)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.show_history)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self).activated.connect(self.new_private_window)

    def close_current_tab(self):
        index = self.tabs.currentIndex()
        if index != -1:
            self.tabs.close_tab(index)

    def restore_last_session(self):
        # TODO: Implement restore session abstraction (Phase 6/8)
        pass

    def reopen_closed_tab(self):
        # TODO: Implement reopen closed tab abstraction
        pass

    def focus_address_bar(self):
        self.toolbar.url_bar.setFocus()
        self.toolbar.url_bar.selectAll()

    def bookmark_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            
            if not url or (url.startswith("file://") and ("new_tab.html" in url or "private_new_tab.html" in url)):
                # If triggered from veil://bookmarks or empty page, just toggle sidebar
                self.bookmark_sidebar.setVisible(not self.bookmark_sidebar.isVisible())
                return
                
            self.bookmark_manager.add_bookmark(title, url, profile_id=self.current_profile_id)
            self.bookmark_sidebar.refresh_bookmarks()
            self.bookmark_sidebar.show()

    def show_history(self):
        if self.history_window is None:
            self.history_window = HistoryWindow(self.current_profile_id)
        self.history_window.load_history()
        self.history_window.show()
        self.history_window.raise_()

    def update_privacy_stats(self):
        if self.privacy_center and self.privacy_center.isVisible():
            self.privacy_center.update_tracker_count(self.tracker_blocker.blocked_count)
            self.privacy_center.update_cookie_count(len(self.known_cookies))
            
            permissions = self.permission_manager.get_all_permissions(self.current_profile_id)
            granted = len([p for p in permissions if p[2] == "allowed"])
            denied = len([p for p in permissions if p[2] == "blocked"])
            self.privacy_center.update_permission_counts(granted, denied)

    def show_privacy_center(self):
        if self.privacy_center is None:
            self.privacy_center = PrivacyCenter(self.web_profile, self.is_private_session, self.tracker_blocker.blocked_count, len(self.known_cookies), self)
        self.update_privacy_stats()
        self.privacy_center.show()
        self.privacy_center.raise_()

    def show_downloads(self):
        if self.download_window is None:
            self.download_window = DownloadWindow(self.current_profile_id)
        self.download_window.show()
        self.download_window.raise_()

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        download_behavior = self.settings_manager.get_setting(self.current_profile_id, "download_behavior", "Use Default Path")
        if download_behavior == "Ask where to save each file":
            suggested_path = os.path.join(download.downloadDirectory(), download.downloadFileName())
            path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested_path)
            if not path:
                download.cancel()
                return
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            
        download.accept()
        
        if self.download_window is None:
            self.download_window = DownloadWindow(self.current_profile_id)
            
        self.download_window.add_active_download(download)
        
        if not self.is_private_session:
            from storage.downloads import DownloadManager
            dm = DownloadManager()
            dm.add_download(
                self.current_profile_id,
                download.url().toString(),
                download.downloadFileName(),
                download.downloadDirectory() + "/" + download.downloadFileName(),
                download.totalBytes()
            )

    def handle_permission_request(self, page, origin, feature):
        feature_name = str(feature).split('.')[-1]
        
        status = self.permission_manager.get_permission(self.current_profile_id, origin.host(), feature_name)
        if status == "allowed":
            page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionGrantedByUser)
            return
        elif status == "blocked":
            page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)
            return
            
        def callback(decision):
            if decision == "allow":
                self.permission_manager.set_permission(self.current_profile_id, origin.host(), feature_name, "allowed")
                page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionGrantedByUser)
                self.update_privacy_stats()
            elif decision == "allow_once":
                page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionGrantedByUser)
            elif decision == "block":
                self.permission_manager.set_permission(self.current_profile_id, origin.host(), feature_name, "blocked")
                page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionDeniedByUser)
                self.update_privacy_stats()

        bar = PermissionInfoBar(origin.host(), feature, callback)
        self.infobar_area.addWidget(bar)

    def on_request_blocked(self, url, reason):
        self.update_privacy_stats()

    def on_cookie_added(self, cookie):
        identifier = f"{cookie.domain()}:{cookie.name().data().decode('utf-8', errors='ignore')}"
        if identifier not in self.known_cookies:
            self.known_cookies.add(identifier)
            self.update_privacy_stats()

    def populate_profile_menu(self):
        menu = QMenu(self)
        profiles = self.profile_manager.get_all_profiles()
        for p in profiles:
            action = menu.addAction(p.name)
            if p.id == self.current_profile_id:
                action.setCheckable(True)
                action.setChecked(True)
            action.triggered.connect(lambda checked, pid=p.id: self.switch_profile(pid))
        
        menu.addSeparator()
        new_prof_action = menu.addAction("Create New Profile...")
        new_prof_action.triggered.connect(self.prompt_create_profile)
        
        self.toolbar.profile_btn.setMenu(menu)

    def switch_profile(self, profile_id):
        if profile_id == self.current_profile_id:
            return
        self.new_window = MainWindow(profile_id)
        self.new_window.show()

    def prompt_create_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Profile Name:")
        if ok and name:
            self.profile_manager.create_profile(name)
            self.populate_profile_menu()

    def new_private_window(self):
        self.private_window = MainWindow(is_private=True)
        self.private_window.show()
