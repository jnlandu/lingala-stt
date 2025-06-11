#!/usr/bin/env python3
"""
Automated Radio Okapi Lingala scraper with article number iteration
Usage: python download_okapi_auto.py --start 190 --end 200 --out data/raw/okapi
"""
# filepath: scripts/download_okapi_auto.py

import re, sys, requests, json, time, argparse, logging
from urllib.parse import urljoin
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"okapi_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

BASE_URL = "https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-"

def fetch_mp3_from_article(article_num: int) -> dict:
    """Fetch MP3 from a specific article number"""
    article_url = f"{BASE_URL}{article_num}"
    
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        html = response.text
        
        # Multiple patterns to try
        patterns = [
            r'(/sites/default/files/[^"\']+?\.mp3)',
            r'href="(/sites/default/files/[^"]+\.mp3)"',
            r"href='(/sites/default/files/[^']+\.mp3)'",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                mp3_path = matches[0]
                mp3_url = urljoin("https://www.radiookapi.net", mp3_path)
                
                # Extract metadata from page
                soup = BeautifulSoup(html, 'html.parser')
                title_elem = soup.find(['h1', 'h2', 'title'])
                title = title_elem.get_text(strip=True) if title_elem else f"Journal Lingala Matin {article_num}"
                
                # Try to extract date from content or filename
                date_match = re.search(r'(\d{2})(\d{2})(\d{4})', mp3_path)
                date = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}" if date_match else None
                
                return {
                    'article_num': article_num,
                    'article_url': article_url,
                    'mp3_url': mp3_url,
                    'title': title,
                    'date': date,
                    'filename': Path(mp3_path).name,
                    'found': True
                }
        
        logger.warning(f"No MP3 found in article {article_num}")
        return {'article_num': article_num, 'found': False, 'error': 'No MP3 found'}
        
    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 404:
            logger.info(f"Article {article_num} not found (404)")
            return {'article_num': article_num, 'found': False, 'error': '404 Not Found'}
        else:
            logger.error(f"Error fetching article {article_num}: {e}")
            return {'article_num': article_num, 'found': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"Unexpected error for article {article_num}: {e}")
        return {'article_num': article_num, 'found': False, 'error': str(e)}

