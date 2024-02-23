from trulens_eval import OpenAI as fOpenAI
from trulens_eval.app import App
from trulens_eval import Feedback
from trulens_eval.feedback import Groundedness
from trulens_eval import TruLlama
from llama_index import VectorStoreIndex, Document
import streamlit as st
import numpy as np

def concate_docs(pdf, start_page_num, end_page_num, doc_process=False):
    text = ""
    doc = []
    for i in range(start_page_num,end_page_num):
        if doc_process:
            doc.append(Document(text=pdf[i].get_text()))
        else:
            text += pdf[i].get_text()
    if doc_process:
        return doc
    else:
        return text
    
@st.cache_data(show_spinner=False)
def load_db(_pdf):
    return VectorStoreIndex.from_documents(concate_docs(_pdf, 0, _pdf.page_count-1, doc_process=True))

def create_options(response):
    text = response.split('\n\n')
    text_list = list(map(lambda s:s.split('\n'), text))
    for i in range(len(text_list)):
        for j in range(6):
            if j == 0:
                text_list[i][j] = text_list[i][j].strip()
            elif j == 5:
                text_list[i][j] = text_list[i][j].strip()[11:]
            else:
                text_list[i][j] = text_list[i][j].strip()[3:]
    return text_list

def process(pdf, start_page_num, end_page_num):
    openai = fOpenAI()
    index = load_db(pdf)
    query_engine = index.as_query_engine()
    context = App.select_context(query_engine)
    grounded = Groundedness(groundedness_provider=openai)
    f_groundedness = (Feedback(grounded.groundedness_measure_with_cot_reasons)
                      .on(context.collect()) 
                      .on_output()
                      .aggregate(grounded.grounded_statements_aggregator))
    
    f_qa_relevance = Feedback(openai.relevance).on_input_output()

    f_qs_relevance = (Feedback(openai.qs_relevance)
                      .on_input()
                      .on(context)
                      .aggregate(np.mean)
        )
    tru_query_engine_recorder = TruLlama(query_engine, 
                                         app_id='TUK', 
                                         feedbacks=[f_groundedness, f_qa_relevance, f_qs_relevance])
    
    with tru_query_engine_recorder as recording:
            response = query_engine.query(f'''You are an Analyst.
                                              Content: {concate_docs(pdf, start_page_num, end_page_num)}               
                                              Job: Analyse the content and generate few multiple choice questions with answers.
                                              Example: what is 2+2 equals?
                                                       A) 1
                                                       B) 3
                                                       C) 4
                                                       D) 5
                                                       Answer: C) 4''')
    rec = recording.get() 
    for feedback, feedback_result in rec.wait_for_feedback_results().items():
        st.session_state['trulens_feedback_score'][feedback.name] = feedback_result.result
       
    st.session_state['options'] = create_options(response.response)
    

