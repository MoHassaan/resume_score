import streamlit as st
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate # Prompt template
from langchain.text_splitter import RecursiveCharacterTextSplitter # Chunks
from langchain.document_loaders import PyPDFLoader  # Load the text
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import VectorDBQA,RetrievalQA, LLMChain # Chains and Retrival ans
from langchain.retrievers.multi_query import MultiQueryRetriever # Multiple Answers
from langchain_google_genai import ChatGoogleGenerativeAI # GenAI model to retrive
from langchain_google_genai import GoogleGenerativeAIEmbeddings # GenAI model to conver words
from langchain_pinecone import PineconeVectorStore
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory

# load keys
load_dotenv()
gemini_key = st.secrets["GEMINI_API_KEY"]
pinecone_key = st.secrets["PINECONE_API_KEY"]
index_name = "langchain-rag-geminii"

# Set up Streamlit page
st.set_page_config(page_title="Resume & JD Matcher Bot", layout="centered")
st.title("Resume & JD Matcher Bot")
st.markdown("Upload a Resume PDF")

# Upload PDF
uploaded_file = st.file_uploader("Upload a Resume PDF", type="pdf")


if uploaded_file:
    # Save uploaded file temporarily
    with open("current_resume.pdf", "wb") as f:
        f.write(uploaded_file.read())


    # Load and split PDF
    loader = PyPDFLoader("current_resume.pdf")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    texts = text_splitter.split_documents(documents)

    # Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model='models/embedding-001',
        google_api_key=gemini_key,
        task_type="retrieval_document"
    )


    # Store in Pinecone
    os.environ["PINECONE_API_KEY"] = pinecone_key
    vectordb = PineconeVectorStore.from_documents(
        documents=texts,
        embedding=embeddings,
        index_name=index_name
    )


    # Gemini LLM
    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }


    chat_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=gemini_key,
        temperature=0.3,
        safety_settings=safety_settings
    )

    # Prompt
    prompt_template = """
You are an intelligent assistant specialized in analyzing and summarizing Resume for job in Indian company.

## Instructions:
Use the **Job Description** in short JD provided below to compare the resume and job description. 
Focus on the Job description and resume from the document.
Genetrate a concise and relevant answer based on the context provided.
If the resume matches the job description, provide a score between 0 to 100.
Be a little strict in your evaluation, and prpovide a little less score than expected.
Provide a detailed explanation of the match score.
Suggest improvements to the resume if the score is below 80.

If the answer is **not found in the context**, respond with:
**"The answer is not available in the provided document."**

## Additional Guidelines:
- Avoid political bias or speculation
- Focus on budgetary figures, schemes, reforms, and policy announcements
- Do not infer or hallucinate numbers or statements

---

### Context:
{context}

### Question:
{question}

### Answer:
"""

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # Retriever
    retriever = MultiQueryRetriever.from_llm(
        retriever=vectordb.as_retriever(search_kwargs={"k": 5}),
        llm=chat_model
    )

    # QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=chat_model,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    # Query input
    user_query = text = st.text_area(
    label="Enter your text here",
    height=200,  # Increase height as needed
    max_chars=1000,  # Optional: limit characters
    placeholder="Paste your long text or paragraph here...",
    key="query"
)


    if user_query:
        with st.spinner("Fetching answer..."):
            response = qa_chain.invoke({"query": user_query})
            st.markdown("### 📌 Answer:")
            st.write(response["result"])

            with st.expander("🔍 Source Snippets"):
                for i, doc in enumerate(response["source_documents"]):
                    st.markdown(f"**Chunk {i+1}:**")
                    st.write(doc.page_content[:500])

else:
    st.info("Please upload a resume PDF to begin.")