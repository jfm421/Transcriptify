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
        messages = [{"role": "user", "content": f"Summarize the following text: {chunk}"}]
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        
        summaries.append(response.choices[0].message['content'].strip())
        progress_bar.progress((i+1)/len(chunked_text)*0.5)  # 50% of the progress bar for this task
    return " ".join(summaries)

def generate_toc_content(summary, model, progress_bar):
    sections = {
        "Introduction": "Provide an introduction based on the summary.",
        "Overview of the project and its objectives": "Extract the overview of the project and its main objectives from the summary.",
        "Research Plan Overview": "Describe the research plan and its origin from initial workshops.",
        "Key hypotheses articulated for the study": "Identify the key hypotheses that were articulated for the study from the summary.",
        "Key Findings and Themes": "Extract the main findings and themes from the summary.",
        "User-suggested remedies and potential solutions": "Identify user-suggested remedies and potential AI-related solutions from the summary.",
        "Discussion on collective thoughts and approaches": "Highlight the collective thoughts and approaches from the summary.",
        "Recommendations": "List the six to eight major themes from user feedback and potential solutions for each problem area, including suggestions for automation.",
        "Personas and Sales Journey Mapping": "Provide an outline of personas, their goals, challenges, and opportunities, and jobs-to-be-done associated with each role from the summary.",
        "Staff Roles Involved in the Sales Journey": "Mention the roles involved in the sales journey including Customer Solutions Consultant, Sales Operations Manager, Sales Support Manager, Product Manager, Account Manager, and Customer Relationship Manager.",
        "Dimensions for Sales Journey Visualisation": "Discuss customer experience highs and lows, data source types, problem statements, tools used, and potential solutions across journey stages.",
        "Map Governance and Update Process opportunities": "Recommend strategies for maintaining wikis, integrating feedback, and using competitor data.",
        "User Interface (UI) Prototypes": "Describe preliminary designs for updated Confluence pages and other interfaces.",
        "Conclusion and Next Steps": "Provide a recap of findings and the suggested path forward, mentioning upcoming presentations and deliverables.",
        "Appendix": "Provide details on the original research plan document, detailed interview transcripts, and syntheses."
    }

    content = {}
    keys = list(sections.keys())
    progress_increment = 1.0 / len(keys)

    for i, (section, prompt) in enumerate(sections.items()):
        messages = [{"role": "user", "content": f"{prompt} {summary}"}]
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        
        content[section] = response.choices[0].message['content'].strip()
        progress_bar.progress((i+1) * progress_increment)

    return content

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

