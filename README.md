# Lingala Speech (Radio Okapi bulletins)

A catalogue of Lingala broadcast news audio for building automatic speech recognition (ASR) data, with the scraper used to collect it. The audio is Radio Okapi's daily *Journal Lingala* bulletin: professional, read news speech from the Democratic Republic of the Congo.

This dataset is also part of [lingala-nlp-datasets](https://github.com/jnlandu/lingala-nlp-datasets), alongside an English–Lingala parallel corpus and Lingala proverbs.

**Status:** collection only. The audio has **not been transcribed, segmented or aligned yet**, and no model has been trained on it.

## Contents

| File | Description |
|---|---|
| `manifest.jsonl` | One line per bulletin: 31 bulletins, 5.6 hours, January 2023 to June 2025 |
| `scripts/download_okapi.py` | Scraper that downloads bulletins and their metadata from radiookapi.net |
| `requirements.txt` | Python dependencies for the scraper |
| `LICENSE` | CC BY-SA 4.0 (manifest and scripts only) |

The audio itself is **not in this repository**. It belongs to Radio Okapi, so it is not redistributed here. Use the manifest and the scraper to rebuild it locally (see below).

## Format

`manifest.jsonl` is UTF-8 JSON Lines. Example line:

```json
{"id": "24012023-p-l-journallingalamatin-web_0", "date": "2023-01-24", "session": "morning", "duration_s": 686.7, "sha256": "fd304a5ee14775f88eb0d120b73997439650267cfc5eb319b3a1d5b08a903162", "article_number": 4, "source_url": "https://www.radiookapi.net/journal-journal-lingala/journal-lingala-matin-4", "audio_url": "https://www.radiookapi.net/sites/default/files/2023-01/24012023-p-l-journallingalamatin-web_0.mp3", "language": "ln", "transcribed": false}
```

| Field | Description |
|---|---|
| `id` | Radio Okapi's file name, without extension |
| `date` | Broadcast date (ISO 8601) |
| `session` | `morning` (*matin*) or `evening` (*soir*) bulletin |
| `duration_s` | Audio length in seconds |
| `sha256` | Checksum of the MP3, to verify a rebuilt copy is identical |
| `article_number` | Radio Okapi's bulletin number |
| `source_url`, `audio_url` | Bulletin page and direct MP3 link on radiookapi.net |
| `language` | `ln` (Lingala) |
| `transcribed` | Whether a transcript exists (all `false` for now) |

- 31 unique bulletins, 5.57 hours in total, about 11 minutes each
- 30 morning bulletins and 1 evening bulletin
- One bulletin (2025-06-10, evening) has no `source_url` or `audio_url`

## Rebuilding the audio

```bash
pip install -r requirements.txt

# bulletins by Radio Okapi article number (e.g. 190 to 200)
python scripts/download_okapi.py --start 190 --end 200 --out data/raw/okapi --incremental

# check a download against the manifest
shasum -a 256 data/raw/okapi/*.mp3
```

The scraper saves each MP3 with a metadata JSON file and writes `manifest.json` in the output folder. `--incremental` skips bulletins already downloaded. It only covers the Lingala **morning** bulletin. To collect regularly, run it from cron, for example daily at 07:00:

```
0 7 * * * cd /path/to/lingala-stt && python scripts/download_okapi.py --latest 5 --out data/raw/okapi --incremental
```

Known issue: `--latest N` does not always return the newest bulletins, so use `--start`/`--end` when you need specific dates.

## Next steps

1. Segment the bulletins into utterances (voice-activity detection).
2. Draft transcripts with an existing Lingala-capable model (Meta MMS, Whisper) and correct a held-out subset by hand.
3. Fine-tune a baseline (e.g. MMS) and report word error rate on that corrected subset.
4. Extend the scraper to Radio Okapi's Kikongo and Tshiluba bulletins.

## License

The **manifest and scripts** are licensed under [CC BY-SA 4.0](LICENSE). The **audio** is © Radio Okapi and is not covered by that license. Check Radio Okapi's terms before using it beyond research.
