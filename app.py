import streamlit as st 
import base64
import os
import fitz
import backend as K

st.set_page_config(page_title="TUK", layout="wide")

if 'options' not in st.session_state and 'trulens_feedback_score' not in st.session_state and 'pdf' not in st.session_state:
    st.session_state['options'] = [] 
    st.session_state['trulens_feedback_score'] = {}
    st.session_state['pdf'] = None

sidebar = st.sidebar
header = st.container()
body = st.container()

with sidebar:
    key = st.text_input('Enter your OpenAI Key:', type="password")
    os.environ["OPENAI_API_KEY"] = key
    uploaded_file = st.file_uploader('Upload your .pdf file', type="pdf")
    if uploaded_file: 
        file_reader = uploaded_file.read()
        pdf = fitz.open(stream=file_reader, filetype="pdf")
        max_page = pdf.page_count
    else:
        max_page = 500
        pdf = ""
    col_1, col_2 = st.columns(2)
    with col_1:
        start_page_num = st.number_input("Start Page", min_value=1, max_value=max_page)
    with col_2:
        end_page_num = st.number_input("End Page", min_value=1, max_value=max_page)
    st.button("Process", on_click=K.process, args=(pdf, start_page_num-1, end_page_num))
    st.write("Trulens_feedback_score:")
    st.write(st.session_state['trulens_feedback_score'])

with header:
    st.markdown("<h1 style='text-align: center;'>Test Your Knowledge (TUK)</h1>", unsafe_allow_html=True)
    st.subheader('', divider='gray')

with body:
    pdf_display, _, tuk_section = st.columns(3)

    with pdf_display:
        st.subheader('PDF viewer')
        if uploaded_file:
            base64_pdf = base64.b64encode(file_reader).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="650" height="800" type="application/pdf">'
            st.markdown(pdf_display, unsafe_allow_html=True)
    
    with tuk_section:
        st.subheader('Select the correct options')
        for i in st.session_state['options']:
            agree = st.radio(i[0],i[1:5],index=None)
            if agree != None:
                if agree == i[5]:
                    st.success("Correct Answer", icon="✅")
                else:
                    st.error("InCorrect Answer", icon="❌")
        
    
