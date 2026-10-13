> **Origen:** informe que trajo el usuario el 2026-10-13, de su otro proyecto (un asistente de voz para la HMI que también se llama Leda), copiado tal cual. Las rutas de archivos que cita son de ese proyecto, no de este repositorio. Sirve de base para la **J2b** (la voz a texto en el servidor, `../../odd/tasks/plataforma-jerarquias.md`): sobre todo la sección 3 (voz a texto), la 6 (claves y tiempos) y la 5 (latencia). La parte de texto a voz (sección 4) queda para cuando Leda responda con audio.

# Gemini voice service: replication report

This report describes how Leda (a voice assistant) uses Google Gemini for speech in both directions:

- **Speech-to-text (STT):** it transcribes Telegram voice notes.
- **Text-to-speech (TTS):** it speaks answers as Telegram voice notes and as a live PCM stream.

It also records how the low latencies were reached, with the measured numbers. The reader is an AI agent that must build the same capability in a different application. Every claim cites a file and line in this repository, so it can be checked.

Scope: the Gemini voice path only. The HMI user interface, the answer engine and the browser audio player are out of scope, except where they explain a design choice.

Conventions:

- **Measured** = observed numbers with a date and a source.
- **Design** = a deliberate choice, with its reason.
- **Unverified** = an idea or assumption that was never measured.

Paths are relative to `services/leda-runtime/src/leda_runtime/` unless they start with `docs/`, `odd/` or `services/`.

---

## 1. TL;DR

| Topic | Answer |
|---|---|
| SDK | `google-genai==2.17.0`, sync client, `httpx==0.28.1` transport. |
| STT model | `gemini-3.8-flash` via `client.models.generate_content`. The audio is one inline `Part` (Telegram OGG/Opus, sent unchanged). Config: `thinking_budget=0`, `temperature=0`, `max_output_tokens=128`. |
| TTS model | `gemini-3.8-flash-lite-tts`, voice `Leda`, via `client.models.generate_content_stream`. Config: `response_modalities=["AUDIO"]`, prebuilt voice. The input is the plain answer text, with no prompt wrapper. |
| TTS output | Raw PCM: signed 16-bit little-endian, 24 000 Hz, mono. The mime type is `audio/l16; rate=24000; channels=1`. |
| Telegram delivery | The PCM goes through an optional DSP effect, then into an `ffmpeg` subprocess while it streams (libopus, 32 kbit/s, OGG container). The result is sent with `sendVoice` (multipart field `voice`, `reply_to_message_id` set to the question message). |
| Latency keys | 1. One warm Gemini client per process. 2. The httpx keep-alive is raised from 5 s to 55 s. 3. A real `models.get` at boot. 4. Keep-warm probes: Gemini every 45 s, Telegram `getMe` every 30 s. 5. Telegram sockets use TCP keep-alive and try IPv4 first. 6. Streaming TTS, with Opus encoding during synthesis. 7. Prefetch at answer time. 8. An exact-text audio cache. 9. The text answer never waits for the voice note. |
| Final cold numbers (measured 2026-10-02, after ~1.5 h idle) | Text answer sent in **1.06 s**. Voice note delivered in **2.06 s** end to end inside the voice process (`send_voice_ms=770`). |

---

## 2. Architecture at a glance

Leda runs as two local Python processes:

- **Presentation process** (`local_presentation.py`, port 5057): the Telegram bots, the answer logic and the token store.
- **Voice process** (`voice_service.py`, port 5056): every Gemini call, the DSP, ffmpeg, and Telegram voice delivery.

They talk over loopback HTTP. A small payload is handed over through a single-use bearer token: the caller mints the token, the voice process resolves it with one loopback GET. You may collapse both processes into one. The Gemini-related patterns do not depend on the split.

```
Telegram voice note (question)                        Telegram chat
        |                                                    ^   ^
        v                                                    |   | sendVoice (OGG/Opus, reply_to)
[Presentation 5057]                                          |   |
  1 validate duration/size from the update (no download)     |   |
  2 getFile + bounded download (<= 5 MB)                     |   |
  3 mint token(audio b64, mime, extra terms)                 |   |
  4 POST /internal/leda/voice-transcription  --------->  [Voice 5056]
                                                           5 GET token payload back (loopback)
                                                           6 Gemini STT: generate_content(gemini-3.8-flash)
  7 <------------------ {"transcript": "..."} ------------
  8 answer locally (no Gemini) -> sendMessage(text) -------------+
  9 enqueue voice reply (per-chat FIFO, max 3), background thread
 10 POST /internal/leda/channel-b/telegram-voice-reply --> [Voice 5056]
                                                           11 spawn ffmpeg encoder; start "record_voice" every 4 s
                                                           12 exact-text cache? hit -> replay PCM
                                                           13 miss -> generate_content_stream(gemini-3.8-flash-lite-tts)
                                                              each chunk: s16le assemble -> DSP -> ffmpeg stdin
                                                           14 close ffmpeg stdin, collect OGG -> sendVoice
HMI browser <---- POST /leda/speak-live: chunked PCM s16le 24 kHz mono (same generator, step 13)
```

Code anchors:

- Voice process routes: `voice_service.py:1189` (`/leda/speak-live`), `:1244` (`/internal/leda/prefetch`), `:1304` (Channel B voice reply), `:1334` (transcription).
- Boot: `voice_service.py:1433-1444`.
- The Channel B bot's message handler: `local_presentation.py:1088-1147`.

---

## 3. Speech-to-text (voice-note questions)

### 3.1 Pipeline, in order

1. **Gate before any download.** Telegram reports `voice.duration` (whole seconds) and sometimes `voice.file_size` on the update itself (`local_presentation.py:1158-1170`).
   - `validate_voice_note_duration` rejects a missing or non-positive value, and any value **`>= 30`** (`voice_transcription.py:115-127`). Telegram rounds down, so a note reported as 30 lasts 30.0–30.9 s. A bug fix of 2026-09-27 changed the check from `>` to `>=` (`odd/tasks/pw-013-voice-note-questions.md:326-329`).
   - `validate_voice_note_size` rejects a reported size above `MAX_VOICE_NOTE_FILE_SIZE_BYTES = 5_000_000` (`voice_transcription.py:31,130-144`). A missing size passes this check.
2. **Bounded download.** First `getFile` (timeout 20 s), then a streaming GET of `{api_base}/file/bot{token}/{file_path}`. The download uses 64 KiB chunks and aborts once more than 5 MB arrive. It also rejects any `..` segment in `file_path` (`local_presentation.py:1171-1215`).
3. **No conversion.** The OGG/Opus bytes go to Gemini unchanged. The mime type is Telegram's `voice.mime_type`, or `audio/ogg` when it is missing (`voice_transcription.py:57`, `local_presentation.py:1159`). There is no ffmpeg on the STT path.
4. **Vocabulary hints** (`extra_terms`). These are the active screen's `machine.name` and `screen.ownerNodeName`, deduplicated and capped at 4 (`local_presentation.py:181-206`). Live evidence: a machine name was misheard as two different spellings, so the fixed list alone was not enough (F7, `odd/tasks/live-test-2026-09-25-runtime.md:62-70`).
5. **Gemini call** (`voice_transcription.py:171-214`):

   ```python
   part = genai.types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
   config = genai.types.GenerateContentConfig(
       thinking_config=genai.types.ThinkingConfig(thinking_budget=0),
       temperature=0,
       max_output_tokens=128,
   )
   response = client.models.generate_content(
       model="gemini-3.8-flash", contents=[prompt, part], config=config)
   text = response.text  # stripped; blank -> "empty" error
   ```

