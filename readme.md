
Project: Resume & JD Matcher Bot

This project uses RAG (Retrieval-Augmented Generation) with Gemini and Pinecone to build an intelligent chatbot that compares a resume with a job description. It provides a match score, gives reasoning behind the score, and suggests improvements if necessary.

Step-by-Step Breakdown

1. Setup and Imports
The project starts by importing necessary modules:
- streamlit: for building the web interface.
- os and dotenv: to securely load API keys from environment variables.
- langchain: provides tools for document loading, text splitting, vector storage, retrieval, and LLM chaining.
- google.generativeai: used for Gemini LLM and embeddings.
- pinecone: used for storing and retrieving embedded text vectors efficiently.

2. Streamlit UI Setup
- Sets up the Streamlit web app title and layout.
- Allows the user to upload a resume in PDF format.
- Provides a text area for the user to paste the job description.

3. Document Handling
- The uploaded resume is saved locally as a temporary PDF file.
- The PDF is loaded using PyPDFLoader from LangChain.
- The text is split into smaller chunks using RecursiveCharacterTextSplitter so it can be processed efficiently by the embedding model.

4. Embeddings Generation
- Gemini’s embedding model (embedding-001) is used to convert the text chunks into vector representations.
- These embeddings help compare the semantic meaning of resume content and JD.

5. Storing in Pinecone
- The embedded text chunks are stored in Pinecone using PineconeVectorStore.
- Pinecone enables fast similarity search for later retrieval based on user query.

6. LLM Setup
- Gemini LLM (gemini-2.0-flash) is initialized with safety settings to avoid harmful content.
- A custom prompt template is defined to guide the LLM's behavior.
  - It instructs the model to focus on resume-JD matching, generate a strict score, and suggest improvements.

7. Retriever and QA Chain
- MultiQueryRetriever is used to retrieve different types of relevant context from the resume.
- RetrievalQA from LangChain combines the retriever, prompt, and LLM to answer the user's query in context of the resume.

8. User Query Handling
- The user pastes a JD or question into a text area.
- When submitted, the system retrieves relevant resume chunks, feeds them to the LLM along with the JD, and returns:
  - A detailed answer
  - A match score
  - Suggested improvements (if score is below 80)
- Also displays the chunks from the resume that were used to generate the response.

Summary of Key Modules

|           Module               |               Purpose                                         |
|------------------------------  |-----------------------------------------------------          |
| streamlit                      | Web interface and interaction                                 |
| PyPDFLoader                    | Loads resume PDF into text                                    |
| RecursiveCharacterTextSplitter | Splits resume into smaller, processable text chunks           |
| GoogleGenerativeAIEmbeddings   | Converts text to embeddings for semantic comparison           |
| PineconeVectorStore            | Stores and retrieves vectorized text using Pinecone           |
| ChatGoogleGenerativeAI         | Calls the Gemini model to generate intelligent responses      |
| MultiQueryRetriever            | Retrieves diverse relevant context for better LLM responses   |
| RetrievalQA                    | Ties everything together to perform RAG (retrieval + answer)  | 
