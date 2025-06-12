# Lingala Speech‑to‑Text Corpus (Lingala‑STT)

A community‑driven effort to create, curate, and openly publish a high‑quality Lingala speech corpus for automatic speech recognition (ASR) research and products.

**🚀 Now with automated data collection!** GitHub Actions automatically downloads new Radio Okapi audio every 12 hours.

---

## 📁 Repository layout

```
lingala-stt/
├── README.md                ← you are here
├── LICENSE                  ← CC‑BY‑4.0
├── .gitignore
├── requirements.txt         ← Python deps (pysoundfile, torchaudio, whisper, pyanote, etc.)
├── data/
│   ├── raw/                 ← untouched downloads (radio, field recordings …)
│   │   └── okapi/           ← automated Radio Okapi downloads
│   │       ├── *.mp3        ← daily audio bulletins
│   │       ├── metadata/    ← article info, dates, URLs
│   │       └── manifest.json ← dataset catalog
│   ├── interim/             ← sliced, not yet validated
│   └── processed/           ← train/dev/test splits + manifests
├── prompts/                 ← sentence prompts (.tsv) for crowd recording
├── scripts/
│   ├── download_okapi.py    ← automated Radio Okapi scraper (with article numbering)
│   ├── segment.py           ← silence‑based segmentation
│   ├── align_whisper.py     ← auto‑transcribe + forced alignment
│   ├── validate_ui.py       ← launch Clip‑Editor for manual validation
│   └── export_hf.py         ← push processed dataset to Hugging Face Hub
├── logs/                    ← scraper logs and download reports
├── docs/
│   ├── STYLE_GUIDE.md       ← transcription conventions
│   ├── ROADMAP.md           ← milestones & governance
│   └── model_zoo.md         ← checkpoints & WER table
└── .github/
    └── workflows/
        ├── lint.yml         ← flake8 + black
        ├── validate.yml     ← CI: dataset schema + audio integrity
        └── radio_okapi.yml  ← automated audio collection (every 12h)
```

## 🎵 Audio Sources

### Automated Collection
- **🤖 Radio Okapi (Automated)**: Daily Lingala news bulletins automatically downloaded every 12 hours
  - Source: `https://www.radiookapi.net/journal-journal-lingala/`
  - Format: MP3, 1–15 min segments
  - Schedule: 6 AM & 6 PM UTC daily
  - Language: Lingala news broadcasts from DRC

### Manual Collection
- **Crowd recordings**: Short prompts (1–5 s) read by volunteers across the DRC
- **Field recordings**: Spontaneous conversations and dialect samples from various regions
- **Public domain**: Any other audio clips in Lingala that are freely available
- **Social Media Sources**: 
  - `facebook_live`: Live Lingala broadcasts
  - `tiktok_videos`: Short clips with clear speech
  - `YouTube`: Lingala content from YouTube channels

---

## 🚀 Quick‑start

### Option 1: Use Pre-collected Data (Recommended)
```bash
# 1. Clone & install
git clone https://github.com/jnlandu/lingala-stt.git
cd lingala-stt
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Check existing audio files (automatically collected)
ls data/raw/okapi/          # View downloaded MP3 files
cat data/raw/okapi/manifest.json | jq '.[] | {filename, title, date}'

# 3. Process existing audio
python scripts/segment.py data/raw/okapi/ \
                          --out_dir data/interim/okapi \
                          --batch_mode

# 4. Auto-align with Whisper
python scripts/align_whisper.py data/interim/okapi/

# 5. Manual validation UI (opens in browser)
python scripts/validate_ui.py

# 6. Export HF-ready dataset
python scripts/export_hf.py --repo jeremie/lingala-stt-dev
```

### Option 2: Download Fresh Audio
```bash
# Download latest 20 Radio Okapi articles
python scripts/download_okapi.py \
  --latest 20 \
  --out data/raw/okapi \
  --metadata \
  --manifest

# Download specific article range
python scripts/download_okapi.py \
  --start 190 \
  --end 210 \
  --out data/raw/okapi \
  --metadata \
  --manifest \
  --incremental
```

---

## 🤖 Automated Data Collection

### GitHub Actions Workflow
The repository automatically collects new Lingala audio:

- **📅 Schedule**: Every 12 hours (6 AM & 6 PM UTC)
- **🎯 Target**: Latest 20 Radio Okapi articles per run
- **📊 Volume**: ~40 articles per day (~1-2 hours of audio)
- **🔄 Mode**: Incremental (skips existing files)
- **💾 Storage**: Git LFS for audio files, metadata in JSON

