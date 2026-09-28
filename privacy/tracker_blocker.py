from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PySide6.QtCore import Signal
import re

class TrackerBlocker(QWebEngineUrlRequestInterceptor):
    request_blocked = Signal(str, str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Local Blocklists
        self.blocklist_domains = [
            "google-analytics.com",
            "doubleclick.net",
            "scorecardresearch.com",
            "quantserve.com",
            "facebook.net",
            "connect.facebook.net",
            "analytics.twitter.com",
            "criteo.com"
        ]
        
        self.blocklist_patterns = [
            r"/ad[s]?/",
            r"/track(er|ing)?/",
            r"/pixel\?"
        ]
        
        self.resource_type_blocks = [] # E.g., QWebEngineUrlRequestInfo.ResourceType.ResourceTypeImage
        
        self.allowlist_domains = []
        
        self.per_site_exceptions = {}
        
        self.blocked_count = 0

    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl().toString()
        host = info.requestUrl().host()
        first_party = info.firstPartyUrl().host()
        resource_type = info.resourceType()
        
        # 1. Allowlist check
        if host in self.allowlist_domains:
            return

        # 2. Per-site exception check
        if first_party in self.per_site_exceptions:
            if host in self.per_site_exceptions[first_party]:
                return

        # 3. Resource type check
        if resource_type in self.resource_type_blocks:
            self._block_request(info, url, f"Resource Type Blocked")
            return

        # 4. Domain blocklist
        for blocked in self.blocklist_domains:
            if blocked in host:
                self._block_request(info, url, f"Domain: {blocked}")
                return

        # 5. Pattern blocklist
        for pattern in self.blocklist_patterns:
            if re.search(pattern, url):
                self._block_request(info, url, f"Pattern: {pattern}")
                return

    def _block_request(self, info, url, reason):
        info.block(True)
        self.blocked_count += 1
        self.request_blocked.emit(url, reason)