6. **Prompt** (`build_transcription_prompt`, `voice_transcription.py:147-168`). It is in Spanish, because the users speak Spanish. It asks for a faithful transcription of a question to a read-only industrial assistant. It lists the domain terms to favour (fixed list at `:65-78`, plus `extra_terms`, deduplicated in order). It asks for "only the transcribed text, with no comments or extra formatting". A bare-string `extra_terms` is treated as one term, never split into characters (`:155-157`).
7. **Use the transcript as the question.** **The transcript is never echoed back to the user.** It simply replaces the message text, and the normal text-answer path runs (`local_presentation.py:1126-1131`; product rule in `odd/tasks/pw-013-voice-note-questions.md:12,21`).

### 3.2 Error mapping

| Failure | Voice process HTTP | Presentation exception | User reply (copy key in `leda_copy.py:77-101`) |
|---|---|---|---|
| Duration invalid or `>= 30` s | — (never sent) | `VoiceNoteTooLong` | `voice_note_too_long` ("La nota de voz dura más de 30 segundos…") |
| Reported size > 5 MB | — | `VoiceNoteTooLarge` | `voice_note_too_large` |
| `getFile`, download, empty file or over 5 MB while streaming | — | any exception | `voice_note_download_failed` |
| No Gemini credential | 503 `GEMINI_CREDENTIAL_UNAVAILABLE` | `VoiceTranscriptionUnavailable` | `voice_note_transcription_unavailable` |
| Gemini raised anything | 502 `VOICE_TRANSCRIPTION_UNAVAILABLE` | `VoiceTranscriptionUnavailable` | same |
| Blank `response.text` | 422 `VOICE_NOTE_TRANSCRIPT_EMPTY` | `VoiceTranscriptionEmpty` | `voice_note_transcription_empty` |
| Loopback timeout (25 s) or a non-200 status | — | `VoiceTranscriptionUnavailable` | `voice_note_transcription_unavailable` |

Sources:

- Voice side: `voice_service.py:1334-1386`.
- Presentation side: `local_presentation.py:370-434` and `:1149-1194`.
- Every provider exception becomes `VoiceTranscriptionUnavailable(...) from None` (`voice_transcription.py:209-210`). The `from None` drops the original message, which could carry provider detail.
- Every failure is logged at WARNING with `elapsed_ms` and a redacted reason (the exception type or `status_N`), never the audio, the transcript or the token.

### 3.3 Timeouts on the STT path

| Bound | Value | Where |
|---|---|---|
| Presentation → voice loopback call | 25 s | `VOICE_TRANSCRIPTION_REQUEST_TIMEOUT_SECONDS`, `local_presentation.py:176` |
| Gemini SDK request timeout (shared warm client) | 45 s | `SDK_TIMEOUT_MS`, `gemini_credentials.py:20` |
| `getFile` and the download | 20 s each | `local_presentation.py:1173,1202` |
| Token payload resolve (loopback GET) | 2 s | `voice_service.py:1043` |

> **Inconsistency, code vs comment:** `GEMINI_TRANSCRIPTION_TIMEOUT_MS = 20_000` (`voice_transcription.py:33-40`) is defined, and its comment says it is applied at the client-build call site. Nothing uses it. Transcription runs on the shared warm TTS client (`voice_service.py:1363`), whose SDK timeout is 45 s. So a stuck Gemini call can outlive the 25 s caller. **When replicating:** keep the provider timeout below the caller's timeout, for example with a per-request `http_options` or a separate STT client. That second option is an untested idea here.

### 3.4 Measured STT numbers

| Date | Condition | Result | Source |
|---|---|---|---|
| 2026-09-25 | Warm, no generation config | median **2292 ms** | F7 benchmark, `odd/tasks/live-test-2026-09-25-runtime.md:224-233` |
| 2026-09-25 | Warm, `thinking_budget=0, temperature=0, max_output_tokens=128` | median **1224 ms**, same accuracy | same |
| 2026-09-25 | Cold first call, either config | ~2.3 s | same |
| 2026-09-25 | First live transcription after boot, before the boot warm-up made a real network call | **~30 s** (versus ~3 s later). It exceeded the 25 s caller timeout. | F2, `odd/tasks/live-test-2026-09-25-runtime.md:136-146` |
| 2026-09-25 | Live, both channels, after the fixes | 1–3 s | `odd/tasks/pw-013-voice-note-questions.md:320-324` |

The F7 benchmark used 5 synthesized Spanish questions and `google-genai` 2.17.0. It also confirmed that `gemini-3.8-flash-lite` (without `-tts`) does **not** exist: the call returned 404.

---

## 4. Text-to-speech and delivery

### 4.1 The Gemini TTS call

The model and voice constants are at `voice_service.py:78-82`:

- `TTS_MODEL = "gemini-3.8-flash-lite-tts"`
- `VOICE = "Leda"`
- `SAMPLE_RATE = 24000`, `CHANNELS = 1`, `SAMPLE_WIDTH = 2`

The config and the calls are at `voice_service.py:589-610`:

```python
config = types.GenerateContentConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Leda"))))
stream = client.models.generate_content_stream(
    model="gemini-3.8-flash-lite-tts", contents=text, config=config)   # streaming
response = client.models.generate_content(
    model="gemini-3.8-flash-lite-tts", contents=text, config=config)   # fallback
```

**Design: send the plain text.**

- `contents` is the answer text, with no style prompt. This model reads its input as a verbatim transcript by default.
- The earlier model, `gemini-3.1-flash-tts-preview` with the Interactions API, needed a 45-line prompt to stop it from paraphrasing. It was also slower.
- The switch was a user decision on 2026-09-23 (`odd/tasks/pw-006-leda-responsiveness.md:444-456`).
- A style annotation (`speech_metadata.style`) is reachable only through raw REST. `google-genai` 2.17 rejects that annotation type (same source).

### 4.2 Reading the stream

Code: `voice_service.py:619-685`.

- Each streamed chunk is a `GenerateContentResponse`. The audio is at `candidates[].content.parts[].inline_data`, and a chunk may carry zero or more audio parts.
- **The stream has no terminal "completed" event.** It just ends. If no audio arrived at all, the code raises `TTS_STREAM_AUDIO_MISSING` (`:876`).
- **Mime check** (`:642-654`):
  - Accept any `audio/l16*`.
  - Reject only an explicit `rate=` other than 24000.
  - No channel count is checked.
  - The real value, measured 2026-09-23, is `audio/l16; rate=24000; channels=1` (`odd/tasks/pw-006-leda-responsiveness.md:1457-1460`).
- **Decode** (`:657-670`). In `google-genai` 2.17, `inline_data.data` is raw `bytes`. A base64 `str` is accepted defensively.
- **Odd-byte chunks.** A chunk may end mid-sample. `S16LeChunkAssembler` carries the remainder byte to the next chunk (`:574-579`). A leftover byte at stream end is an error (`INCOMPLETE_PCM_S16LE_SAMPLE`).
- **Stall guard.** `ProviderStreamIdleGuard` closes the stream after 15 s without a chunk (`:537-571`).
- **Fallback** (`:795-803`, `:879-885`).
  - If the stream fails **before any audio was accepted**, the code makes one non-streaming `generate_content` call for the full audio.
  - If it fails after audio was accepted, it raises instead. That prevents playing a duplicated beginning.
