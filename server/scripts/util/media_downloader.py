import os
import base64
import subprocess
import whisper

model = whisper.load_model("base")

# https://www.ffmpeg.org/documentation.html
def ffmpeg_support(url, folder, media_type, index, extension="mp4"):
    output_filename = os.path.join(folder, f"{media_type}_{index}.{extension}")
    audio_filename = os.path.join(folder, f"{media_type}_{index}.mp3")
    
    try:
        if url.startswith("data:"):
            # Handle data URL
            header, encoded = url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            extension = mime_type.split("/")[-1]
            decoded_data = base64.b64decode(encoded)
            
            # Save decoded data to a temporary file
            temp_filename = os.path.join(folder, f"temp_{index}.{extension}")
            with open(temp_filename, "wb") as f:
                f.write(decoded_data)

            # Convert and save final output with FFmpeg
            ffmpeg_command = ["ffmpeg", "-i", temp_filename, output_filename]
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Remove temporary file
            os.remove(temp_filename)
            print(f"[✅] Video Downloaded {output_filename}")

        else:
            # Handle standard media URL
            ffmpeg_command = ["ffmpeg", "-i", url, output_filename]
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[✅] Saved {media_type}_{index} to {output_filename}")

        # Convert video to audio
        ffmpeg_audio_command = ["ffmpeg", "-i", output_filename, "-q:a", "0", "-map", "a", audio_filename]
        subprocess.run(ffmpeg_audio_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Transcribe audio with Whisper
        result = model.transcribe(audio_filename)
        transcription_text = result["text"]

        # Optionally save transcription to a text file
        transcription_file = os.path.join(folder, f"{media_type}_{index}_transcription.txt")
        with open(transcription_file, "w") as f:
            f.write(transcription_text)
        
        print(f"[✅] Transcription saved to {transcription_file}")

        return transcription_text

    except subprocess.CalledProcessError as e:
        print(f"[🛑] FFmpeg failed {media_type}: {e}")
    except Exception as e:
        print(f"[🛑] Failed {media_type} URL with FFmpeg: {e}")

    # Return an empty string on error to avoid returning None.
    return ""
