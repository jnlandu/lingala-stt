# Lingala Speech‑to‑Text Corpus (Lingala‑STT)

A community‑driven effort to create, curate, and openly publish a high‑quality Lingala speech corpus for automatic speech recognition (ASR) research and products.

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
│   ├── interim/             ← sliced, not yet validated
│   └── processed/           ← train/dev/test splits + manifests
├── prompts/                 ← sentence prompts (.tsv) for crowd recording
├── scripts/
│   ├── download_okapi.py    ← grab daily Radio Okapi bulletins
│   ├── segment.py           ← silence‑based segmentation
│   ├── align_whisper.py     ← auto‑transcribe + forced alignment
│   ├── validate_ui.py       ← launch Clip‑Editor for manual validation
│   └── export_hf.py         ← push processed dataset to Hugging Face Hub
├── docs/
│   ├── STYLE_GUIDE.md       ← transcription conventions
│   ├── ROADMAP.md           ← milestones & governance
│   └── model_zoo.md         ← checkpoints & WER table
└── .github/
    └── workflows/
        ├── lint.yml         ← flake8 + black
        └── validate.yml     ← CI: dataset schema + audio integrity
```

## Audio Sources
- **Radio Okapi**: daily news bulletins (1–15 min) from the DRC’s leading radio station.
- **Crowd recordings**: short prompts (1–5 s) read by volunteers across the DRC.
- **Field recordings**: spontaneous conversations and dialect samples from various regions.
- **Public domain**: any other audio clips in Lingala that are freely available.
 - **Social Media**: 
    -  'facebook_live': 'Live Lingala broadcasts',
    -  'tiktok_videos': 'Short clips with clear speech'
    -  'YouTube': 'Lingala content from YouTube channels'
---

## 🚀 Quick‑start

```bash
# 1. clone & install
$ git clone https://github.com/your‑org/lingala-stt.git
$ cd lingala-stt
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 2. download & segment a single Radio Okapi bulletin (example)
$ python scripts/download_okapi.py --date 2025-06-11  
$ python scripts/segment.py data/raw/2025‑06‑11_okapi.mp3 \
                        --out_dir data/interim/2025‑06‑11

# 3. auto‑align
$ python scripts/align_whisper.py data/interim/2025‑06‑11  

# 4. manual validation UI (opens in browser)
$ python scripts/validate_ui.py

# 5. export HF‑ready dataset
$ python scripts/export_hf.py --repo jeremie/lingala-stt-dev
```

---

## 🤝 Contributing

1. **Check an issue** tagged `good first issue` or open a new one.
2. Follow the [STYLE\_GUIDE](docs/STYLE_GUIDE.md) when transcribing.
3. Run `pre-commit run --all-files` before pushing.
4. Submit your PR—GitHub Actions will run lint + dataset integrity checks.

All contributors agree to license their work under **CC‑BY‑4.0**.

---

## 📜 License

```
Creative Commons Attribution 4.0 International
<https://creativecommons.org/licenses/by/4.0/>
```

---

## 🛠️ Dataset card for the Hugging Face Hub

Below is a template you can copy to `dataset_card.md` in **a *separate* Hugging Face repo** (e.g. `jeremie/lingala-stt`).
Lines starting with `>` are comments to remove.

````yaml
---
language: [ "ln" ]         # ISO 639‑1 for Lingala
license: "cc-by-4.0"
pretty_name: "Lingala Speech‑to‑Text Corpus v1.0"
version: "1.0.0"
author: "Lingala‑STT community"
multilinguality: monolingual
> Add more tags if you also provide French/English translations
---

# Lingala Speech‑to‑Text Corpus v1.0

## Summary
A 120‑hour validated corpus of spoken Lingala covering news broadcasts, crowd‑read prompts, and conversational speech.  Each clip is 1–15 seconds long, 48 kHz WAV, with orthographic transcription in standard Lingala.

## Supported Tasks and Leaderboards
- **Automatic Speech Recognition** (primary)
- **Self‑supervised pre‑training** (raw split)

| Split | Hours | # Clips | # Speakers |
|-------|------:|--------:|-----------:|
| train | 102 h | 46 381 |  310 |
| dev   |  12 h |  5 468 |   90 |
| test  |   6 h |  2 601 |   82 |

## Usage example
```python
from datasets import load_dataset
ds = load_dataset("jeremie/lingala-stt", split="train")
print(ds[0]["audio"]["array"], ds[0]["text"])
````

## Citation

```
@dataset{lingala_stt_2025,
  title     = {Lingala Speech‑to‑Text Corpus v1.0},
  author    = {Jeremie Nlandu Mabiala and contributors},
  year      = {2025},
  publisher = {Hugging Face},
  version   = {1.0},
  url       = {https://huggingface.co/datasets/jeremie/lingala-stt}
}
```

---

```

---

## 🔄 How GitHub ↔︎ Hugging Face sync works

1. **Dataset building scripts live in this GitHub repo.**
2. GitHub Action `export_hf.yml` (coming soon) runs nightly or on demand to:
   - pull latest `data/processed/` manifests,
   - upload only the diff to the HF dataset repo via `huggingface_hub` CLI,
   - trigger the HF dataset viewer refresh.
3. Model checkpoints fine‑tuned on this data can then depend on the same HF dataset repo.

---

## 📅 Roadmap (excerpt)

| Month | Deliverable |
|-------|-------------|
| 2025‑07 | v0.2 release (60 h) + baseline WER report |
| 2025‑10 | Field recordings (dialects) merged |
| 2026‑02 | v1.0 stable + Interspeech paper prep |

<br/>

---

*Maintained by @jeremie‑nlandu and the Lingala‑STT community. For questions, open an issue or ping **#lingala-asr** on the Masakhane Discord.*

```