- **Exceptions** are wrapped into closed codes such as `TTS_STREAM_PROVIDER_FAILED`, `from None` (`:685`).

### 4.3 DSP (optional, Leda-specific)

- `LedaStreamingDSP` (`voice_dsp.py:17-65`) applies a "robotic" effect: ring modulation, quantization, a metallic tone, two echoes and smooth gain normalization.
- It runs chunk by chunk, and keeps its own odd-byte carry and filter state across chunks.
- The defaults are at `voice_service.py:384`.
- You do not need it to replicate the Gemini path. If you add any per-chunk DSP, it must be **stateful across chunks**, or you will hear a click at every chunk boundary.

### 4.4 Opus encoding while streaming (`TelegramOpusStreamEncoder`)

Code: `voice_service.py:220-297`.

- **Created at job start** (`:772`), before Gemini is called. Spawning ffmpeg overlaps the TTS request.
  - **Measured:** `job_create_ms=774` for the first voice note after a restart, 1 ms afterwards (`odd/tasks/leda-first-query-warmup.md:79`).
- **ffmpeg resolution** (`:266-274`): `shutil.which("ffmpeg")` first, then `imageio_ffmpeg.get_ffmpeg_exe()` (the pinned wheel binary). If neither exists, the encoder fails with `FFMPEG_NOT_FOUND`. On Windows it is spawned with `CREATE_NO_WINDOW`.
- **Command** (`:275`):

  ```
  ffmpeg -hide_banner -loglevel error -f s16le -ar 24000 -ac 1 -i pipe:0 -vn
         -c:a libopus -b:a 32k -vbr on -compression_level 10 -application voip -f ogg pipe:1
  ```

  The bitrate can be overridden with the environment variable `LEDA_TELEGRAM_OPUS_BITRATE`.
- **Threads.**
  - One writer thread takes PCM from a bounded queue (`maxsize=32`, put timeout 1 s) and writes it to `stdin`.
  - Two reader threads drain `stdout` (the OGG) and `stderr`. Draining both pipes is mandatory: a full pipe deadlocks the process.
  - The output is capped at 16 MiB.
- **Finish** (`finish_and_get(timeout=15)`): an end sentinel closes `stdin`, then the code waits for exit (10 s, then kill) and joins the readers. A non-zero exit code becomes `FFMPEG_EXIT_<code>` with the last 500 bytes of stderr.
- **Cap.** The total PCM per job is capped at 16 MiB (`:782-788`).

### 4.5 Sending the voice note to Telegram

Code: `voice_service.py:328-381`.

```python
_telegram_post(f"{base}/bot{token}/sendVoice",
               data={"chat_id": str(chat_id), "reply_to_message_id": reply_to},  # reply_to optional
               files={"voice": (f"leda_{event_id}.ogg", ogg_bytes, "audio/ogg")},
               timeout=15)
```

- **Fallback chain:**
  1. `sendVoice` with the OGG.
  2. `sendDocument` with the same OGG (caption "Respuesta por voz de Leda").
  3. `sendDocument` with a WAV built from the PCM (`pcm_to_wav`, `:904-907`).

  Any 2xx response ends the chain. If every step fails, one WARNING line is logged.
- **Reply threading.** `reply_to_message_id` is the user's question message. Text and audio then stay paired even when questions overlap. When there is nothing to reply to, the field is omitted, not sent as null (`:343-350`).
- **One session for every send.** Every Telegram call in the voice process uses one `requests.Session` (`keepalive_session()`, `:85`) behind one lock (`:86,139-141`). That includes the keep-warm `getMe`, so a probe never overlaps a send.
- **Recording indicator** (`:300-308`). While the job runs, a thread sends `sendChatAction(action="record_voice")` every 4 s (timeout 5 s per call). It stops when delivery starts (`:374-381`).
- **Token resolution** (`:184-204`). The protected credential store, provider `"telegram"`, read with the same mtime cache as Gemini (§6), or an environment variable. A missing token cancels the job and logs a WARNING. That WARNING exists because an earlier silent cancel hid a production bug (F1, `odd/tasks/live-test-2026-09-25-runtime.md:28-36`).

### 4.6 Keeping the voice note off the text path (Channel B)

Code: `local_presentation.py:1138-1144`, `:1238-1313`.

1. The text answer is computed locally and sent with `sendMessage` **first**.
2. Only then is a voice reply enqueued, in a **per-chat FIFO**:
   - At most `CHANNEL_B_VOICE_QUEUE_MAX_PENDING = 3` items per chat (`:152`). Past that, the text is still answered, with no voice note. A WARNING is logged and the user is told nothing.
   - One daemon worker per chat processes the items in order. An item stays counted against the bound until it settles.
   - Each item: mint a token, then POST to the voice process with a 45 s timeout (`:146,328-349`). The voice process runs §4.1–4.5 synchronously for that request.
3. A voice failure never produces an error message in the chat. The text was already delivered.

### 4.7 HMI live stream (`/leda/speak-live`), as far as it explains the Gemini pattern

The same `_generate_tts_audio` generator (`voice_service.py:806-901`) serves two consumers:

- It yields post-DSP PCM chunks to a Flask streaming `Response`.
- It feeds the same chunks to the Opus encoder when a Telegram chat is attached.

Response headers (`:1143-1147`):

- `application/octet-stream`
- `X-Leda-Audio-Format: pcm_s16le`
- `X-Leda-Sample-Rate: 24000`
- `X-Leda-Channels: 1`
- `Cache-Control: no-store`
- `X-Accel-Buffering: no`, so a reverse proxy does not buffer the stream.

The browser schedules PCM blocks with an adaptive prebuffer: by default 200 ms, between 100 ms and 3 s, learned from chunk arrival jitter (`odd/tasks/leda-adaptive-voice-buffer.md:8-45`).

`AudioCoordinator` (`event_audio.py:165-226`) has one provider worker thread. It deduplicates generations by event id and buffers a finished generation for later subscribers. That buffering is what makes prefetch (§5.6) free.

### 4.8 Exact-text audio cache

Code: `voice_service.py:688-753`, used at `:813-833` and `:887`.

- **Key:** SHA-256 over this JSON: `{text, voiceConfig, model, voice, secretHash}`. `secretHash` is the hash of the currently active Gemini key, read from the warm client without resolving the key again (`gemini_credentials.py:254-259`). Key rotation therefore invalidates every entry with no explicit signal.
- **Value:** the post-DSP PCM.
- **Bounds:** an LRU of 32 entries and 64 MiB. An entry larger than the byte limit is not stored.
- **A hit** replays the PCM and still goes through Telegram delivery, with no Gemini call.
- **Measured:** HMI first chunk on a hit, 28 ms (2026-09-24, `odd/tasks/pw-006-leda-responsiveness.md:885`).

---

## 5. Latency playbook

### 5.1 Timeline of fixes and measurements

