import streamlit as st
import openai

# Use Streamlit's secrets management
API_KEY = st.secrets["openai"]["api_key"]
openai.api_key = API_KEY

def chunk_text(text, max_length=4000):
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        cut_at = text.rfind(".", 0, max_length)
        if cut_at == -1:
            cut_at = text.rfind(" ", 0, max_length)
        chunks.append(text[:cut_at+1])
        text = text[cut_at+1:]
    return chunks

def summarize_text(chunked_text, model, progress_bar):
    summaries = []
    for i, chunk in enumerate(chunked_text):
        response = openai.Completion.create(
            model=model,
            prompt=f"Summarize the following text:\n\n{chunk}",
            max_tokens=200
        )
        summaries.append(response.choices[0].text.strip())
        progress_bar.progress((i+1)/len(chunked_text)*0.5) # Assign 50% of the progress bar to this task
    return " ".join(summaries)

def extract_themes_goals_challenges_painpoints(summary, model, progress_bar):
    prompts = {
        "themes": "Identify the key themes from the summary:",
        "goals": "List the main goals mentioned in the summary:",
        "challenges": "Highlight the main challenges from the summary:",
        "pain points": "Point out the pain points based on the summary:"
    }

    results = {}
    keys = list(prompts.keys())

    for i, (key, prompt) in enumerate(prompts.items()):
        response = openai.Completion.create(
            model=model,
            prompt=f"{prompt}\n\n{summary}",
            max_tokens=150
        )
        results[key] = response.choices[0].text.strip()
        progress_bar.progress(0.5 + (i+1)/len(keys)*0.5)  # Remaining 50% of the progress bar
    return results

def main():
    st.title('Transcript Analyzer')
    
    # Model switcher
    model_choice = st.selectbox(
        "Choose the model:", 
        ["gpt-4", "gpt-3.5-turbo"]
    )
    
    uploaded_file = st.file_uploader("Upload a transcript text file", type=["txt"])
    
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode()
        
        st.write("Processing...")
        progress_bar = st.progress(0)
        
        chunked_transcript = chunk_text(transcript)
        
        summarized_transcript = summarize_text(chunked_transcript, model_choice, progress_bar)
        extracted_info = extract_themes_goals_challenges_painpoints(summarized_transcript, model_choice, progress_bar)
        
        st.subheader("Summarized Transcript")
        st.write(summarized_transcript)
        
        for key, value in extracted_info.items():
            st.subheader(key.capitalize())
            st.write(value)

if __name__ == "__main__":
    main()

