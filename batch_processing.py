import os
import threading
import queue
from pathlib import Path
from video_processing import extract_audio
from transcription import transcribe_audio
from content_generation import (
    generate_title, generate_description, generate_tags,
    generate_hashtags, generate_chapters, generate_captions
)

class BatchProcessor:
    """
    Batch processor for handling multiple video files.
    """
    
    def __init__(self):
        self.processing_queue = queue.Queue()
        self.results = {}
        self.processing = False
        self.current_file = None
        self.progress_callback = None
    
    def add_file(self, file_path):
        """
        Add a file to the processing queue.
        
        Args:
            file_path (str): Path to the video file
        """
        self.processing_queue.put(file_path)
    
    def set_progress_callback(self, callback):
        """
        Set callback function for progress updates.
        
        Args:
            callback (function): Function to call with progress updates
        """
        self.progress_callback = callback
    
    def process_queue(self):
        """
        Process all files in the queue.
        """
        if self.processing:
            return
        
        self.processing = True
        
        def worker():
            while not self.processing_queue.empty():
                try:
                    file_path = self.processing_queue.get_nowait()
                    self.current_file = file_path
                    self._update_progress(f"Processing {os.path.basename(file_path)}")
                    
                    # Process the file
                    result = self._process_file(file_path)
                    self.results[file_path] = result
                    
                    self._update_progress(f"Completed {os.path.basename(file_path)}")
                    self.processing_queue.task_done()
                except queue.Empty:
                    break
                except Exception as e:
                    self._update_progress(f"Error processing file: {e}")
            
            self.processing = False
            self.current_file = None
            self._update_progress("Batch processing completed")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
    
    def _process_file(self, file_path):
        """
        Process a single file.
        
        Args:
            file_path (str): Path to the video file
        
        Returns:
            dict: Processing results
        """
        result = {
            "file": file_path,
            "status": "failed",
            "error": None,
            "content": {}
        }
        
        try:
            # Extract audio
            self._update_progress("Extracting audio...")
            audio_path = extract_audio(file_path)
            if not audio_path:
                result["error"] = "Failed to extract audio"
                return result
            
            # Transcribe audio
            self._update_progress("Transcribing audio...")
            transcript = transcribe_audio(audio_path)
            if not transcript:
                result["error"] = "Failed to transcribe audio"
                return result
            result["transcript"] = transcript # Store transcript in result
            
            # Generate content
            self._update_progress("Generating content...")
            result["content"]["title"] = generate_title(transcript)
            result["content"]["description"] = generate_description(transcript)
            result["content"]["tags"] = generate_tags(transcript)
            result["content"]["hashtags"] = generate_hashtags(transcript)
            result["content"]["chapters"] = generate_chapters(transcript)
            result["content"]["captions"] = generate_captions(transcript)
            
            result["status"] = "success"
            
            # Clean up temporary audio file
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception as e:
                print(f"Warning: Could not remove temporary audio file: {e}")
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _update_progress(self, message):
        """
        Update progress through callback.
        
        Args:
            message (str): Progress message
        """
        if self.progress_callback:
            self.progress_callback(message)
    
    def get_results(self):
        """
        Get processing results.
        
        Returns:
            dict: Processing results
        """
        return self.results
    
    def is_processing(self):
        """
        Check if batch processing is active.
        
        Returns:
            bool: True if processing, False otherwise
        """
        return self.processing
    
    def get_queue_size(self):
        """
        Get the number of files in the queue.
        
        Returns:
            int: Number of files in queue
        """
        return self.processing_queue.qsize()

# Example usage:
# processor = BatchProcessor()
# processor.add_file("video1.mp4")
# processor.add_file("video2.mp4")
# processor.set_progress_callback(lambda msg: print(msg))
# processor.process_queue()