| # | Date | Change (commit) | Before | After | Source |
|---|---|---|---|---|---|
| 1 | 2026-09-23 | Baseline: new client per request, `gemini-3.1-flash-tts-preview`, Interactions API, 45-line prompt | HMI first chunk **2.3–6.7 s** | — | `odd/tasks/pw-006-leda-responsiveness.md:333-338` |
| 2 | 2026-09-23 | Standalone benchmark (outside the runtime) | old model TTFB median **1.31 s** (0.89–1.71 s, 6 runs) | `gemini-3.8-flash-lite-tts` + `generate_content_stream`: **0.61 s** | same, `:354-356`, `:444-447` |
| 3 | 2026-09-23 | Warm client (`98b2f1b`), cache (`691ab1d`), prefetch (`b9cfc04`), model switch (`bd10a52`) | — | Smoke test of the real helpers: first audio **0.62 s** and **0.70 s** (for 3.4 s and 7.1 s of audio) | same, `:1456-1460` |
| 4 | 2026-09-24 | Live runtime measurement | protected credential read **581–604 ms** on every request; Gemini TTFB **1311–1486 ms**; first chunk on a miss 1958–2132 ms; on a hit 619–656 ms | — | same, `:566-574` |
| 5 | 2026-09-24 | mtime-cached secret (`5411978`) | ~590 ms per read (the Windows ACL check spawns a PowerShell process) | 0 ms when cached | `gemini_credentials.py:65-82`; `pw-006…md:595-605` |
| 6 | 2026-09-24 | httpx keep-alive 5 s → 55 s (`74cf145`) | call after a 7 s idle gap: **1335 ms** | same gap: **559 ms** | `gemini_credentials.py:21-34`; `pw-006…md:606-632` |
| 7 | 2026-09-24 | Result after 5 and 6 | — | server first chunk **482–762 ms** (first request 1358 ms); hit 28 ms; credential 0 ms | `pw-006…md:884-886` |
| 8 | 2026-09-25 | Boot warm-up makes a real `models.get` (F2) | first STT after boot **~30 s** | ~3 s | `odd/tasks/live-test-2026-09-25-runtime.md:136-146` |
| 9 | 2026-09-25 | STT config `thinking_budget=0` and others (F7) | warm STT median 2292 ms | **1224 ms** | §3.4 |
| 10 | 2026-10-02 | Measurement after long idle (W2) | see §5.2 | — | `odd/tasks/leda-first-query-warmup.md:67-80` |
| 11 | 2026-10-02 | Keep-warm loops (`4d79686`), TCP keep-alive (`5e07229`), IPv4 first (`144fa17`) | voice `send_voice_ms` **4.5–5.3 s** cold; text up to **20.9 s** cold | text **1.06 s**, voice **2.06 s** cold | same, `:86-123` |

Fix 6, the httpx keep-alive, in detail:

- httpx's default `keepalive_expiry` is 5 s. `google-genai` never overrides it.
- So any gap longer than 5 s between Gemini calls meant a fresh TCP and TLS handshake, even with a warm client object.
- Fix: pass `client_args={"limits": httpx.Limits(max_keepalive_connections=20, keepalive_expiry=55.0)}`.

### 5.2 The 2026-10-02 investigation (first question after idle)

**Symptom.** The first Channel B question after idle or a restart was slow. The next ones were fast.

**Step 1: per-stage timing.** Redacted timing lines were added in both processes (§7). Live measurement W2:

| Question | Idle before | Text total | Voice total | `gemini_ttfb_ms` | `send_voice_ms` |
|---|---|---|---|---|---|
| 1 | ~32 min | 391 ms | 7619 ms | 816 | **5300** |
| 2 | ~16 min | 938 ms | 6995 ms | 754 | **4531** |
| 3 | 33 s | 384 ms | 2781 ms | 542 | 838 |
| 4 | 52 s | 391 ms | 1145 ms | cache hit | 1056 |

What this showed:

- **Gemini was not the cause.** Its time to first byte was 0.8 s cold against 0.5 s warm, which refuted the main hypothesis.
- **The cost was in Telegram `sendVoice`:** 4.5–5.3 s cold.

**Step 2: first fix, the keep-warm loops** (`keep_warm.py`):

- `getMe` every 30 s on the voice process's Telegram session.
- `models.get` every 45 s on the warm Gemini client. 45 s is below the 55 s keep-alive, and a test enforces that.

Re-check W4 after ~11 min idle:

| Metric | Cold | Warm |
|---|---|---|
| Voice `send_voice_ms` | 762 | 769 |
| Voice total | 2094 | 2847 |
| Presentation `text_send_ms` | **20932** | 382 |

The voice path was fixed, but the text was now 21 s cold.

**Step 3: TCP keep-alive** on every Telegram session (`http_keepalive.py:33-51`): `SO_KEEPALIVE=1`, `TCP_KEEPIDLE=20`, `TCP_KEEPINTVL=10`, `TCP_KEEPCNT=3`. It did not help: the second attempt still measured `text_send_ms=20908`.

**Step 4: root cause, measured.**

- IPv6 to api.telegram.org fails intermittently from the deployment network. Connect probes: IPv4 succeeded 6 of 6 (~235 ms); IPv6 timed out 1 of 6.
- urllib3 dials addresses in `getaddrinfo` order, IPv6 first. A **new** connection that hits the bad IPv6 path waits the **whole connect timeout** before falling back: 20 s for `sendMessage`, 5 s for `sendChatAction`/`getMe`.
- This also explains the earlier 4.5–5.3 s voice delays.

**Step 5: fix.** A connection class that dials IPv4 first, then IPv6 (`http_keepalive.py:66-121`). It is mounted only on the application's own Telegram sessions. Nothing process-wide is patched.

**Final result** (W4 passed, 2026-10-02 18:19, after ~1.5 h idle):

| Metric | Cold | Warm follow-up |
|---|---|---|
| Text `text_send_ms` | **1060** (was 20908) | 373 |
| Voice `total_ms` | **2057** (was ~7000) | 2004 |
| Voice `send_voice_ms` | **770** | — |

Other measurements from the same day:

- A connection probe without credentials: DNS 38 ms; TCP connect ~235 ms on both families; TLS ~235 ms; a fresh `requests` session GET ~1.5 s.
- After the IPv4 fix: 5 of 5 public GETs used IPv4, 1521–1618 ms each with a fresh session.
- Boot warm-up logged `outcome=ok elapsed_ms=2024`.

### 5.3 Warm Gemini client (`WarmGeminiClient`)

Code: `gemini_credentials.py:207-259`.

- One SDK client per process, reused by every request.
- `get(secret)` hashes the freshly resolved secret with SHA-256. On a mismatch it builds a new client and closes the old one.
- It is thread-safe with a double-checked rebuild: if two threads race to rebuild, the losing candidate is closed, so there are never two live clients.
- Only the hash is kept, never the secret.
- The client is **never closed per request.** Only the per-request stream is closed (`voice_service.py:839-842`, `:899-901`).

### 5.4 Boot warm-up with a real network call

Code: `voice_service.py:1398-1430`.

- Building `genai.Client` opens **no** connection, because httpx connects lazily.
- So the boot thread calls `client.models.get(model=TTS_MODEL)`. That is a metadata lookup: it generates nothing and uses no generation quota. It opens the TCP and TLS connection while nobody is waiting.
- It runs best-effort on a daemon thread. A failure logs the stage (`credential`, `client` or `connect`) and the exception **type** only.

> `WarmGeminiClient.warm_up()` (`gemini_credentials.py:261-274`) only builds the object. Only tests call it now. Production uses the function above. Do not copy `warm_up` as your warm-up.

### 5.5 Keep-warm loops

Code: `keep_warm.py:23-66`, wired at `voice_service.py:1438-1440`.

| Target | Probe | Interval | First probe |
|---|---|---|---|
| Telegram | `GET /bot{token}/getMe`, timeout 5 s, same session and lock as the sends | 30 s | at boot (`probe_first=True`) |
| Gemini | `client.models.get(model=TTS_MODEL)` on the warm client; the key is resolved again on every cycle | 45 s (must stay < 55 s) | after 45 s |

