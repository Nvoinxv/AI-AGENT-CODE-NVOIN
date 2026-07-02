import urllib.request
import urllib.error
from html.parser import HTMLParser
from tools.base_tool import BaseTool

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.ignore_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            stripped = data.strip()
            if stripped:
                self.text_parts.append(stripped)

    def get_text(self):
        return "\n".join(self.text_parts)

class FetchWebPageTool(BaseTool):
    name = "fetch_web_page"
    description = "Mengambil isi halaman web / dokumentasi online berdasarkan URL (Browser tool untuk Nvoin AI)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL lengkap halaman web yang ingin dibaca (misal: https://docs.python.org)."}
        },
        "required": ["url"]
    }

    def execute(self, url: str, **kwargs) -> str:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NvoinAI/2.0 (Cloud Agent)'
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content_type = response.headers.get_content_type()
                raw_data = response.read().decode('utf-8', errors='ignore')
                
                if 'html' in content_type:
                    parser = _HTMLTextExtractor()
                    parser.feed(raw_data)
                    clean_text = parser.get_text()
                    return f"=== HASIL BROWSER FETCH: {url} ===\n" + clean_text[:6000]
                else:
                    return f"=== HASIL FETCH TEKS/JSON: {url} ===\n" + raw_data[:6000]
        except urllib.error.HTTPError as e:
            return f"Error Browser HTTP ({e.code}): Gagal mengambil halaman '{url}'."
        except urllib.error.URLError as e:
            return f"Error Browser Koneksi: Tidak dapat terhubung ke '{url}' ({e.reason})."
        except Exception as e:
            return f"Error menjalankan Browser Tool untuk '{url}': {str(e)}"
