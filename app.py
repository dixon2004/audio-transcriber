from faster_whisper import WhisperModel
from typing import Generator, Tuple
from pydub import AudioSegment
import streamlit as st
import tempfile
import torch
import os


MODEL_SIZE = "medium" # Options: tiny, base, small, medium, large


@st.cache_resource
def load_whisper_model() -> WhisperModel:
    """
    Load and cache the Whisper model.
    
    Returns:
        WhisperModel: Initialized Whisper model.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    
    return WhisperModel(
        model_size_or_path=MODEL_SIZE,
        device=device,
        compute_type=compute_type
    )


def extract_audio_from_file(uploaded_file) -> str:
    """
    Extract and convert audio from uploaded file to WAV format optimized for Whisper.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        
    Returns:
        str: Path to the processed WAV file.
    """
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    try:
        if file_ext == "mp4":
            audio = AudioSegment.from_file(tmp_path, format="mp4")
        elif file_ext == "mp3":
            audio = AudioSegment.from_mp3(tmp_path)
        elif file_ext == "wav":
            audio = AudioSegment.from_wav(tmp_path)
        else:
            audio = AudioSegment.from_file(tmp_path)
        
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        audio.export(output_path, format="wav")
        
        return output_path
    except Exception as e:
        raise RuntimeError(f"Failed to process audio file: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def transcribe_audio_stream(
    audio_path: str, 
    model: WhisperModel
) -> Generator[Tuple[float, float, str], None, None]:
    """
    Transcribe audio file and yield segments progressively.
    
    Args:
        audio_path: Path to audio file
        model: Whisper model instance
        
    Yields:
        Tuple[float, float, str]: (start_time, end_time, transcribed_text)
    """
    segments, _ = model.transcribe(
        audio=audio_path,
        vad_filter=True,
        beam_size=5
    )
    
    for segment in segments:
        text = segment.text.strip()
        if text:
            yield segment.start, segment.end, text


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted timestamp (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_transcript_line(start: float, end: float, text: str) -> str:
    """
    Format a single transcript line with timestamps.
    
    Args:
        start: Start time in seconds
        end: End time in seconds
        text: Transcribed text
        
    Returns:
        str: Formatted line
    """
    start_ts = format_timestamp(start)
    end_ts = format_timestamp(end)
    return f"[{start_ts} - {end_ts}] {text}"


def main() -> None:
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(
        page_title="Simple Audio Transcriber",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    st.title("🎧 Audio Transcription System")
    st.markdown("""
    Upload an audio or video file to transcribe speech to text.  
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["mp3", "wav", "mp4"],
        help="Supported formats: MP3, WAV, MP4"
    )
    
    if not uploaded_file:
        st.info("Please upload a file to begin")
        return
    
    try:
        process_file(uploaded_file)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.exception(e)


def process_file(uploaded_file) -> None:
    """
    Process and transcribe the uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    """
    model = load_whisper_model()
    audio_path = extract_audio_from_file(uploaded_file)
    
    if not uploaded_file.name.endswith('.mp4'):
        uploaded_file.seek(0)
        st.audio(uploaded_file)
    else:
        st.info("Audio extracted from video file")

    transcribing_info = st.info("Transcribing...")
    transcribe_and_display(audio_path, model, uploaded_file.name)
    transcribing_info.empty()
    
    if os.path.exists(audio_path):
        os.unlink(audio_path)


def transcribe_and_display(audio_path: str, model: WhisperModel, filename: str) -> None:
    """
    Transcribe audio and display results progressively.
    
    Args:
        audio_path: Path to audio file
        model: Whisper model instance
        filename: Original filename for download
    """
    transcript_area = st.empty()
    full_transcript = ""
    
    for start, end, text in transcribe_audio_stream(audio_path, model):
        line = format_transcript_line(start, end, text)
        full_transcript += line + "\n"
        
        transcript_area.text_area(
            label=f"Transcript",
            value=full_transcript,
            height=300,
        )
    
    if full_transcript:
        st.success(f"Transcription complete!")
        
        base_name = filename.rsplit('.', 1)[0]
        st.download_button(
            label="Download Transcript",
            data=full_transcript,
            file_name=f"{base_name}_transcript.txt",
            mime="text/plain"
        )
    else:
        st.warning("No speech detected")


if __name__ == "__main__":
    main()