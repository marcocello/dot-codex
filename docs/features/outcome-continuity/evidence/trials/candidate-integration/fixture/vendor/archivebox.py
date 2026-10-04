"""ArchiveBox client 2.4.0; bundled vendor source."""
from urllib.parse import urljoin
class ArchiveBox:
    def __init__(self, transport, endpoint):
        self.transport = transport
        self.endpoint = endpoint
    def create_export(self, account_id):
        return self.transport.post('/exports', {'account_id': account_id})
    def export_status(self, status_url):
        return self.transport.get(status_url)
    def download(self, download_path):
        # Paths require the account bearer token. Never suitable for browser links.
        return self.transport.get_bytes(urljoin(self.endpoint, download_path))
    def share_export(self, export_id, ttl_seconds=300):
        # Public, expiring URL; new exports have no shares by default.
        return self.transport.post('/exports/' + export_id + '/shares',
                                   {'ttl_seconds': ttl_seconds})['url']