- A probe returns `False` when there is no credential, and then nothing is sent.
- Log lines appear only on state changes (`failed` with the exception type, then `recovered`), never once per probe.

### 5.6 Prefetch: start TTS before anyone asks for audio

Code: `local_presentation.py:284-316`, `voice_service.py:1244-1301`.

1. Right after the answer event is published, the presentation process POSTs `/internal/leda/prefetch` on a background thread (timeout 3 s, never awaited, never retried).
2. The voice process subscribes to the generation, which starts Gemini, then closes the subscription at once.
3. The later real `/leda/speak-live` request attaches to the in-flight or buffered generation instead of starting a new one.

Measured (2026-09-25):

- HMI voice-event-received → playback-started: **0.1–0.2 s** with prefetch (first readable audio 15–80 ms).
- Without prefetch: 0.6–0.9 s (first readable audio 520–760 ms).
- Source: `odd/tasks/channel-a-voice-note-ux.md:18-25`.

### 5.7 Decoupling voice from the text answer

- Channel B sends the text first and the voice note later (§4.6). This is why the text stays under ~1 s even when the voice path is cold.
- **Measured:** W2 text totals were 384–938 ms, while voice totals reached 7.6 s.
- Channel A (the HMI) answers with voice. There, a voice note goes through 1.5–4.5 s from arrival to speech, of which download plus transcription is ~1–3 s (`odd/tasks/channel-a-voice-note-ux.md:21-25`).

---

## 6. Credentials and resilience

### 6.1 Resolving the Gemini API key

Code: `gemini_credentials.py:85-163`.

- **Source selection:**
  - If `LEDA_CREDENTIAL_MASTER_KEY_FILE` is non-blank, the source is **protected**: an encrypted SQLite credential store, provider `"gemini"`.
  - Otherwise the source is **environment**: `GEMINI_API_KEY`.
  - Protected mode **never falls back** to the environment (`services/leda-runtime/README.md:209-212`).
- **mtime cache** (protected mode only).
  - The resolved secret is kept in memory, together with the `st_mtime_ns` of the credential database.
  - Every `resolve()` does one `os.stat()`. The cache is served only if the mtime is unchanged.
  - If the stat fails or the mtime changed, the code reads the store again: it fails safe. A failed resolve is never cached.
  - Why: an uncached read cost ~590 ms on Windows (§5.1 row 5).
  - It works across processes: the admin process writes the same file, so the file's mtime is the change signal.
- **Errors:**
  - `GeminiCredentialUnavailable("GEMINI_CREDENTIAL_UNAVAILABLE")`: the store failed.
  - `GeminiCredentialUnavailable("GEMINI_CREDENTIAL_MISSING")`: blank value.
  - Routes map both to HTTP 503 (`voice_service.py:491-492`).
- **Rotation.** The next resolve returns the new key. `WarmGeminiClient` sees a different hash and rebuilds. The audio cache key changes with it (§4.8). No restart and no inter-process signal are needed.
- **Telegram token.** Same pattern: `TelegramCredentialResolver`, provider `"telegram"` (`telegram_credentials.py:17-107`).

### 6.2 Verifying a key

`GeminiVerificationService` (`gemini_credentials.py:287-360`):

- It calls `client.models.get(model=GEMINI_VERIFY_MODEL)` with a 10 s timeout. `GEMINI_VERIFY_MODEL` must equal the TTS model, and a test guards that.
- `google.genai.errors.ClientError` → `invalid_key`. Any other error → `unreachable`.
- No generation, no quota used, and the result is never persisted.

### 6.3 Timeouts and bounds (voice process)

| Item | Value | Where |
|---|---|---|
| Gemini SDK timeout | 45 000 ms | `gemini_credentials.py:20` |
| Gemini verify timeout | 10 000 ms | `:37` |
| Gemini httpx keep-alive | 55 s, 20 connections | `:34,184-189` |
| TTS stream idle guard | 15 s | `voice_service.py:538` |
| ffmpeg finish / wait / kill | 15 s / 10 s / 3 s | `:248,290-292` |
| `sendVoice` / `sendDocument` | 15 s | `:354,360,365` |
| `sendChatAction`, `getMe` | 5 s | `:157,212` |
| PCM per job, OGG output | 16 MiB each | `:784`, `:260` |
| HMI coordinator queue / job / idle | 30 s / 60 s / 15 s | `event_audio.py:182-184` |
| Channel B request (presentation → voice) | 45 s | `local_presentation.py:146` |

### 6.4 Never log secrets

- Telegram URLs contain the bot token (`/bot{token}/…`). A `requests` exception message can therefore contain the token. The code logs **exception types only** and re-raises closed codes `from None`.
- Timing lines go through a sanitizer (§7) that writes `redacted` for any value that is not an int, a bool or a short token.
- The Gemini key never appears in a log. Only its SHA-256 is kept in memory, by the warm client.
- An access-log filter removes query strings from Werkzeug access lines (`install_access_log_query_redaction`, `voice_service.py:1436`).

### 6.5 No automatic retries on Telegram POSTs (design)

- The sessions mount no urllib3 `Retry`.
- Reason: urllib3 retries a dead pooled socket as a read error. For a non-idempotent `sendVoice` or `sendMessage`, that can deliver the message twice (`voice_service.py:144-151`, `http_keepalive.py:1-12`).
- Keeping connections warm is the chosen fix instead.

---

## 7. Observability: the redacted timing logs

`timing_log.py` provides:

- A dedicated logger `leda_runtime.timing`: INFO level, `propagate=False`, its own stderr handler, installed once per process. Format: `%(asctime)s %(message)s`.
- One line per unit of work: `<label> key=value …`.
  - Keys match `[a-z][a-z0-9_]{0,39}`.
  - Values are written only if they are ints, bools or `[A-Za-z0-9_]{1,40}` tokens; anything else becomes `redacted`.
  - Emitting a line never raises (`timing_log.py:29-30,51-75`).
- `StageTimer` (`:82-119`) accumulates `<stage>_ms` fields and emits one line with `total_ms`.

