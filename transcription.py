from faster_whisper import WhisperModel
import torch

def transcribe_audio(audio_path):
    try:
        # Use a smaller model for faster transcription
        # Options: "tiny", "base", "small", "medium", "large"
        model_size = "tiny"  # Fastest option with reasonable accuracy
        
        # Enable GPU acceleration if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        segments, info = model.transcribe(audio_path, beam_size=5)
        return "".join(segment.text for segment in segments)
    except Exception as e:
        print(e)
        return None