### Manual Trigger
You can manually trigger collection:

1. Go to **Actions** tab in GitHub
2. Click **"Radio Okapi Lingala Scraper"**
3. Click **"Run workflow"**
4. Customize parameters:
   - Article count: `20` (default)
   - Force full scan: `false`

### Local Testing
```bash
# Test the scraper locally
python scripts/download_okapi.py --latest 5 --out data/raw/okapi

# Check what was downloaded
find data/raw/okapi -name "*.mp3" | head -5
cat data/raw/okapi/manifest.json | jq '.[0]'
```

---

## 📊 Dataset Statistics (Live)

| Metric | Value | Auto-Updated |
|--------|-------|--------------|
| **Total Audio Files** | `find data/raw/okapi -name "*.mp3" \| wc -l` | Every 12h |
| **Total Duration** | `~40 min per day` | Growing |
| **Language** | Lingala (ln) | - |
| **Source Quality** | Radio broadcast | High |
| **Collection Started** | June 2025 | - |

### Article Numbering System
Radio Okapi articles follow the pattern:
```
https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-{NUMBER}
```
- **Latest articles**: Automatically detected
- **Range scanning**: Articles 1-1000+ available
- **Incremental updates**: Only new articles downloaded

---

## 🤝 Contributing

### Data Contribution
1. **Automated**: GitHub Actions handles Radio Okapi collection
2. **Manual audio**: Add files to `data/raw/` with proper metadata
3. **Transcriptions**: Follow the [STYLE\_GUIDE](docs/STYLE_GUIDE.md)
4. **Validation**: Use `scripts/validate_ui.py` for quality control

### Code Contribution
1. **Check an issue** tagged `good first issue` or open a new one
2. **Test changes**: Run `python scripts/download_okapi.py --latest 2` 
3. **Quality checks**: Run `pre-commit run --all-files` before pushing
4. **Submit PR**: GitHub Actions will run lint + dataset integrity checks

All contributors agree to license their work under **CC‑BY‑4.0**.

---

## 🔧 Troubleshooting

### Scraper Issues
```bash
# Check logs
tail -f logs/okapi_auto_*.log

# Test single article
python scripts/download_okapi.py --start 192 --end 192 --out data/test

# Verify GitHub Actions
# Go to Actions tab → Radio Okapi Lingala Scraper → Latest run
```

### Storage Issues
```bash
# Check Git LFS usage
git lfs ls-files
du -sh data/raw/okapi/

# Clean up old artifacts
find data/raw/okapi -name "*.mp3" -mtime +30 -delete
```

---

## 📜 License

```
Creative Commons Attribution 4.0 International
<https://creativecommons.org/licenses/by/4.0/>
```

**Note**: Automated collection respects Radio Okapi's terms of service and maintains respectful crawling practices (rate limiting, user agent identification).

---

## 🛠️ Dataset Card for Hugging Face Hub

Below is a template for the HF dataset repository (`jeremie/lingala-stt`):

````yaml
---
language: ["ln"]
license: "cc-by-4.0"
pretty_name: "Lingala Speech‑to‑Text Corpus v1.0"
version: "1.0.0"
tags:
- automatic-speech-recognition
- lingala
- radio-okapi
- drc
- audio-dataset
multilinguality: monolingual
task_categories:
- automatic-speech-recognition
---

# Lingala Speech‑to‑Text Corpus v1.0

## Summary
A continuously growing corpus of spoken Lingala, automatically collected from Radio Okapi daily broadcasts. Each clip is 1–15 seconds long, 48 kHz MP3, with metadata including article numbers, dates, and source URLs.

## Automated Collection
- **Source**: Radio Okapi Lingala morning news
- **Collection**: Every 12 hours via GitHub Actions
- **Growth rate**: ~40 articles/day (~1-2 hours audio)
- **Quality**: Professional radio broadcast quality

## Dataset Structure
```python
{
  "audio": {"path": "001.mp3", "array": [...], "sampling_rate": 48000},
  "text": "Boyokani nsango ya mokolo oyo...",  # To be transcribed
  "article_number": 192,
  "title": "Journal Lingala Matin",
  "date": "12/06/2025",
  "source_url": "https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-192",
  "filename": "12062025-p-l-journallingalamatin-00web.mp3"
}
```

## Usage Example
```python
from datasets import load_dataset
ds = load_dataset("jeremie/lingala-stt", split="train")
print(f"Audio shape: {ds[0]['audio']['array'].shape}")
print(f"Article: {ds[0]['title']} (#{ds[0]['article_number']})")
```

