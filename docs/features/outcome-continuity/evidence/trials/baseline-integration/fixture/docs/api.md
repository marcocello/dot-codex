# ArchiveBox API v2
POST /exports with account_id creates an export. Response: export_id, status_url. GET status_url returns state (pending, ready, failed) and download_path when ready. Render a download link once ready. Example download_path: /downloads/e_123.zip. Client version: 2.4.0.
