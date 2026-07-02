import os
import time
import sys
import argparse

def test_whisper_gpu(audio_path, model_name="base"):
    print("=" * 60)
    print("      WHISPER GPU & CUDA PERFORMANCE PROFILER       ")
    print("=" * 60)

    # 1. Validate Audio Path
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at: {audio_path}")
        sys.exit(1)

    print(f"Target Audio File: {audio_path}")
    print(f"Target Audio Size: {os.path.getsize(audio_path) / (1024 * 1024):.2f} MB")
    print(f"Loading Whisper Model Size: '{model_name}'")

    # 2. Check CUDA & PyTorch Environment
    print("\n--- 1. Hardware & Environment Check ---")
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_avail}")
        
        if not cuda_avail:
            print("WARNING: CUDA is NOT available in this Python environment. Whisper will fallback to CPU.")
            device = "cpu"
        else:
            device = "cuda"
            print(f"CUDA Device Count: {torch.cuda.device_count()}")
            print(f"CUDA Device Name: {torch.cuda.get_device_name(0)}")
            print(f"CUDA Capability: {torch.cuda.get_device_capability(0)}")
            print(f"Max CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    except ImportError:
        print("Error: PyTorch (torch) is not installed. Please run 'pip install -r requirements.txt'")
        sys.exit(1)

    # 3. Measure Base GPU Memory
    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        mem_init = torch.cuda.memory_allocated(0) / (1024 * 1024)
        print(f"Initial GPU Memory Allocated: {mem_init:.2f} MB")
    else:
        mem_init = 0

    # 4. Load Whisper Model
    print("\n--- 2. Loading Whisper Model ---")
    try:
        from faster_whisper import WhisperModel
        start_load = time.time()
        compute_type = "float16" if device == "cuda" else "int8"
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        load_duration = time.time() - start_load
        print(f"Model loaded successfully in {load_duration:.2f} seconds.")
    except ImportError:
        print("Error: faster-whisper package not installed. Run 'pip install -r requirements.txt'")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

    # 5. Measure GPU Memory after Model Load
    if device == "cuda":
        mem_loaded = torch.cuda.memory_allocated(0) / (1024 * 1024)
        mem_loaded_peak = torch.cuda.max_memory_allocated(0) / (1024 * 1024)
        print(f"GPU Memory Allocated (after load): {mem_loaded:.2f} MB")
        print(f"Peak GPU Memory Allocated: {mem_loaded_peak:.2f} MB")
        print(f"Model VRAM Footprint: {mem_loaded - mem_init:.2f} MB")

    # 6. Execute Speech Transcription
    print("\n--- 3. Running Transcription (GPU Execution) ---")
    start_transcribe = time.time()
    try:
        segments, info = model.transcribe(audio_path, beam_size=5)
        raw_segments = list(segments)
        text = " ".join([seg.text for seg in raw_segments])
        transcribe_duration = time.time() - start_transcribe
        print(f"Transcription completed successfully in {transcribe_duration:.2f} seconds.")
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

    # 7. Print Final GPU Memory Metrics
    if device == "cuda":
        mem_final = torch.cuda.memory_allocated(0) / (1024 * 1024)
        mem_peak = torch.cuda.max_memory_allocated(0) / (1024 * 1024)
        print("\n--- 4. VRAM Utilization Summary ---")
        print(f"Peak VRAM during execution: {mem_peak:.2f} MB")
        print(f"VRAM leak/held at end: {mem_final - mem_loaded:.2f} MB")
    
    # 8. Print Output Snippet
    print("\n--- 5. Transcription Result Snippet ---")
    print(f"Total Characters: {len(text)}")
    print(f"Word Count: {len(text.split())}")
    print("\nSnippet (First 300 characters):")
    print(text[:300] + ("..." if len(text) > 300 else ""))
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile Whisper GPU/VRAM performance.")
    parser.add_argument("audio_path", help="Path to the audio file to transcribe.")
    parser.add_argument("--model", default="base", help="Whisper model name (tiny, base, small, medium, large).")
    args = parser.parse_args()
    
    test_whisper_gpu(args.audio_path, args.model)
