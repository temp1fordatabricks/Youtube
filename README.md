# YouTube Content Optimizer

A desktop application that helps content creators optimize their YouTube videos by automatically generating titles, descriptions, tags, hashtags, chapters, and captions using AI.

## Features

- **Automatic Content Generation**: Generate optimized titles, descriptions, tags, hashtags, chapters, and captions for your YouTube videos
- **AI-Powered**: Uses Perplexity AI to create high-quality, SEO-optimized content
- **Batch Processing**: Process multiple videos at once
- **Export Options**: Export generated content in various formats
- **User-Friendly Interface**: Simple and intuitive desktop application built with Flet

## Requirements

- Python 3.8 or higher
- FFmpeg installed and accessible in your system's PATH
- Perplexity API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-content-optimizer.git
   cd youtube-content-optimizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install FFmpeg:
   - Windows: Download from https://ffmpeg.org/download.html
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Configure your Perplexity API key in the settings
3. Upload a video file
4. Wait for the AI to generate optimized content
5. Review and export the generated content

## Configuration

The application stores your settings in `app_config.json`, including your API key and UI preferences.

## Packaging

To create a distributable package:

```
python setup.py sdist bdist_wheel
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Perplexity AI for content generation
- Faster-Whisper for audio transcription
- Flet for the desktop UI framework