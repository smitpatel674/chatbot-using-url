import re
import time
import queue
import urllib.parse as urlparse
import urllib.robotparser as robotparser
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set

import tldextract
import html2text
from playwright.sync_api import sync_playwright
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import clean_text, chunk_text

@dataclass
class Page:
    url: str
    title: str
    text: str

def extract_visible_text(html_content: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = False
    h.body_width = 0
    md = h.handle(html_content)
    return clean_text(md)

def extract_with_playwright(url: str, user_agent: str = "SiteChatbotBot/1.0") -> tuple[str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=user_agent)
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
        title = page.title()
        html_content = page.content()
        browser.close()
    text = extract_visible_text(html_content)
    return title, text

def canonicalize(base: str, href: str) -> Optional[str]:
    if not href:
        return None
    u = urlparse.urljoin(base, href)
    parsed = urlparse.urlparse(u)
    if parsed.scheme not in ("http", "https"):
        return None
    return parsed._replace(fragment="").geturl()

def is_same_domain(seed: str, candidate: str) -> bool:
    try:
        s = tldextract.extract(seed)
        c = tldextract.extract(candidate)
        return (s.registered_domain == c.registered_domain) and (c.registered_domain != "")
    except Exception:
        return False

@dataclass
class SiteKB:
    seed_url: str
    max_pages: int = 20
    max_depth: int = 2
    user_agent: str = "SiteChatbotBot/1.0 (+https://example.com)"
    request_delay: float = 0.5

    pages: List[Page] = field(default_factory=list)
    chunks: List[str] = field(default_factory=list)
    chunk_sources: List[Tuple[int, str]] = field(default_factory=list)
    vectorizer: Optional[TfidfVectorizer] = None
    tfidf_matrix = None
    robots: Optional[robotparser.RobotFileParser] = None

    def _init_robots(self):
        try:
            parsed = urlparse.urlparse(self.seed_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robots = rp
        except Exception:
            self.robots = None

    def _allowed(self, url: str) -> bool:
        if self.robots is None:
            return True
        try:
            return self.robots.can_fetch(self.user_agent, url)
        except Exception:
            return True

    def crawl(self):
        self._init_robots()
        seen: Set[str] = set()
        q: queue.Queue = queue.Queue()
        q.put((self.seed_url, 0))
        seen.add(self.seed_url)

        while not q.empty() and len(self.pages) < self.max_pages:
            url, depth = q.get()
            if not self._allowed(url):
                continue
            try:
                title, text = extract_with_playwright(url, self.user_agent)
                if text:
                    self.pages.append(Page(url=url, title=title, text=text))
                    chunks = chunk_text(text)
                    page_idx = len(self.pages) - 1
                    for ch in chunks:
                        self.chunks.append(ch)
                        self.chunk_sources.append((page_idx, url))
                if depth < self.max_depth:
                    for href in re.findall(r'href=["\'](.*?)["\']', text):
                        u = canonicalize(url, href)
                        if not u or u in seen:
                            continue
                        if is_same_domain(self.seed_url, u):
                            seen.add(u)
                            q.put((u, depth + 1))
            except Exception as e:
                print(f"Error scraping {url}: {e}")
            time.sleep(self.request_delay)

        if self.chunks:
            self.vectorizer = TfidfVectorizer(stop_words="english", max_features=50000)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)

    def retrieve(self, query: str, k: int = 6):
        if not self.chunks or self.vectorizer is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        idxs = sims.argsort()[::-1][:k]
        return [(self.chunks[i], self.chunk_sources[i][1]) for i in idxs]
