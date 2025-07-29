import os
import requests
import json
from config import config

API_URL = "https://api.perplexity.ai/chat/completions"

def _call_perplexity_api(system_prompt, user_prompt):
    """
    Helper function to call the Perplexity API with given prompts.
    """
    # Get API key from config (which checks both environment variables and config file)
    api_key = config.get_api_key("perplexity")
    if not api_key:
        print("DEBUG: Perplexity API key not found.")
        return "Error: Perplexity API key not set. Please configure it in the settings."
    print(f"DEBUG: Using Perplexity API key (first 5 chars): {api_key[:5]}*****")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    print(f"DEBUG: API Request Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"DEBUG: API Response Status Code: {response.status_code}")
        print(f"DEBUG: API Response Headers: {response.headers}")
        print(f"DEBUG: API Response Text: {response.text}")
        
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error calling Perplexity API: {e}. Status code: {response.status_code}. Response: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error calling Perplexity API: {e}"
    except Exception as e:
        return f"Unexpected error calling Perplexity API: {e}"

def generate_title(transcript):
    """
    Generates a YouTube title based on the video transcript.
    """
    system_prompt = "You are a YouTube title generator."
    user_prompt = f"Generate a catchy, clear title under 60 characters for a video with this transcript. Place primary keywords at the beginning for better SEO. Incorporate numbers and power words to increase click-through rates. Ensure relevance to video content while avoiding misleading clickbait:\n\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)

def generate_description(transcript):
    """
    Generates a YouTube video description based on the transcript.
    """
    system_prompt = "You are a YouTube description writer. Create engaging, keyword-rich descriptions that hook viewers in the first 2-3 lines."
    user_prompt = f"Create a detailed YouTube video description for a video with this transcript. Include:\n1. A hook with keyword-rich opening 2-3 lines\n2. Detailed video summary for YouTube's algorithm\n3. Timestamped chapters for easy navigation\n4. Social media links and website references\n5. Credits and acknowledgments\n6. Optimized hashtags at the end\n\nTranscript:\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)

def generate_tags(transcript):
    """
    Generates optimized YouTube tags based on the transcript.
    """
    system_prompt = "You are a YouTube SEO expert specializing in tag optimization."
    user_prompt = f"Generate a mix of broad and specific tags for maximum reach for a video with this transcript. Include exact match and long-tail keyword variations. Balance relevance with strategic reach optimization:\n\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)

def generate_hashtags(transcript):
    """
    Generates trending hashtags based on the transcript.
    """
    system_prompt = "You are a social media trends expert who identifies trending hashtags."
    user_prompt = f"Generate trending hashtags for a video with this transcript. Combine trending general hashtags with video-specific ones. Research current social media trends across platforms. Balance discovery with relevance:\n\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)

def generate_chapters(transcript):
    """
    Generates timestamped chapters based on the transcript.
    """
    system_prompt = "You are a YouTube chapter generator that creates timestamped content segments."
    user_prompt = f"Generate descriptive chapter titles with precise timestamps for a video with this transcript. Automatically detect content segments from the transcript analysis. Format chapters for optimal YouTube integration:\n\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)

def generate_captions(transcript):
    """
    Generates formatted captions based on the transcript.
    """
    system_prompt = "You are a caption formatter that creates SEO-optimized, accessible captions."
    user_prompt = f"Format this transcript as SEO-optimized, accessible captions. Ensure proper formatting for YouTube. Include punctuation and speaker identification if applicable:\n\n{transcript}"
    return _call_perplexity_api(system_prompt, user_prompt)