import requests
from requests.exceptions import RequestException
from typing import Optional, Dict, Any

class RemoteComm:
    """
    Handles HTTP/HTTPS POST communication with a user-specified remote endpoint.
    """
    def __init__(self, url: Optional[str] = None):
        self.url = url

    def set_url(self, url: str):
        """Set the remote endpoint URL. Allows both http:// and https:// URLs."""
        if not (url.lower().startswith('http://') or url.lower().startswith('https://')):
            raise ValueError('Only HTTP or HTTPS URLs are allowed.')
        self.url = url

    def send_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a JSON payload to the remote endpoint via HTTPS POST.
        Returns a dict with 'success', 'status_code', 'response', and 'error' (if any).
        """
        if not self.url:
            return {'success': False, 'error': 'Remote URL not set.'}
        try:
            resp = requests.post(self.url, json=data, timeout=10)
            resp.raise_for_status()
            return {
                'success': True,
                'status_code': resp.status_code,
                'response': resp.text,
                'error': None
            }
        except RequestException as e:
            return {
                'success': False,
                'status_code': getattr(e.response, 'status_code', None),
                'response': getattr(e.response, 'text', ''),
                'error': str(e)
            } 