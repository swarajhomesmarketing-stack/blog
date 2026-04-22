import os
import feedparser
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime

# The library automatically looks for an environment variable named GOOGLE_API_KEY
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("CRITICAL ERROR: GOOGLE_API_KEY not found in environment variables.")
    # This will help us debug in the GitHub Actions log
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_topics():
    rss_url = "https://news.google.com/rss/search?q=Maharashtra+Real+Estate+MahaRERA+when:1d&hl=en-IN&gl=IN"
    feed = feedparser.parse(rss_url)
    return [entry.title for entry in feed.entries[:4]]

def generate_blog(topic, platform):
    prompt = f"Write an 800-word humanized, professional blog for {platform} about: {topic}. Focus on Maharashtra, India. Use local real estate terms. Do not sound like an AI."
    
    try:
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        return response.text
    except Exception as e:
        return f"AI Generation failed. Error: {str(e)}"

def main():
    topics = get_topics()
    platforms = ["WordPress", "Medium", "Blogger", "Substack"]
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"blogs-{date_str}.txt"
    
    if not topics:
        print("No news found today.")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"DAILY BLOG REPORT: {date_str}\n" + "="*30 + "\n\n")
        for i in range(len(topics)):
            print(f"Generating blog {i+1}...")
            content = generate_blog(topics[i], platforms[i])
            img_url = f"https://image.pollinations.ai/prompt/luxury_real_estate_maharashtra_{topics[i].replace(' ', '_')}"
            
            f.write(f"TOPIC: {topics[i]}\n")
            f.write(f"FOR PLATFORM: {platforms[i]}\n")
            f.write(f"IMAGE LINK: {img_url}\n\n")
            f.write(content)
            f.write("\n\n" + "-"*50 + "\n\n")

if __name__ == "__main__":
    main()
