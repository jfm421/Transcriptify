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
        messages = [{"role": "user", "content": f"You are an expert in business strategy and enterprise architecture. Take a deep breath and work on this problem step by step. Identify the subject matter under discussion and the outcomes required in this context, and consider these factors when you summarize the following text: {chunk}"}]
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        
        summaries.append(response.choices[0].message['content'].strip())
        progress_bar.progress((i+1)/len(chunked_text)*0.5)  # 50% of the progress bar for this task
    return " ".join(summaries)

def extract_themes_information_stakeholders_goals_challenges_opportunities_capabilities(summary, model, progress_bar):
    prompts = {
        "themes": "Identify the key themes from the summary:",
        "information": "List the key information concepts and business objects mentioned in the summary",
        "stakeholders": "List the stakeholders and organisations mentioned in the summary:",
        "goals": "List the main goals mentioned in the summary:",
        "challenges": "Point out the pain points and challenges based on the summary:",
        "opportunities": "List the opportunities to resolve the challenges from the summary and provide a set of recommendations:",
        "capabilities": "Where possible infer connections and relate the above datapoints to relevant business capabilities in the bizbok style and provide succinct commentary on the following capability dimensions including human resources - roles and skills required, business processes required, information and data aspects and technology enablers:", 
    }

    results = {}
    keys = list(prompts.keys())

    for i, (key, prompt) in enumerate(prompts.items()):
        messages = [{"role": "user", "content": f"{prompt} {summary}"}]
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        
        results[key] = response.choices[0].message['content'].strip()
        progress_bar.progress(0.5 + (i+1)/len(keys)*0.5)  # Remaining 50% of the progress bar

    return results

def main():
    st.title('Transcript Analyzer')
    
    # Model switcher
    model_choice = st.selectbox(
        "Choose the model:", 
        ["gpt-4", "gpt-3.5-turbo-16k"]
    )
    
    uploaded_file = st.file_uploader("Upload a transcript text file", type=["txt"])
    
    if uploaded_file is not None:
        transcript = uploaded_file.read().decode()
        
        st.write("Processing...")
        progress_bar = st.progress(0)
        
        chunked_transcript = chunk_text(transcript)
        
        summarized_transcript = summarize_text(chunked_transcript, model_choice, progress_bar)
        extracted_info = extract_themes_information_stakeholders_goals_challenges_opportunities_capabilities(summarized_transcript, model_choice, progress_bar)
        
        st.subheader("Summarized Transcript")
        st.write(summarized_transcript)
        
        for key, value in extracted_info.items():
            st.subheader(key.capitalize())
            st.write(value)

if __name__ == "__main__":
    main()
