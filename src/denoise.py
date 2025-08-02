import os
import librosa
import soundfile as sf
import noisereduce as nr

"""
Denoising with Spectral Gating

We apply spectral noise gating using noisereduce.reduce_noise() to clean heart sound 
recordings before extracting embeddings. This method works by estimating a noise profile, 
masking low-energy frequency bins, and reconstructing a denoised signal with minimal 
distortion. This improves the quality of features extracted for downstream classification
tasks.

Internally uses STFT → Noise Spectrum Estimation → Spectral Gating → iSTFT.
"""

def denoise_audio(input_path, output_path=None):
    """
    Apply spectral noise reduction to an audio file.

    Args:
        input_path (str): Path to the noisy .wav file.
        output_path (str, optional): Path to save the denoised .wav file.
                                     If None, saves as *_denoised.wav next to input.

    Returns:
        str: Path to the denoised audio file.
    """
    try:
        # Load audio file
        y, sr = librosa.load(input_path, sr=None)
        print(f"🎧 Loaded audio: {input_path} (Sample Rate: {sr}, Duration: {len(y)/sr:.2f}s)")

        # Apply noise reduction
        reduced_noise = nr.reduce_noise(y=y, sr=sr, prop_decrease=1.0)
        print(f"✨ Noise reduction applied.")

        # Determine output path
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_denoised.wav"

        # Write the denoised audio
        sf.write(output_path, reduced_noise, sr)
        print(f"💾 Denoised file saved: {output_path}")

        return output_path

    except Exception as e:
        print(f"❌ Error in denoise_audio: {e}")
        raise
