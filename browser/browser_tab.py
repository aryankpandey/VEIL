from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import Signal

class VeilWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        scheme = url.scheme()
        if scheme == "veil":
            host = url.host()
            window = self.view().window()
            if host == "bookmarks" and hasattr(window, "bookmark_page"):
                window.bookmark_page()
            elif host == "private" and hasattr(window, "new_private_window"):
                window.new_private_window()
            elif host == "settings":
                # TODO: Implement settings abstraction
                pass
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class BrowserTab(QWebEngineView):
    permission_requested = Signal(object, object, object)

    def __init__(self, web_profile, parent=None):
        super().__init__(parent)
        page = VeilWebPage(web_profile, self)
        self.setPage(page)
        page.featurePermissionRequested.connect(self.on_feature_requested)

    def on_feature_requested(self, origin, feature):
        self.permission_requested.emit(self.page(), origin, feature)