def download_mp3(mp3_info: dict, output_dir: Path) -> bool:
    """Download MP3 file"""
    if not mp3_info.get('found'):
        return False
    
    filename = mp3_info['filename']
    output_path = output_dir / filename
    
    # Skip if file already exists
    if output_path.exists():
        logger.info(f"⏭️  Skipping existing file: {filename}")
        return True
    
    try:
        logger.info(f"⬇️  Downloading: {filename}")
        
        response = requests.get(mp3_info['mp3_url'], stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        size_mb = output_path.stat().st_size / 1024 / 1024
        logger.info(f"✅ Downloaded: {filename} ({size_mb:.1f} MB)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Download failed for {filename}: {e}")
        if output_path.exists():
            output_path.unlink()  # Remove partial file
        return False

def save_metadata(mp3_info: dict, output_dir: Path):
    """Save metadata for downloaded file"""
    if not mp3_info.get('found'):
        return
    
    metadata_dir = output_dir / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    
    filename_stem = Path(mp3_info['filename']).stem
    metadata_file = metadata_dir / f"{filename_stem}.json"
    
    metadata = {
        'article_number': mp3_info['article_num'],
        'title': mp3_info['title'],
        'date': mp3_info['date'],
        'source_url': mp3_info['article_url'],
        'audio_url': mp3_info['mp3_url'],
        'filename': mp3_info['filename'],
        'downloaded_at': datetime.now().isoformat(),
        'source': 'radio_okapi_lingala'
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

def find_article_range(start_num: int = None, end_num: int = None) -> tuple:
    """Find valid article number range by probing"""
    logger.info("🔍 Finding valid article range...")
    
    if start_num and end_num:
        return start_num, end_num
    
    # If no range specified, find the current range
    current_num = 200  # Start from a reasonable number
    
    # Find the highest available article
    while current_num < 1000:  # Safety limit
        result = fetch_mp3_from_article(current_num)
        if result.get('error') == '404 Not Found':
            break
        current_num += 1
        time.sleep(0.1)  # Small delay
    
    max_num = current_num - 1
    min_num = max(1, max_num - 50)  # Get last 50 articles
    
    logger.info(f"📊 Found article range: {min_num} to {max_num}")
    return min_num, max_num

def load_processed_articles(output_dir: Path) -> set:
    """Load list of already processed articles"""
    processed_file = output_dir / "processed_articles.json"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_articles(output_dir: Path, processed: set):
    """Save list of processed articles"""
    processed_file = output_dir / "processed_articles.json"
    with open(processed_file, 'w') as f:
        json.dump(list(processed), f, indent=2)

def generate_manifest(output_dir: Path):
    """Generate dataset manifest"""
    manifest = []
    
    for mp3_file in output_dir.glob("*.mp3"):
        metadata_file = output_dir / "metadata" / f"{mp3_file.stem}.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {
                'title': mp3_file.stem,
                'article_number': None,
                'date': None
            }
        
        manifest.append({
            'audio_path': str(mp3_file.relative_to(output_dir.parent.parent)),
            'filename': mp3_file.name,
            'title': metadata.get('title', mp3_file.stem),
            'article_number': metadata.get('article_number'),
            'date': metadata.get('date'),
            'source': 'radio_okapi',
            'source_url': metadata.get('source_url'),
            'file_size': mp3_file.stat().st_size,
            'language': 'ln',
            'needs_transcription': True
        })
    
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📋 Generated manifest with {len(manifest)} files")

def main():
    parser = argparse.ArgumentParser(description="Automated Radio Okapi Lingala scraper")
    parser.add_argument("--start", type=int, help="Start article number")
    parser.add_argument("--end", type=int, help="End article number")
    parser.add_argument("--out", type=str, default="data/raw/okapi", help="Output directory")
    parser.add_argument("--threads", type=int, default=3, help="Number of concurrent downloads")
    parser.add_argument("--incremental", action="store_true", help="Skip already processed articles")
    parser.add_argument("--latest", type=int, help="Download only the latest N articles")
    parser.add_argument("--metadata", action="store_true", default=True, help="Save metadata")
    parser.add_argument("--manifest", action="store_true", default=True, help="Generate manifest")
    
    args = parser.parse_args()
    
    # Setup directories
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load processed articles for incremental mode
    processed_articles = load_processed_articles(output_dir) if args.incremental else set()
    
    # Determine article range
    if args.latest:
        # Find current max and go backwards
        _, max_num = find_article_range()
        start_num = max(1, max_num - args.latest + 1)
        end_num = max_num
    else:
        start_num, end_num = find_article_range(args.start, args.end)
    
    logger.info(f"🚀 Starting scrape of articles {start_num} to {end_num}")
    logger.info(f"📁 Output directory: {output_dir}")
    logger.info(f"🧵 Using {args.threads} threads")
    logger.info(f"🔄 Incremental mode: {args.incremental}")
    
    # Generate article numbers to process
    article_numbers = []
    for num in range(start_num, end_num + 1):
        if args.incremental and num in processed_articles:
            continue
        article_numbers.append(num)
    
    logger.info(f"📊 Processing {len(article_numbers)} articles")
    
    # Process articles with threading
    successful_downloads = 0
    failed_downloads = 0
    processed_count = 0
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit all article fetching tasks
        future_to_num = {
            executor.submit(fetch_mp3_from_article, num): num 
            for num in article_numbers
        }
        
        for future in as_completed(future_to_num):
            article_num = future_to_num[future]
            processed_count += 1
            
            try:
                mp3_info = future.result()
                
                if mp3_info.get('found'):
                    # Download the MP3
                    if download_mp3(mp3_info, output_dir):
                        successful_downloads += 1
                        
                        # Save metadata
                        if args.metadata:
                            save_metadata(mp3_info, output_dir)
                    else:
                        failed_downloads += 1
                else:
                    # Still count as processed
                    pass
                
                # Update processed list
                processed_articles.add(article_num)
                
                # Progress update
                if processed_count % 10 == 0:
                    logger.info(f"📈 Progress: {processed_count}/{len(article_numbers)} articles processed")
                
            except Exception as e:
                logger.error(f"Error processing article {article_num}: {e}")
                failed_downloads += 1
            
            # Small delay between requests
            time.sleep(0.1)
    
    # Save processed articles list
    if args.incremental:
        save_processed_articles(output_dir, processed_articles)
    
    # Generate manifest
    if args.manifest:
        generate_manifest(output_dir)
    
    # Summary
    logger.info(f"🎉 Scraping complete!")
    logger.info(f"✅ Successful downloads: {successful_downloads}")
    logger.info(f"❌ Failed downloads: {failed_downloads}")
    logger.info(f"📁 Total files: {len(list(output_dir.glob('*.mp3')))}")
    logger.info(f"💾 Output directory: {output_dir}")

if __name__ == "__main__":
    main()