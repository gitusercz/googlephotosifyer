import cv2
import os
import imageio
from pathlib import Path
from PIL import Image

# Define the source and output directories relative to the script location
script_dir = Path(__file__).parent
src_dir = 'C:/Users/HP/PycharmProjects/GooglePhotosify/demo_img'
output_dir = script_dir / 'output'
thumbnails_dir = output_dir / 'thumbnails'
output_dir.mkdir(exist_ok=True)  # Ensure the output directory exists
thumbnails_dir.mkdir(exist_ok=True)  # Ensure the thumbnails directory exists


# Function to extract frames, resize them, and create a GIF with infinite loop
def extract_frames_and_create_gif(video_path, output_gif_path, percentages, resize_percentage=0.2):
    vidcap = cv2.VideoCapture(str(video_path))
    try:
        duration = vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / vidcap.get(cv2.CAP_PROP_FPS)
        if duration == 0:
            raise ZeroDivisionError
    except ZeroDivisionError:
        print(f"Error: Frame count or FPS is zero for {video_path}. Creating a placeholder GIF.")
        # Create a red placeholder image for the GIF
        placeholder = Image.new('RGB', (100, 100), color='red')
        placeholder.save(output_gif_path, format='GIF', loop=0)
        vidcap.release()
        return
    frames = []
    for percent in percentages:
        time = duration * percent
        frame_num = int(time * vidcap.get(cv2.CAP_PROP_FPS))
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, image = vidcap.read()
        if success:
            # Resize frame
            height, width = image.shape[:2]
            new_dimensions = (int(width * resize_percentage), int(height * resize_percentage))
            resized_image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)
            frames.append(resized_image)
        else:
            print(f"Frame at {percent * 100}% could not be read from {video_path}")
    vidcap.release()
    # Ensure frames are converted to RGB as imageio expects images in RGB format
    frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in frames]
    # Save the GIF with infinite looping
    imageio.mimsave(output_gif_path, frames_rgb, fps=4, loop=0)


def resize_and_save_image_with_pil(image_path, output_path, resize_percentage=0.1):
    try:
        # Open the image using PIL
        with Image.open(image_path) as img:
            # Calculate the new size
            width, height = img.size
            new_dimensions = (int(width * resize_percentage), int(height * resize_percentage))

            # Resize the image
            resized_image = img.resize(new_dimensions, Image.Resampling.LANCZOS)

            # Save the resized image
            resized_image.save(output_path)
        # print(f"Resized {image_path} using PIL.")
    except Exception as e:
        print(f"Failed to resize {image_path} with PIL due to: {e}")


def resize_and_save_image(image_path, output_path, resize_percentage=0.1):
    # Try with cv2
    image = cv2.imread(str(image_path))
    if image is None:
        # print(f"Warning: Could not read {image_path} with OpenCV. Trying with PIL.")
        # Fallback to PIL if cv2 fails
        resize_and_save_image_with_pil(image_path, output_path, resize_percentage)
    else:
        height, width = image.shape[:2]
        new_dimensions = (int(width * resize_percentage), int(height * resize_percentage))
        resized_image = cv2.resize(image, new_dimensions, interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(output_path), resized_image)
        # print(f"Resized {image_path} using OpenCV.")


def process_directory(src_dir):
    thumbnails_dir = src_dir / 'thumbnails'
    html_file = src_dir / f'{src_dir.name}.html'

    # Check if the thumbnails directory and HTML file already exist
    if thumbnails_dir.exists() and html_file.exists():
        print(f"Skipping {src_dir} as thumbnails and HTML file already exist.")
        return  # Skip processing this directory

    # If they don't exist, create the thumbnails directory
    thumbnails_dir.mkdir(exist_ok=True)

    content = ""
    for file in sorted(os.listdir(src_dir)):
        file_path = src_dir / file
        if file.lower().endswith('.mp4'):
            # Create GIFs in the thumbnails directory
            gif_path = thumbnails_dir / f'{Path(file).stem}.gif'
            extract_frames_and_create_gif(file_path, gif_path, [i / 10 for i in range(10)])
            thumbnail_path = f'thumbnails/{Path(file).stem}.gif'
        elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Create resized images in the thumbnails directory
            thumbnail_path = thumbnails_dir / file
            resize_and_save_image(file_path, thumbnail_path)
            thumbnail_path = f'thumbnails/{file}'
        else:
            continue  # Skip non-image/video files
        original_path = f'{file}'
        content += f'<a href="{original_path}" target="_blank"><img src="{thumbnail_path}" alt="{file}" style="width:auto; height:auto;"></a>\n'

    # Generate HTML content
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{src_dir.name}</title>
    </head>
    <body>
        <h1>{src_dir.name}</h1>
        <div>{content}</div>
    </body>
    </html>
    """

    # Save the HTML file in the current src_dir
    with open(src_dir / f'{src_dir.name}.html', 'w', encoding='utf-8') as f:
        f.write(html_template.format(content=content))


# # Main process
# script_dir = Path(__file__).parent
# src_dir = script_dir / 'src_img'

for root, dirs, files in os.walk(src_dir):
    current_dir = Path(root)
    # Check if the current directory contains image or video files
    if any(file.lower().endswith(('.mp4', '.png', '.jpg', '.jpeg', '.gif')) for file in files):
        process_directory(current_dir)

print("HTML galleries created successfully in each directory!")
