"""Reuse the bounded homepage evidence for public links and guided research."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlencode

PLATFORMS = {'github.com': 'GitHub', 'linkedin.com': 'LinkedIn', 'youtube.com': 'YouTube', 'facebook.com': 'Facebook', 'instagram.com': 'Instagram', 'twitter.com': 'Twitter / X', 'x.com': 'Twitter / X'}

class LinkReader(HTMLParser):
    """Read actual anchor links rather than matching arbitrary HTML substrings."""
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a' and len(self.links) < 500:
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

def footprint(case):
    """Describe links without visiting them or asserting ownership."""
    domain = case['domain']
    web = case.get('results', {}).get('web', {})
    data = web.get('data', {})
    parser = LinkReader()
    parser.feed(data.get('body', '')[:131072])
    links, seen = [], set()
    for href in parser.links:
        try:
            url = urlsplit(urljoin('https://' + domain + '/', href))
            if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or url.port not in (None, 80, 443):
                continue
            host = url.hostname.lower()
            social = next((v for k, v in PLATFORMS.items() if host == k or host.endswith('.' + k)), None)
            same_site = host == domain or host.endswith('.' + domain)
            document = same_site and url.path.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv'))
            if not social and not document:
                continue
            clean = url._replace(query='', fragment='').geturl()
            if clean in seen:
                continue
            seen.add(clean)
            links.append({'url': clean, 'kind': 'Social / code link' if social else 'Document link', 'label': social or url.path.rsplit('/', 1)[-1],
                          'note': 'Linked from the sampled homepage; not visited or ownership-verified.'})
        except ValueError:
            continue
    templates = [
        ('Public pages', f'site:{domain}', 'See pages indexed by the search engine.'),
        ('Public documents', f'site:{domain} filetype:pdf', 'Review indexed PDFs for information intended to be public.'),
        ('Public spreadsheets', f'site:{domain} (filetype:xls OR filetype:xlsx OR filetype:csv)', 'Review published spreadsheets. Their presence alone does not mean a data leak.'),
        ('Login pages', f'site:{domain} (inurl:login OR inurl:signin)', 'List public sign-in entry points without attempting to access accounts.'),
        ('Public code references', f'site:github.com "{domain}"', 'Find public references; a mention does not prove ownership.'),
        ('Privacy information', f'site:{domain} (privacy OR "data protection")', 'Find published privacy information; this is not a compliance assessment.'),
    ]
    queries = [{'title': title, 'query': query, 'meaning': meaning, 'url': 'https://www.google.com/search?' + urlencode({'q': query})} for title, query, meaning in templates]
    return {'links': links[:60], 'queries': queries, 'observed': web.get('status') == 'SUCCESS' and 200 <= data.get('status_code', 0) < 400,
            'note': 'Only the collected homepage was inspected. Search links are suggestions, not search results. Opening a search sends the domain and query to Google. Public visibility is not a vulnerability.'}
