import os
import json
from datetime import datetime

def export_content(content_dict, base_filename=None):
    """
    Export all generated content to separate files.
    
    Args:
        content_dict (dict): Dictionary containing all generated content
        base_filename (str): Base filename for exported files
    
    Returns:
        list: List of paths to exported files
    """
    if not base_filename:
        base_filename = f"youtube_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    exported_files = []
    
    # Export each content type to a separate file
    for content_type, content in content_dict.items():
        if content and content.strip():
            filename = f"{base_filename}_{content_type}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                exported_files.append(filename)
            except Exception as e:
                print(f"Error exporting {content_type}: {e}")
    
    # Also export everything to a single JSON file
    json_filename = f"{base_filename}_all_content.json"
    try:
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(content_dict, f, indent=2, ensure_ascii=False)
        exported_files.append(json_filename)
    except Exception as e:
        print(f"Error exporting JSON: {e}")
    
    return exported_files

def copy_to_clipboard(content):
    """
    Copy content to clipboard (cross-platform).
    
    Args:
        content (str): Content to copy to clipboard
    """
    try:
        # Try to import tkinter for clipboard functionality
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()
        root.destroy()
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

def format_for_youtube_description(content_dict):
    """
    Format content specifically for YouTube description.
    
    Args:
        content_dict (dict): Dictionary containing all generated content
    
    Returns:
        str: Formatted YouTube description
    """
    description = ""
    
    # Add title
    if content_dict.get('title'):
        description += f"Title: {content_dict['title']}\n\n"
    
    # Add main description
    if content_dict.get('description'):
        description += f"{content_dict['description']}\n\n"
    
    # Add chapters if available
    if content_dict.get('chapters'):
        description += f"Chapters:\n{content_dict['chapters']}\n\n"
    
    # Add tags
    if content_dict.get('tags'):
        description += f"Tags: {content_dict['tags']}\n\n"
    
    # Add hashtags
    if content_dict.get('hashtags'):
        description += f"Hashtags: {content_dict['hashtags']}\n\n"
    
    return description.strip()

def format_for_youtube_chapters(chapters_content):
    """
    Format chapters specifically for YouTube.
    
    Args:
        chapters_content (str): Chapters content to format
    
    Returns:
        str: Formatted YouTube chapters
    """
    # For now, just return the content as-is
    # In a more advanced implementation, we might parse and reformat timestamps
    return chapters_content

def save_captions_as_srt(captions_content, filename):
    """
    Save captions in SRT format.
    
    Args:
        captions_content (str): Captions content
        filename (str): Output filename (without extension)
    
    Returns:
        str: Path to saved file
    """
    srt_filename = f"{filename}.srt"
    try:
        # This is a simplified implementation
        # A full implementation would parse the transcript and create proper SRT format
        with open(srt_filename, 'w', encoding='utf-8') as f:
            f.write(captions_content)
        return srt_filename
    except Exception as e:
        print(f"Error saving SRT file: {e}")
        return None