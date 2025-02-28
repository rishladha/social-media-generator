import streamlit as st
import openai
from PIL import Image
from io import BytesIO
import base64
import requests

# Page configuration
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide"
)

# Function to generate text content with OpenAI
def generate_post_text(api_key, event_details, platform, tone, focus, include_cta):
    openai.api_key = api_key
    
    # Platform-specific instructions
    platform_guides = {
        "LinkedIn": "Professional, can be detailed (~1200 characters), use line breaks effectively, may include hashtags (3-5 relevant ones), encouraging engagement. Include emojis sparingly.",
        "Twitter": "Concise (under 280 characters), engaging, include relevant hashtags (2-3), designed for retweets and engagement. Emojis are welcome.",
        "WhatsApp": "Personal, direct, clear information, no hashtags, informal but clear, focus on essential details, use emojis as appropriate."
    }
    
    # Create prompt
    prompt = f"""Generate a {tone} post for {platform} about the following event:

Event Name: {event_details['name']}
Date & Time: {event_details['datetime']}
Location: {event_details['location']}
Description: {event_details['description']}
Target Audience: {event_details['audience']}
Speakers/Hosts: {event_details['speakers']}
Registration Details: {event_details['registration']}

Content focus should be on {focus}.
{'' if include_cta else 'Do NOT include a call to action.'}

Platform-specific guidelines: {platform_guides[platform]}
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a social media marketing expert. Create engaging content for {platform}."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return None

# Function to generate image with DALL-E
def generate_event_image(api_key, event_details, platform):
    openai.api_key = api_key
    
    # Image style by platform
    image_styles = {
        "LinkedIn": "professional, corporate style with clean layout",
        "Twitter": "attention-grabbing, colorful, social media friendly",
        "WhatsApp": "clear, direct, mobile-optimized"
    }
    
    prompt = f"""Create a promotional image for an event with these details:
    
Event: {event_details['name']}
Date: {event_details['datetime']}
Topic: {event_details['description'][:100]}
Audience: {event_details['audience']}

Style: {image_styles[platform]}. 
Create a clean design suitable for {platform}, with the event name prominently displayed.
Do not include too much text. The image should be visually appealing and relevant to the event topic.
"""

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        
        return image
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Function to create download link for images
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}">📥 {text}</a>'
    return href

# Main function
def main():
    st.title("📱 Social Media Post Generator")
    st.write("Create professional posts for LinkedIn, Twitter, and WhatsApp from your event details")
    
    # Add API key input with password protection
    with st.sidebar:
        st.header("OpenAI API Key")
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        st.caption("Your API key is not stored and only used for this session")
        
        st.header("Post Customization")
        tone = st.selectbox(
            "Select tone:",
            ["Professional", "Casual", "Excited", "Urgent", "Informative", "Humorous", "Formal"]
        )
        
        focus = st.selectbox(
            "Content focus:",
            ["Value for attendees", "Industry relevance", "Learning opportunity", "Networking", "Entertainment"]
        )
        
        include_cta = st.checkbox("Include call-to-action", value=True)
    
    # Create tabs for the form and the outputs
    tab1, tab2 = st.tabs(["Event Details", "Generated Posts"])
    
    with tab1:
        st.header("Event Information")
        
        # Event details form
        with st.form("event_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                event_name = st.text_input("Event Name", "Tech Innovation Summit 2025")
                event_datetime = st.text_input("Date & Time", "March 15, 2025, 10:00 AM - 4:00 PM EST")
                event_location = st.text_input("Location", "Virtual Event (Zoom)")
                event_audience = st.text_input("Target Audience", "Tech professionals, IT managers, and innovation leaders")
            
            with col2:
                event_speakers = st.text_area("Speakers/Hosts", "Jane Doe (CTO, TechCorp), John Smith (AI Researcher)")
                event_registration = st.text_input("Registration Details", "Register at example.com/register by March 10")
                event_description = st.text_area("Event Description", "A one-day summit exploring emerging technologies with expert panels, workshops, and networking opportunities. Topics include AI, blockchain, and sustainable tech.")
            
            # Store event details in a dict to pass to functions
            event_details = {
                "name": event_name,
                "datetime": event_datetime,
                "location": event_location,
                "audience": event_audience,
                "speakers": event_speakers,
                "registration": event_registration,
                "description": event_description
            }
            
            submit_button = st.form_submit_button("Generate Posts")
    
    with tab2:
        if api_key and 'event_details' in locals() and submit_button:
            # Generate posts for each platform
            platforms = ["LinkedIn", "Twitter", "WhatsApp"]
            
            for platform in platforms:
                st.header(f"{platform} Post")
                
                col1, col2 = st.columns([3, 2])
                
                with st.spinner(f"Generating {platform} post..."):
                    # Generate text
                    post_text = generate_post_text(
                        api_key,
                        event_details,
                        platform,
                        tone,
                        focus,
                        include_cta
                    )
                    
                    # Generate image
                    post_image = generate_event_image(
                        api_key,
                        event_details,
                        platform
                    )
                
                with col1:
                    if post_text:
                        st.subheader("Post Text")
                        st.text_area(f"{platform} Text", post_text, height=200, key=f"{platform}_text")
                        download_text = f'<a href="data:text/plain;charset=utf-8,{post_text}" download="{platform.lower()}_post.txt">📥 Download Text</a>'
                        st.markdown(download_text, unsafe_allow_html=True)
                    
                with col2:
                    if post_image:
                        st.subheader("Post Image")
                        st.image(post_image, use_column_width=True)
                        st.markdown(
                            get_image_download_link(post_image, f"{platform.lower()}_image.png", "Download Image"), 
                            unsafe_allow_html=True
                        )
                
                st.divider()
        
        elif submit_button and not api_key:
            st.warning("Please enter your OpenAI API key in the sidebar to generate posts")

if __name__ == "__main__":
    main()