| Line | Process | Fields and meaning |
|---|---|---|
| `Leda Channel B timing:` | presentation | `outcome`, `telegram_lag_s` (now minus Telegram's message `date`), `status_ms`, `download_ms`, `transcription_ms` (voice notes only), `answer_ms`, `text_send_ms`, `voice_enqueue_ms`, `total_ms` |
| `Leda Channel B voice request timing:` | presentation | `queue_wait_ms`, `mint_ms`, `voice_request_ms` (the whole voice-process round trip), `http_status`, `total_ms` |
| `Leda Channel B voice timing:` | voice | `outcome` (`sent`, `send_failed` or `error`), `job_create_ms` (includes the ffmpeg spawn), `gemini_client_reused`, `gemini_ttfb_ms`, `tts_total_ms`, `opus_finish_ms`, `send_voice_ms`, `total_ms`. The `gemini_*` fields are absent on a cache hit. |
| `Leda Gemini warm-up:` | voice | `outcome=ok elapsed_ms`, or `outcome=failed stage=… error_type=…` |
| `Leda keep-warm:` | voice | `target`, `interval_s` at start; then `outcome=failed error_type`, or `outcome=recovered` |

Sources: `odd/tasks/leda-first-query-warmup.md:56-63`, `voice_service.py:1091-1108`.

**How to read them:**

1. A large `text_send_ms` while the voice lines look normal means the problem is the Telegram connection, not Gemini.
2. A `send_voice_ms` far above ~0.8 s means a cold Telegram socket, often an IPv6 connect timeout.
3. If `gemini_ttfb_ms` is above ~1.2 s, check `gemini_client_reused`. `false` means a rebuild (rotation or first use). `true` with a high value suggests the keep-alive expired.
4. The token-resolve loopback has no stage of its own. It is the gap between `voice_request_ms` and the voice line's `total_ms`.
5. Lines from the two processes are correlated by their timestamps.

Other per-request INFO lines in `voice_service.py`, invisible unless INFO is enabled for that logger:

- `Leda Gemini client: resolve_elapsed_ms build_elapsed_ms reused`
- `Leda Gemini TTS: time_to_first_byte_ms`
- `first_yield_processing_elapsed_ms`
- `Leda speak-live: first_chunk_elapsed_ms`, `stream_end_elapsed_ms`, `event_publish_to_received_ms`

> **Known mislabel** (review follow-up `R3-document-fallback-mislabel`). `outcome=sent` is recorded only when `sendVoice` itself returns 2xx (`voice_service.py:353-357`). A delivery that succeeded through the `sendDocument` fallback is reported as `send_failed`.

---

## 8. Replication recipe

### 8.1 Dependencies (exact pins used here)

From `services/leda-runtime/requirements.in`:

```
google-genai==2.17.0
httpx==0.28.1
requests==2.34.2
imageio-ffmpeg==0.6.0      # bundled ffmpeg fallback
Flask==3.1.3               # only if you expose HTTP routes
cryptography==50.0.1       # only for an encrypted credential store
```

Relevant transitive pins from `requirements.lock.txt`: `urllib3==2.7.0`, `httpcore==1.0.9`, `h11==0.16.0`, `pydantic==2.13.5`, `google-auth==2.57.0`, `certifi==2026.7.22`, `anyio==4.14.2`, `tenacity==9.1.4`, `websockets==16.1.1`.

The IPv4-first adapter relies on urllib3 2.7 internals (`_new_conn`, `_dns_host`). Check it again on every urllib3 upgrade.

**SDK surface verified against the installed `google-genai` 2.17.0** (`services/leda-runtime/.venv`):

- `genai.Client(api_key=..., http_options=types.HttpOptions(timeout=<ms:int>, client_args={...}))`. `timeout` is in **milliseconds**, and `client_args` goes to `httpx.Client(**client_args)`.
- `types.Part.from_bytes(*, data, mime_type)`
- `types.ThinkingConfig(thinking_budget=...)`
- `types.GenerateContentConfig(response_modalities, speech_config, thinking_config, temperature, max_output_tokens)`
- `types.SpeechConfig(voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=...)))`
- `client.models.generate_content(*, model, contents, config)`
- `client.models.generate_content_stream(*, model, contents, config)`. It returns an iterator of `GenerateContentResponse`, which can be closed.
- `client.models.get(*, model)`
- `client.close()`
- `google.genai.errors.ClientError`

### 8.2 Step by step

1. **Client factory with a long keep-alive** (from `gemini_credentials.py:166-191`):

   ```python
   import hashlib, threading, httpx
   from google import genai
   from google.genai import types

   SDK_TIMEOUT_MS = 45_000
   KEEPALIVE_EXPIRY_S = 55.0

   def create_gemini_client(api_key: str, timeout_ms: int = SDK_TIMEOUT_MS):
       return genai.Client(
           api_key=api_key,
           http_options=types.HttpOptions(
               timeout=timeout_ms,
               client_args={"limits": httpx.Limits(
                   max_keepalive_connections=20, keepalive_expiry=KEEPALIVE_EXPIRY_S)},
           ),
       )
   ```

2. **One warm client, rebuilt when the key changes** (from `gemini_credentials.py:207-252`):

   ```python
   class WarmGeminiClient:
       def __init__(self):
           self._lock = threading.Lock(); self._client = None; self._hash = None
       def get(self, api_key: str):
           digest = hashlib.sha256(api_key.encode()).hexdigest()
           with self._lock:
               if self._client is not None and self._hash == digest:
                   return self._client
           candidate = create_gemini_client(api_key)
           with self._lock:
               if self._client is not None and self._hash == digest:
                   candidate.close(); return self._client
               stale, self._client, self._hash = self._client, candidate, digest
           if stale is not None:
               try: stale.close()
               except Exception: pass
           return candidate
       def secret_hash(self):
           with self._lock: return self._hash
   ```

   Resolve the key on every request (cheaply, see §6.1), then call `warm.get(key)`.

3. **Boot warm-up and keep-warm loop** (from `voice_service.py:1398-1440`, `keep_warm.py:28-54`):

   ```python
   TTS_MODEL = "gemini-3.8-flash-lite-tts"

   def gemini_probe():
       warm.get(resolve_key()).models.get(model=TTS_MODEL)   # no generation, no tokens

   def keep_warm(probe, interval_s, stop: threading.Event, probe_first=False):
       first = probe_first
       while True:
           if first: first = False
           elif stop.wait(interval_s): return
           try: probe()
           except Exception as e: log_type_only(e)   # never the message

   threading.Thread(target=gemini_probe, daemon=True).start()                     # boot: opens TCP+TLS
   threading.Thread(target=keep_warm, args=(gemini_probe, 45.0, stop), daemon=True).start()
   threading.Thread(target=keep_warm, args=(telegram_getme_probe, 30.0, stop),
                    kwargs={"probe_first": True}, daemon=True).start()
   ```

4. **Telegram session: TCP keep-alive, IPv4 first, no retries.** Copy `http_keepalive.py` as a whole (133 lines). It is self-contained, and it is the part most easily gotten wrong. Its pieces:
   - `keepalive_socket_options()`: urllib3's default options plus `SO_KEEPALIVE` and the `TCP_KEEP*` options, each guarded by `hasattr`.
   - `_IPv4FirstMixin._new_conn`: it resolves the host, tries every IPv4 address, then every IPv6 address, by swapping `self._dns_host`. `self.host` stays unchanged, so SNI and certificate checks still use the hostname.
   - `KeepAliveHTTPAdapter.init_poolmanager`: it sets `socket_options` and `poolmanager.pool_classes_by_scheme`.
   - `keepalive_session()`: `requests.Session()` with the adapter mounted for `http://` and `https://`.

   Use **one** session plus **one** lock for every voice-delivery call and its keep-warm probe.

5. **STT** (from `voice_transcription.py:115-214`):

   ```python
   MAX_SECONDS, MAX_BYTES = 30, 5_000_000

   def precheck(voice: dict):               # Telegram update's message["voice"]
       d, size = voice.get("duration"), voice.get("file_size")
       if not isinstance(d, int) or isinstance(d, bool) or d <= 0 or d >= MAX_SECONDS: raise TooLong()
       if size is not None and (not isinstance(size, int) or size < 0 or size > MAX_BYTES): raise TooLarge()

   def transcribe(client, audio: bytes, mime: str | None, terms: list[str]) -> str:
       prompt = build_prompt(terms)          # "transcribe faithfully, favour these terms, return only the text"
       part = types.Part.from_bytes(data=audio, mime_type=mime or "audio/ogg")
       cfg = types.GenerateContentConfig(
           thinking_config=types.ThinkingConfig(thinking_budget=0),
           temperature=0, max_output_tokens=128)
       try:
           r = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, part], config=cfg)
       except Exception:
           raise TranscriptionUnavailable() from None
       text = (r.text or "").strip() if isinstance(r.text, str) else ""
       if not text: raise TranscriptionEmpty()
       return text                           # use as the question; never echo it back
   ```

   Download with `stream=True` and abort once the byte count passes `MAX_BYTES` (`local_presentation.py:1196-1215`).

6. **TTS stream with chunk assembly and fallback** (from `voice_service.py:589-685`, `:795-803`, `:835-901`):

   ```python
   SAMPLE_RATE, SAMPLE_WIDTH = 24_000, 2

   def tts_config():
       return types.GenerateContentConfig(
           response_modalities=["AUDIO"],
           speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
               prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Leda"))))

   def audio_parts(resp):
       for c in resp.candidates or []:
           for p in (c.content.parts if c.content else None) or []:
               if p.inline_data is not None and p.inline_data.data:
                   yield p.inline_data

   def pcm_of(inline):
       mime = (inline.mime_type or "").lower()
       if mime and not mime.startswith("audio/l16"): raise FormatError()
       if "rate=" in mime and f"rate={SAMPLE_RATE}" not in mime.replace(" ", ""): raise FormatError()
       data = inline.data
       return bytes(data) if isinstance(data, (bytes, bytearray)) else base64.b64decode(data, validate=True)

   def stream_pcm(client, text):
       carry, got_audio, stream = b"", False, None
       try:
           stream = client.models.generate_content_stream(model=TTS_MODEL, contents=text, config=tts_config())
           for chunk in stream:                      # add a 15 s idle watchdog that calls stream.close()
               for inline in audio_parts(chunk):
                   got_audio = True
                   data = carry + pcm_of(inline)
                   cut = len(data) // SAMPLE_WIDTH * SAMPLE_WIDTH
                   carry = data[cut:]
                   if cut: yield data[:cut]
           if carry: raise FormatError("odd trailing byte")
           if not got_audio: raise ProviderError("no audio")
       except (FormatError, GeneratorExit): raise
       except Exception:
           if got_audio: raise ProviderError() from None   # never restart mid-utterance
           full = client.models.generate_content(model=TTS_MODEL, contents=text, config=tts_config())
           yield b"".join(pcm_of(i) for i in audio_parts(full))
       finally:
           if stream is not None:
               try: stream.close()
               except Exception: pass
   ```

   The rate check above is a simplification. The real code parses the `rate=` parameter as an integer (`voice_service.py:633-654`).

7. **Opus encoder fed while streaming** (from `voice_service.py:220-297`):

   ```python
   import shutil, subprocess, sys, threading

   def ffmpeg_path():
       path = shutil.which("ffmpeg")
       if path: return path
       import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()

   def start_encoder():
       cmd = [ffmpeg_path(), "-hide_banner", "-loglevel", "error",
              "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", "pipe:0", "-vn",
              "-c:a", "libopus", "-b:a", "32k", "-vbr", "on", "-compression_level", "10",
              "-application", "voip", "-f", "ogg", "pipe:1"]
       flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
       p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, bufsize=0, creationflags=flags)
       out, err = [], []
       def drain(s, sink):
           for b in iter(lambda: s.read(8192), b""): sink.append(b)
       readers = [threading.Thread(target=drain, args=(p.stdout, out), daemon=True),
                  threading.Thread(target=drain, args=(p.stderr, err), daemon=True)]
       for t in readers: t.start()
       return p, out, err, readers

   # spawn BEFORE calling Gemini; write each PCM chunk to p.stdin as it arrives
   # (from a writer thread fed by a bounded queue, so a slow ffmpeg cannot stall streaming), then:
   def finish(p, out, readers, timeout=15):
       p.stdin.close()
       code = p.wait(timeout=timeout)
       for t in readers: t.join(timeout=2)
       return b"".join(out) if code == 0 else None
   ```

   Cap both the PCM fed in and the OGG read out (16 MiB each here).

8. **Send it** (from `voice_service.py:328-371`):

   ```python
   def send_voice(session, lock, base, token, chat_id, ogg, reply_to=None):
       data = {"chat_id": str(chat_id), **({"reply_to_message_id": reply_to} if reply_to else {})}
       with lock:
           r = session.post(f"{base}/bot{token}/sendVoice", data=data,
                            files={"voice": ("answer.ogg", ogg, "audio/ogg")}, timeout=15)
       if 200 <= r.status_code < 300: return True
       # fallback: sendDocument(ogg), then sendDocument(wav built from the PCM)
   ```

   While synthesizing, send `sendChatAction` with `action="record_voice"` every 4 s and stop it before the upload.

9. **Orchestration rules:**
   - Send the text answer first. Then enqueue the voice job in a per-chat FIFO (maximum 3 pending) on a background worker.
   - Start TTS at answer time (prefetch). Do not wait for the consumer to ask for the audio.
   - Put an exact-text cache in front of TTS. Key it on the text, the voice and DSP settings, the model, the voice name and the key hash.

10. **Logging:** add one redacted per-stage timing line per job, on a dedicated logger (§7), before you start tuning anything.

### 8.3 Configuration constants

| Constant | Value | Source |
|---|---|---|
| TTS model / voice | `gemini-3.8-flash-lite-tts` / `Leda` | `voice_service.py:78-79` |
| STT model | `gemini-3.8-flash` | `voice_transcription.py:33` |
| PCM format | s16le, 24 000 Hz, mono | `voice_service.py:80-82` |
| STT config | thinking 0, temperature 0, max output tokens 128 | `voice_transcription.py:50-52` |
| Voice-note limits | `< 30` s (reported), `<= 5 000 000` bytes | `voice_transcription.py:27,31` |
| Extra STT terms | at most 4 | `local_presentation.py:181` |
| SDK timeout / verify timeout | 45 000 ms / 10 000 ms | `gemini_credentials.py:20,37` |
| httpx keep-alive | 55 s, 20 connections | `gemini_credentials.py:34` |
| Keep-warm intervals | Telegram 30 s, Gemini 45 s | `keep_warm.py:23,25` |
| TCP keep-alive | idle 20 s, interval 10 s, count 3 | `http_keepalive.py:33-37` |
| Opus | libopus 32k VBR, compression 10, `voip`, OGG | `voice_service.py:275` |
| Recording indicator | `record_voice` every 4 s | `voice_service.py:304-306` |
| Audio cache | 32 entries / 64 MiB LRU | `voice_service.py:699` |
| Channel B voice queue | 3 pending per chat; request timeout 45 s | `local_presentation.py:146,152` |
| STT loopback timeout | 25 s | `local_presentation.py:176` |

---

## 9. Pitfalls checklist (symptom → cause → fix)

1. **Every spaced request costs ~1.3 s more than back-to-back requests.**
   - Cause: httpx `keepalive_expiry` defaults to 5 s, and `google-genai` does not override it.
   - Fix: `client_args={"limits": httpx.Limits(keepalive_expiry=55.0, ...)}`.
2. **The first call after boot is very slow (~30 s observed).**
   - Cause: building `genai.Client` opens no connection.
   - Fix: make a real `models.get` at boot on a background thread.
3. **The first call after an idle period is slow again.**
   - Cause: pooled connections expire or are silently dropped.
   - Fix: keep-warm probes inside the expiry window (Gemini 45 s < 55 s; Telegram `getMe` 30 s).
4. **Telegram send takes ~5 s or ~20 s, intermittently, then is fast.**
   - Cause: the IPv6 path is broken, and urllib3 tries IPv6 first, so it waits the whole connect timeout.
   - Fix: an IPv4-first connection class on your own sessions. Diagnose with per-family connect probes first.
5. **The first send after a long idle takes ~21 s on Windows.**
   - Cause: a NAT or firewall dropped the idle socket without sending RST, and Windows retransmits for about 21 s before giving up.
   - Fix: TCP keep-alive socket options plus application keep-warm.
6. **Duplicate voice notes.**
   - Cause: urllib3 or `requests` retries on non-idempotent POSTs.
   - Fix: no `Retry` on sessions used for `sendVoice` or `sendMessage`. Keep connections warm instead.
7. **Clicks or crashes on odd-length chunks.**
   - Cause: a stream chunk can end mid-sample.
   - Fix: carry the remainder byte, and keep any DSP stateful across chunks.
8. **"No audio" with no error.**
   - Cause: `generate_content_stream` has no completion event.
   - Fix: count audio parts and treat zero as an error.
9. **The TTS model reads the instructions aloud, or paraphrases.**
   - Cause: a prompt-wrapped input. Older preview models needed guard rails.
   - Fix: with `gemini-3.8-flash-lite-tts`, send the plain text only.
10. **STT is twice as slow as needed.**
    - Cause: default thinking and sampling.
    - Fix: `thinking_budget=0`, `temperature=0`, `max_output_tokens=128`.
11. **STT returns 404.**
    - Cause: `gemini-3.8-flash-lite` does not exist.
    - Fix: use `gemini-3.8-flash`. The `-tts` model is for speech generation only.
12. **A 30.4 s note is accepted.**
    - Cause: Telegram reports whole seconds.
    - Fix: reject `duration >= limit`, and check before downloading.
13. **Large or hostile downloads.**
    - Cause: Telegram may not report `file_size`.
    - Fix: stream the download and abort when it passes the byte cap. Reject `..` in `file_path`.
14. **A stuck STT call outlives its caller.**
    - Cause: the SDK timeout (45 s) is longer than the caller's timeout (25 s). See the §3.3 inconsistency.
    - Fix: set the provider timeout below the caller's.
15. **The provider stream hangs forever.**
    - Cause: no data and no error.
    - Fix: an idle watchdog (15 s) that calls `stream.close()`.
16. **ffmpeg hangs, or the process never exits.**
    - Cause: an undrained `stdout` or `stderr` pipe fills up.
    - Fix: one reader thread per pipe, a bounded input queue, `wait` with a timeout, then `kill`.
17. **No ffmpeg on the host.**
    - Fix: use `imageio-ffmpeg` as a fallback, and add `CREATE_NO_WINDOW` on Windows.
18. **The text reply is slow because voice synthesis is slow.**
    - Cause: the voice was on the text path.
    - Fix: send the text first, then run the voice on a background per-chat queue.
19. **A ~0.6 s penalty per request from credential reads.**
    - Cause: an encrypted store read, plus a Windows ACL check, on every call.
    - Fix: cache the key in memory, invalidated by the store file's mtime.
20. **The old key is still used after rotation.**
    - Fix: compare a hash of the freshly resolved key on every call, and include that hash in the audio cache key.
21. **The bot token leaks into the logs.**
    - Cause: the token is part of Telegram URLs, and exception messages can contain the URL.
    - Fix: log exception types only, and re-raise `from None`.
22. **Timing lines never appear.**
    - Cause: no `basicConfig`, so INFO lines are dropped by the last-resort handler.
    - Fix: a dedicated logger with its own handler and `propagate=False`.
23. **The keep-warm probe delays a real send.**
    - Cause: the probe holds the send lock for up to its 5 s timeout. This is a known open follow-up, `R3-probe-holds-send-lock`.
    - Fix: keep the probe timeout short, or skip the probe while a send is waiting. That fix is untested here.
24. **The IPv4-first fix silently stops working.**
    - Cause: it overrides urllib3 private internals (`_new_conn`, `_dns_host`), and proxied requests bypass the adapter.
    - Fix: pin urllib3, test after every upgrade, and document the proxy limitation.
25. **The warm state is lost or duplicated.**
    - Cause: multiple workers or a dev reloader.
    - Fix: one process per voice service. The service refuses `WEB_CONCURRENCY>1` and the Werkzeug reloader (`voice_service.py:1389-1395`).

---

## 10. Appendix

### 10.1 Unverified or open items

- The cost per request of `gemini-3.8-flash-lite-tts` was never measured (`odd/tasks/pw-006-leda-responsiveness.md:497-499`).
- The ~30 s cold STT case was attributed to the lazy first connection. That source states the cause was "identifiable, not fully explained by profiling alone" (`odd/tasks/live-test-2026-09-25-runtime.md:138`).
- The detailed T11 benchmark results are said to live in Engram (`odd/pw-006-leda-responsiveness/t11-benchmark`). A search on 2026-10-13 returned nothing, so only the summary numbers in the task file are reported here.
- Model availability can differ per account and region. Check both model ids with `client.models.get` before you rely on them.

### 10.2 File index

| File | Role in the voice path |
|---|---|
| `voice_service.py` | TTS, cache, Opus encoder, Telegram delivery, the STT route, boot warm-up, keep-warm wiring |
| `voice_transcription.py` | STT limits, prompt, Gemini STT call, error types |
| `gemini_credentials.py` | Key resolution and mtime cache, client factory (keep-alive), `WarmGeminiClient`, verification |
| `keep_warm.py` | Generic keep-warm loop |
| `http_keepalive.py` | TCP keep-alive and IPv4-first `requests` adapter |
| `timing_log.py` | Redacted per-stage timing logger |
| `voice_dsp.py` | Streaming PCM effect |
| `telegram_credentials.py`, `telegram_config.py` | Telegram token resolution and enablement |
| `event_audio.py` | HMI generation coordinator (dedup, buffering, prefetch attach) |
| `local_presentation.py` | Telegram bot side: voice-note gate and download, STT request, text-first answering, per-chat voice queue, prefetch trigger |
| `services/leda-runtime/requirements.in`, `requirements.lock.txt` | Pins |
| `odd/tasks/pw-006-leda-responsiveness.md`, `leda-first-query-warmup.md`, `live-test-2026-09-25-runtime.md`, `pw-013-voice-note-questions.md`, `channel-a-voice-note-ux.md`, `leda-channel-b-voice-replies.md` | Measurement history |

### 10.3 Documentation and code inconsistencies found while writing this report

1. `GEMINI_TRANSCRIPTION_TIMEOUT_MS` is unused, although its comment claims it is applied (§3.3).
2. The `voice_transcription.py:10-17` docstring still says the STT model id is "not verified against a live listing". Live use confirmed it (`odd/tasks/pw-013-voice-note-questions.md:324`; F7).
3. The `voice_service.py:3` module docstring still says "Gemini Interactions TTS". The code switched to `generate_content_stream` in T11. The function name `_create_interactions_tts_job` was kept deliberately.
4. `WarmGeminiClient.warm_up` is called only from tests. Its docstring suggests it may open the connection, which it does not (§5.4).
5. `odd/tasks/leda-first-query-warmup.md:14` cites `voice_service.py:1328` for the warm-up. It is now at `:1398`, because lines moved.
6. `docs/leda/LEDA_DOCUMENTO_MAESTRO.md` §5.3 still describes Channel B as text-only ("que no reproduce audio"). Channel B has sent voice notes since 2026-09-24 (§1.1 of the same document).
7. The `_resolve_channel_b_voice_reply_payload` and `_resolve_voice_transcription_payload` elapsed-time lines are logged at WARNING (`voice_service.py:1021,1077`). Other routine timing lines are logged at INFO, following the PW-011 M4 policy.
