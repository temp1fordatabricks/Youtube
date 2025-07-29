import flet as ft
from video_processing import extract_audio
from transcription import transcribe_audio
from content_generation import (
    generate_title, generate_description, generate_tags,
    generate_hashtags, generate_chapters, generate_captions
)
from export_utils import export_content, copy_to_clipboard
from config import config
from batch_processing import BatchProcessor
import os
import threading

def main(page: ft.Page):
    page.title = "YouTube Content Optimization"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT if config.get_ui_setting("theme") == "light" else ft.ThemeMode.DARK
    page.window_width = config.get_ui_setting("window_size")[0]
    page.window_height = config.get_ui_setting("window_size")[1]

    # Global variables
    current_content = {}
    current_transcript = ""
    batch_processor = BatchProcessor()
    selected_file_path = None

    def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        theme_toggle_button.icon = (
            ft.Icons.DARK_MODE_OUTLINED
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.WB_SUNNY_OUTLINED
        )
        # Save theme preference
        config.set_ui_setting("theme", "dark" if page.theme_mode == ft.ThemeMode.DARK else "light")
        page.update()

    theme_toggle_button = ft.IconButton(
        ft.Icons.DARK_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.WB_SUNNY_OUTLINED,
        on_click=theme_changed
    )

    # Define the AlertDialog and its controls at the top level of main
    api_key_input_field = ft.TextField(
        label="Perplexity API Key",
        password=True,
        can_reveal_password=True,
    )

    def close_api_key_dialog(e):
        api_key_dialog.open = False
        page.update()

    def save_api_key(e):
        api_key = api_key_input_field.value
        print(f"DEBUG: Attempting to save API Key: {api_key[:5]}*****") # Debug print
        if api_key:
            config.set_api_key("perplexity", api_key)
            api_key_status.value = "API Key Set ✓"
            api_key_status.color = ft.Colors.GREEN
            show_snackbar("API Key saved successfully!")
        else:
            api_key_status.value = "API Key Not Set ✗"
            api_key_status.color = ft.Colors.RED
            show_snackbar("API Key cannot be empty.", color=ft.Colors.RED)
        close_api_key_dialog(e)

    def clear_api_key(e):
        config.set_api_key("perplexity", "")
        api_key_input_field.value = ""
        api_key_status.value = "API Key Not Set ✗"
        api_key_status.color = ft.Colors.RED
        page.update()
        show_snackbar("API Key cleared.", color=ft.Colors.ORANGE_ACCENT)
        close_api_key_dialog(e)

    api_key_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("API Key Configuration"),
        content=ft.Column([
            ft.Text("Enter your Perplexity API key:"),
            api_key_input_field,
            ft.Text("Get your API key from https://perplexity.ai", size=12, color=ft.Colors.GREY)
        ], width=400),
        actions=[
            ft.TextButton("Clear", on_click=clear_api_key),
            ft.TextButton("Cancel", on_click=close_api_key_dialog),
            ft.TextButton("Save", on_click=save_api_key),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Add the dialog to the page overlay
    page.overlay.append(api_key_dialog)
    page.update()

    def show_api_key_dialog(e):
        print("DEBUG: show_api_key_dialog called") # Debug print
        # Set the initial value of the TextField when the dialog is opened
        api_key_input_field.value = config.get_api_key("perplexity")
        api_key_dialog.open = True
        page.update()

    # Check if API key is set
    api_key_status = ft.Text(
        "API Key Not Set ✗" if not config.get_api_key("perplexity") else "API Key Set ✓",
        color=ft.Colors.RED if not config.get_api_key("perplexity") else ft.Colors.GREEN,
        size=12
    )

    api_key_button = ft.IconButton(
        ft.Icons.SETTINGS,
        on_click=show_api_key_dialog,
        tooltip="Configure API Key"
    )

    page.appbar = ft.AppBar(
        title=ft.Text("YouTube Content Optimization"),
        actions=[api_key_status, api_key_button, theme_toggle_button],
    )

    def show_snackbar(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            open=True,
            bgcolor=color
        )
        page.update()

    def show_error_dialog(title, message):
        def close_error_dlg(e):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Ok", on_click=close_error_dlg)
            ]
        )
        page.dialog.open = True
        page.update()

    def update_progress_ui(message):
        progress_text.value = message
        page.update()

    def on_batch_processing_complete(e=None):
        update_progress_ui("Batch processing completed!")
        process_button.disabled = False
        batch_process_button.disabled = False
        progress_bar.visible = False
        page.update()
        # Display results of the last processed file in the batch
        results = batch_processor.get_results()
        if results:
            last_file_path = list(results.keys())[-1]
            last_result = results[last_file_path]
            if last_result["status"] == "success":
                global current_content, current_transcript
                current_content = last_result["content"]
                current_transcript = last_result.get("transcript", "") # Use .get for safety
                update_result_tabs()
                show_snackbar(f"Batch processing finished. Displaying results for {os.path.basename(last_file_path)}")
            else:
                show_error_dialog("Batch Processing Error", f"Error processing {os.path.basename(last_file_path)}: {last_result['error']}")
                update_progress_ui(f"Batch processing finished with errors.")

    def update_result_tabs():
        title_text_field.value = current_content.get("title", "")
        description_text_field.value = current_content.get("description", "")
        tags_text_field.value = current_content.get("tags", "")
        hashtags_text_field.value = current_content.get("hashtags", "")
        chapters_text_field.value = current_content.get("chapters", "")
        captions_text_field.value = current_content.get("captions", "")
        transcript_text_field.value = current_transcript

        export_all_button.disabled = False
        copy_title_button.disabled = not bool(current_content.get("title"))
        copy_description_button.disabled = not bool(current_content.get("description"))
        copy_tags_button.disabled = not bool(current_content.get("tags"))
        copy_hashtags_button.disabled = not bool(current_content.get("hashtags"))
        page.update()

    def process_video_thread(selected_file_path):
        """Main processing logic in a separate thread to avoid UI freezing."""
        try:
            # Reset current content
            global current_content, current_transcript
            current_content = {}
            current_transcript = ""

            # Update progress
            page.run_thread(update_progress_ui, "Extracting audio...")
            audio_path = extract_audio(selected_file_path)
            if not audio_path:
                page.run_thread(show_error_dialog, "Audio Extraction Failed", "Could not extract audio from the video. Ensure FFmpeg is installed and accessible in your system's PATH.")
                return

            # Update progress
            page.run_thread(update_progress_ui, "Transcribing audio...")
            transcript = transcribe_audio(audio_path)
            if not transcript:
                page.run_thread(show_error_dialog, "Transcription Failed", "Could not transcribe audio. Check the audio file and Whisper model.")
                return

            current_transcript = transcript
            print(f"DEBUG: Transcript length: {len(transcript)} characters")
            print(f"DEBUG: Transcript snippet: {transcript[:200]}...")

            # Update progress
            page.run_thread(update_progress_ui, "Generating content...")
            
            # Generate all content
            current_content["title"] = generate_title(transcript)
            current_content["description"] = generate_description(transcript)
            current_content["tags"] = generate_tags(transcript)
            current_content["hashtags"] = generate_hashtags(transcript)
            current_content["chapters"] = generate_chapters(transcript)
            current_content["captions"] = generate_captions(transcript)

            print(f"DEBUG: Generated Content: {current_content}")

            # Check for API errors in generated content
            for key, value in current_content.items():
                if isinstance(value, str) and (value.startswith("Error:") or value.startswith("HTTP Error:") or "error" in value.lower()):
                    page.run_thread(show_error_dialog, "Content Generation Error", f"An API error occurred during {key} generation: {value}. Please check your API key and network connection.")
                    current_content[key] = ""
            
            page.run_thread(update_result_tabs)
            page.run_thread(show_snackbar, "Processing complete!")
            page.run_thread(update_progress_ui, "Processing complete!")
        except Exception as ex:
            page.run_thread(show_error_dialog, "Processing Error", f"An unexpected error occurred: {str(ex)}")
            page.run_thread(update_progress_ui, f"Error: {str(ex)}")
        finally:
            progress_bar.visible = False
            process_button.disabled = False
            page.run_thread(page.update)

            # Clean up temporary audio file
            try:
                if 'audio_path' in locals() and os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary audio file: {e}")

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
            global selected_file_path
            selected_file_path = selected_file.path
            progress_bar.visible = True
            progress_text.visible = True
            update_progress_ui("Processing video...")
            process_button.disabled = True
            page.update()

            # Check API key before starting
            if not config.get_api_key("perplexity"):
                show_error_dialog("API Key Missing", "Please configure your Perplexity API key in settings before processing.")
                progress_bar.visible = False
                progress_text.visible = False
                process_button.disabled = False
                page.update()
                return

            # Run processing in a separate thread
            thread = threading.Thread(target=process_video_thread, args=(selected_file.path,), daemon=True)
            thread.start()

    def pick_files_for_batch_result(e: ft.FilePickerResultEvent):
        if e.files:
            # Check API key before starting batch
            if not config.get_api_key("perplexity"):
                show_error_dialog("API Key Missing", "Please configure your Perplexity API key in settings before starting batch processing.")
                page.update()
                return

            for f in e.files:
                batch_processor.add_file(f.path)
            
            if not batch_processor.is_processing():
                progress_bar.visible = True
                progress_text.visible = True
                update_progress_ui(f"Added {len(e.files)} files to batch. Starting processing...")
                process_button.disabled = True
                batch_process_button.disabled = True
                batch_processor.set_progress_callback(update_progress_ui)
                batch_processor.process_queue()
            else:
                update_progress_ui(f"Added {len(e.files)} files to queue. {batch_processor.get_queue_size()} files in queue.")
            page.update()

    def copy_content_to_clipboard(content_type):
        content = current_content.get(content_type, "")
        if content:
            if copy_to_clipboard(content):
                show_snackbar(f"{content_type.capitalize()} copied to clipboard!")
            else:
                show_snackbar(f"Failed to copy {content_type} to clipboard.", color=ft.Colors.RED)
        else:
            show_snackbar(f"No {content_type} content to copy.", color=ft.Colors.ORANGE_ACCENT)

    def export_all_content(e):
        if current_content:
            try:
                from datetime import datetime # Import datetime here to avoid circular dependency if it's not used elsewhere
                # Use the filename of the last processed file for single mode, or a generic name for batch
                if batch_processor.is_processing() or batch_processor.get_results():
                    base_filename = f"youtube_batch_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                else:
                    # Use the actual file name from the single file picker
                    if selected_file_path:
                        base_filename = f"{os.path.splitext(os.path.basename(selected_file_path))[0]}_youtube_content"
                    else:
                        base_filename = f"youtube_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                exported_files = export_content(current_content, base_filename)
                if exported_files:
                    show_snackbar(f"Exported {len(exported_files)} files!")
                    update_progress_ui(f"Exported {len(exported_files)} files!")
                else:
                    show_error_dialog("Export Failed", "No files were exported. Check console for errors.")
                    update_progress_ui("Export failed.")
            except Exception as ex:
                show_error_dialog("Export Failed", f"An error occurred during export: {str(ex)}")
                update_progress_ui(f"Export failed: {str(ex)}")
        else:
            show_snackbar("No content to export.", color=ft.Colors.ORANGE_ACCENT)
            update_progress_ui("No content to export.")

    # UI Elements
    progress_bar = ft.ProgressBar(width=400, visible=False)
    progress_text = ft.Text("", visible=False)
    
    file_picker = ft.FilePicker(on_result=pick_files_result)
    batch_file_picker = ft.FilePicker(on_result=pick_files_for_batch_result)
    page.overlay.append(file_picker)
    page.overlay.append(batch_file_picker)

    process_button = ft.ElevatedButton(
        "Upload Single Video",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allowed_extensions=["mp4", "avi", "mov", "mkv"]),
    )

    batch_process_button = ft.ElevatedButton(
        "Upload Multiple Videos (Batch)",
        icon=ft.Icons.PLAY_FOR_WORK,
        on_click=lambda _: batch_file_picker.pick_files(allow_multiple=True, allowed_extensions=["mp4", "avi", "mov", "mkv"]),
    )

    # Copy buttons
    copy_title_button = ft.IconButton(
        icon=ft.Icons.COPY,
        tooltip="Copy Title",
        on_click=lambda _: copy_content_to_clipboard("title"),
        disabled=True
    )
    
    copy_description_button = ft.IconButton(
        icon=ft.Icons.COPY,
        tooltip="Copy Description",
        on_click=lambda _: copy_content_to_clipboard("description"),
        disabled=True
    )
    
    copy_tags_button = ft.IconButton(
        icon=ft.Icons.COPY,
        tooltip="Copy Tags",
        on_click=lambda _: copy_content_to_clipboard("tags"),
        disabled=True
    )
    
    copy_hashtags_button = ft.IconButton(
        icon=ft.Icons.COPY,
        tooltip="Copy Hashtags",
        on_click=lambda _: copy_content_to_clipboard("hashtags"),
        disabled=True
    )

    # Export button
    export_all_button = ft.ElevatedButton(
        "Export All",
        icon=ft.Icons.SAVE,
        on_click=export_all_content,
        disabled=True
    )

    # Create TextField widgets for each tab
    title_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    description_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    tags_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    hashtags_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    chapters_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    captions_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )
    
    transcript_text_field = ft.TextField(
        value="",
        multiline=True,
        min_lines=10,
        max_lines=20,
        read_only=True,
        expand=True
    )

    # Tab content creation helper
    def create_tab_content(label, text_field):
        return ft.Column([
            ft.Row([
                ft.Text(label, size=20, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.COPY, tooltip=f"Copy {label}", on_click=lambda _: copy_content_to_clipboard(label.lower()))
            ]),
            text_field
        ], expand=True)

    # Create tabs
    title_tab = ft.Tab(
        text="Title",
        content=create_tab_content("Title", title_text_field)
    )
    
    description_tab = ft.Tab(
        text="Description",
        content=create_tab_content("Description", description_text_field)
    )
    
    tags_tab = ft.Tab(
        text="Tags",
        content=create_tab_content("Tags", tags_text_field)
    )
    
    hashtags_tab = ft.Tab(
        text="Hashtags",
        content=create_tab_content("Hashtags", hashtags_text_field)
    )
    
    chapters_tab = ft.Tab(
        text="Chapters",
        content=create_tab_content("Chapters", chapters_text_field)
    )
    
    captions_tab = ft.Tab(
        text="Captions",
        content=create_tab_content("Captions", captions_text_field)
    )
    
    transcript_tab = ft.Tab(
        text="Transcript",
        content=create_tab_content("Transcript", transcript_text_field)
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            title_tab,
            description_tab,
            tags_tab,
            hashtags_tab,
            chapters_tab,
            captions_tab,
            transcript_tab
        ],
        expand=1
    )

    # Main layout
    page.add(
        ft.Column(
            [
                ft.Text("YouTube Content Optimization Tool", size=30, weight=ft.FontWeight.BOLD),
                ft.Row([
                    process_button,
                    batch_process_button,
                    export_all_button
                ]),
                ft.Row([
                    copy_title_button,
                    copy_description_button,
                    copy_tags_button,
                    copy_hashtags_button
                ]),
                progress_bar,
                progress_text,
                tabs
            ],
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)