# YouTube Frame Extractor

A modern Python-based GUI application to extract specific frames from YouTube videos at the highest available resolution and codec quality, embedding metadata and generating companion logs automatically.

---

## Purpose & Background

When citing online videos in academic research, media studies, or machine learning datasets, obtaining high-fidelity, uncompressed frames is crucial. Traditional methods (like manual screenshots) suffer from compression artifacts, incorrect resolutions, or frame offsets. 

This tool was developed to solve these issues by allowing researchers to:
1. **Extract Pristine Frames**: Download directly from raw video streams with zero quality degradation.
2. **Preserve Image Authenticity**: Keep pixels 100% untouched to avoid visual noise or watermark burn-ins that could affect analysis.
3. **Ensure Traceability**: Automate academic reproducibility by embedding source URLs, target frame indexes, timestamps, and environment software versions directly into both the PNG file header and a companion Markdown report.

---

## Features

- **Highest Quality Extraction**: Automatically queries video stream formats using `yt-dlp` and selects the highest resolution format and best codec (AV1 > VP9 > H.264).
- **Accurate seeking**: Invokes FFmpeg with hybrid seeking (fast seek to nearby keyframe followed by accurate seek) to pull the exact frame index.
- **Embedded PNG Metadata**: Saves frames as a PNG file and injects provenance metadata directly inside the PNG's `tEXt` chunks using Pillow, leaving the original pixels untouched.
- **Companion Markdown Logs**: Simultaneously outputs a detailed Markdown file matching the name of the image, recording parameters like codec, resolution, frame index, extraction timestamp, and package versions.
- **No Global Dependencies**: Works out-of-the-box using a portable FFmpeg wrapper via `imageio-ffmpeg` if system-wide FFmpeg is not installed.
- **Modern Interface**: Fluent/Material Design inspired dark-themed GUI built using `customtkinter`.

---

## Installation

Ensure you have Python 3.8 or higher installed on your system.

1. Clone or download this repository.
2. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Start the GUI by executing the entry point script:

```bash
python run.py
```

### Input Parameters

1. **YouTube URL**: The web link to the target YouTube video.
2. **Target Frame**: The target frame index number you want to extract (e.g. `500`).
3. **Output Folder**: The directory where the final PNG and Markdown files will be saved (defaults to the project folder).
4. **FFmpeg Path**: Automatically auto-detects the portable FFmpeg executable, but allows picking a custom file manually if needed.

Click **Extract Target Frame** to start. The status bar and terminal-style console will display real-time progress and logs.

---

## Embedded Metadata Schema

The extracted PNG image contains the following keys in its file headers (`tEXt` chunks):

- `Copyright`: `YouTube Video Creator`
- `Source`: YouTube Video URL
- `ExtractionFrame`: Index number of the frame
- `ExtractionTimestamp`: ISO 8601 extraction timestamp
- `ExtractionSoftware`: `YouTube Frame Extractor v1.0.0`
- `VideoTitle`: The title of the source video
- `VideoCodec`: Codec used (e.g. `vp09`, `av01`)
- `VideoResolution`: Native width and height of the video stream

---

## 日本語概要 (Japanese Description)

### 開発目的
学術研究やメディア分析において、オンライン動画から静止画フレームを引用・抽出する際、「圧縮によるノイズのないオリジナル画質で取得すること」と「引用元データのトレーサビリティ（追跡可能性）を確保すること」が極めて重要です。

本ツールは以下の要件を満たすために開発されました。
1. **ストリームからの最高画質抽出**: スクリーンショットによる画質劣化やアスペクト比のズレを防ぎ、配信されている最高の解像度およびコーデックから直接画像を切り出します。
2. **真正性（オリジナル状態）の維持**: 画像自体に透かし文字や黒帯などを焼き付けず（ピクセル無改変）、分析資料としての妥当性を担保します。
3. **トレーサビリティの自動化**: PNGファイルの電子メタデータ（`tEXt` チャンク）と、随伴するMarkdownファイルの両方に動画リンク、フレーム番号、抽出環境等の情報を自動で記録し、引用元への正確なアクセスを可能にします。

---

本プログラムは、YouTube上の任意の動画から、指定したフレーム番号の画像を最高の解像度・コーデックで正確に切り出すGUIアプリケーションです。

### 特徴
- **画像ピクセル無劣化の来歴付与**: 切り出したPNG画像のメタデータ領域（`tEXt` チャンク）に動画情報や抽出日時を直接埋め込むため、研究利用などの際に画像の見た目を損なうことがありません。
- **自動ポータブルFFmpeg**: システムにFFmpegがインストールされていない場合でも、自動的にライブラリ内のポータブルFFmpegをロードして動作します。
- **メタデータログ作成**: 画像ファイルと同時に、同じディレクトリに動画の詳細情報や使用パッケージのバージョンを記載したMarkdownファイルを出力します。

### 起動方法
```bash
pip install -r requirements.txt
python run.py
```

---

## License

This project is open-sourced under the [MIT License](LICENSE).
