import os
import requests
import base64
import subprocess

#https://www.ffmpeg.org/documentation.html
def ffmpeg_support(url, folder, media_type, index, extension="mp4"):
    output_filename = os.path.join(folder, f"{media_type}_{index}.{extension}")
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
    except subprocess.CalledProcessError as e:
        print(f"[🛑] FFmpeg failed {media_type}: {e}")
    except Exception as e:
        print(f"[🛑] Failed {media_type} URL with FFmpeg: {e}")

def image_download(url, folder, media_type, index, extension="jpg"):
    output_filename = os.path.join(folder, f"{media_type}_{index}.{extension}")
    try:
        if url.startswith("data:"):
            # Handle data URL
            header, encoded = url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            extension = mime_type.split("/")[-1]
            decoded_data = base64.b64decode(encoded)
            with open(output_filename, "wb") as f:
                f.write(decoded_data)
            print(f"[✅] Successfully download Image {output_filename}")
        else:
            # Handle standard media URL
            response = requests.get(url)
            response.raise_for_status()
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"[✅] {media_type} Downloaded {output_filename}")
    except requests.RequestException as e:
        print(f"[🛑] Failed to download {media_type}_{index} URL: {e}")
    except Exception as e:
        print(f"[🛑] Failed to grab {media_type}_{index} URL: {e}")

def js_download(url, folder):
    name = os.path.basename(url)
    output_filename = os.path.join(folder, f"{name}.js")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_filename, "w") as f:
            f.write(response.text)
        print(f"[✅] Downloaded JavaScript from URL to {output_filename}")
    except requests.RequestException as e:
        print(f"[🛑] Failed to download JavaScript from URL: {e}")
    except Exception as e:
        print(f"[🛑] Failed to grab JavaScript URL: {e}")