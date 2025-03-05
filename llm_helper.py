from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq

groq_api_key= os.environ.get("GROPQ_API_KEY")

llm = ChatGroq(model="llama3-70b-8192",groq_api_key = groq_api_key)

if __name__ == "__main__":
    response = llm.invoke("Two most important rules to become rich")
    print(response.content)