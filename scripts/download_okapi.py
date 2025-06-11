#  Run the code using the command:
#  python download_okapi.py "https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-192"

#

import re, sys, requests
from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup

def fetch_mp3(article_url: str) -> str:
    html = requests.get(article_url, timeout=10).text
    
    # Fixed regex pattern - single backslash for the dot
    mp3_match = re.search(r'(/sites/default/files/[^"\']+?\.mp3)', html)
    
    if not mp3_match:
        print("No MP3 found. Debugging...")
        # Debug: look for any mention of mp3
        mp3_mentions = re.findall(r'[^"\'>\s]*mp3[^"\'<\s]*', html, re.I)
        print(f"Found {len(mp3_mentions)} MP3 mentions: {mp3_mentions[:5]}")
        
        # Debug: look for download links
        soup = BeautifulSoup(html, 'html.parser')
        download_links = soup.find_all('a', string=re.compile(r'(télécharger|download)', re.I))
        print(f"Found {len(download_links)} download links:")
        for link in download_links:
            print(f"  Text: '{link.get_text()}' -> Href: '{link.get('href')}'")
        
        # Try alternative patterns
        alternative_patterns = [
            r'href="(/sites/default/files/[^"]+\.mp3)"',
            r"href='(/sites/default/files/[^']+\.mp3)'",
            r'(/sites/default/files/\S+\.mp3)',
            r'(https?://[^"\'>\s]+\.mp3)'
        ]
        
        for i, pattern in enumerate(alternative_patterns):
            matches = re.findall(pattern, html)
            if matches:
                print(f"Pattern {i+1} found: {matches}")
                return urljoin(article_url, matches[0])
        
        raise ValueError("No MP3 file found on this page")
    
    return urljoin(article_url, mp3_match.group(1))

def download(url: str, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=15) as r, open(out, "wb") as f:
        r.raise_for_status()
        for chunk in r.iter_content(8192):
            f.write(chunk)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_okapi.py <article_url>")
        print("Example: python download_okapi.py 'https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-190'")
        sys.exit(1)
    
    article = sys.argv[1]
    print(f"Checking article: {article}")
    
    try:
        mp3_url = fetch_mp3(article)
        print("Found MP3:", mp3_url)
        fn = Path("data/raw/okapi") / Path(mp3_url).name
        download(mp3_url, fn)
        print("Saved to", fn)
    except Exception as e:
        print(f"Error: {e}")