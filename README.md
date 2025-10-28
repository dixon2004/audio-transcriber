# Simple Audio Transcriber

## Overview

**Simple Audio Transcriber** is a web-based application built using Streamlit that converts speech in audio and video files into text. It supports real-time, progressive transcription, handles mixed-language audio (e.g., English and Chinese), and provides timestamps for each segment.

Users can upload MP3, WAV, or MP4 files, listen to the audio, view a live transcript, and download the final transcription as a `.txt` file. The system is optimized for performance using the Faster Whisper model with caching.

Try the live app here: [Simple Audio Transcriber](https://simple-audio-transcriber.streamlit.app/)

## Approach

1. Audio Extraction & Preprocessing
    - Uploaded files are converted to mono 16 kHz WAV, which is optimal for Whisper transcription.
    - For MP4 video files, audio is extracted automatically for playback and transcription.
    - Preprocessing ensures consistent audio format for reliable results.

2. Transcription
    - Utilizes the Faster Whisper model for high-performance speech recognition.
    - Transcription is progressive, displaying segments as they are processed.
    - Each line of transcript is timestamped in [MM:SS - MM:SS] format.
    - Supports multiple languages and mixed-language audio input.

3. User Interface
    - Built with Streamlit, providing a simple, interactive, and user-friendly interface.
    - Features include:
        - File upload (MP3, WAV, MP4)
        - Audio playback of the uploaded or extracted audio
        - Progressive display of transcribed text
        - Downloadable final transcript as a `.txt` file

4. Caching & Resource Management
    - The Whisper model is cached using `@st.cache_resource` to avoid repeated loading for multiple files.
    - Temporary audio files are deleted after transcription.
    - GPU memory is managed efficiently, and the cached model persists while the app is running.

## Technologies & Tools Used

- **Python 3.12**
- **Streamlit:** Web-based interface for file upload and display
- **Faster Whisper:** High-performance Whisper model implementation
- **PyTorch:** Backend for model inference (CPU/GPU)
- **Pydub:** Audio extraction and preprocessing
- **Tempfile & OS:** Temporary file management

## Steps to Reproduce

1. Clone the repository

    ```bash
    git clone https://github.com/dixon2004/audio-transcriber.git
    cd audio-transcriber
    ```

2.	Create and activate a virtual environment

    ```bash
    python -m venv .venv
    source .venv/bin/activate      # macOS / Linux
    .venv\Scripts\activate         # Windows
    ```

3. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

4. Install FFmpeg (required for MP3/MP4 processing)

    - **macOS (Homebrew):** brew install ffmpeg
    - **Windows:** Download from FFmpeg official site and add to PATH
    - **Linux (Ubuntu/Debian):** sudo apt install ffmpeg

5. Run the Streamlit app

    ```bash
    streamlit run app.py
    ```

6. Upload a file
    - Supported formats: MP3, WAV, MP4
    - Play the audio using the play button.
    - Progressive transcription will display on the screen.
    - Download the transcript after processing.

## Notes & Recommendations

- The app automatically uses GPU if available, significantly improving transcription speed.
- Transcription speed depends on the model size: tiny → large (default: medium).
- The Whisper model remains cached while the app is running, allowing multiple files to be processed efficiently.
- Temporary audio files are cleaned up automatically to save disk space.
- The system is robust for mixed-language content, making it suitable for real-world scenarios.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.