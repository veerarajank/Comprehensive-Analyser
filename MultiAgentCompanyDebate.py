from groq import Groq
from NewsAnalyser import SentimentAnalysis
from TechnicalAnalyser import TechincalAnalysis
import yfinance as yf
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict, Optional
import streamlit as st

load_dotenv()
# Create the Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

company: str = st.chat_input("Enter a prompt here")

# State
class GraphState(TypedDict):
    history: Optional[str] = None
    company: str = None
    prop_expert: str = None
    prop_fundamental: str = None
    prop_sentiment: str = None
    prop_technical: str = None

workflow = StateGraph(GraphState)

def llm(role, user_input):
    new_message = []
    new_message.append({
    "role": "system",
    "content": role
   })

     # Append the user input to the chat history
    new_message.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(model="llama3-70b-8192",
                                            messages=new_message,
                                            max_tokens=32768,
                                            temperature=1.2)
    new_message.append({
      "role": "assistant",
      "content": response.choices[0].message.content
    })
    return response.choices[0].message.content

def expert(state):
    history = state.get('history', '').strip()
    company = state.get('company', '').strip()
    prompt = "Analysis:{}".format(history)
    result = llm("You are expert in stock market. Please compare the analysis provided by the Sentiment Analyser, Technical Analyser, and Fundamental Analyser regarding a specific company. Based on the sentiment, technical indicators, and fundamental metrics, provide a recommendation on whether to buy, sell, or hold the company's stock and explain in detail about your decision in precise.", prompt)
    return {"history": history+"\n Expert:\n"+result, "prop_company": company, "prop_expert": result}

def sentiment(state):
    history = state.get('history', '').strip()
    company = state.get('company', '').strip()
    prompt = " Analysis:{}".format(SentimentAnalysis(company))
    result = llm("You are an expert in sentiment analysis using News from different sources. you are in debate with Technical analyzer and fundamental analyzer. provide the recommendation on whether we need to buy, sell or hold the company and explain in detail about your decision in precise.", prompt)
    return {"history": history+"\n Sentiment Analysis:\n"+result, "company": company, "prop_sentiment": result}

def technical(state):
    history = state.get('history', '').strip()
    company = state.get('company', '').strip()
    prompt = " Analysis:{}".format(TechincalAnalysis(company))
    result = llm("You are an expert in technical analysis using technical indicators. you are in debate with Sentimental analyzer and fundamental analyzer. provide the recommendation on whether we need to buy, sell or hold the company based on the analysis you are done and explain in detail about your decision in precise.", prompt)
    return {"history": history+"\n Technical Analysis:\n"+result, "company": company, "prop_technical": result}

def fundamental(state):
    history = state.get('history', '').strip()
    company = state.get('company', '').strip()
    prompt = " Analysis:{}".format(yf.Ticker(company).info)
    result = llm("You are an expert in fundamental analysis using company financial information. you are in debate with Sentimental analyzer and technical analyzer. provide the recommendation on whether we need to buy, sell or hold the company based on the analysis you are done and explain in detail about your decision in precise.", prompt)
    return {"history": history+"\n Fundamental Analysis:\n"+result, "company": company, "prop_fundamental": result}

# def deployment_ready(state):
#     if state.get('technical', '').strip()!='':
#         print(state.get('technical', '').strip())

workflow.add_node("sentiment_analyser",sentiment)
workflow.add_node("technical_analyser",technical)
workflow.add_node("fundamental_analyser",fundamental)
workflow.add_node("expert",expert)

# workflow.add_conditional_edges("sentiment_analyser", deployment_ready)
workflow.set_entry_point("sentiment_analyser")
workflow.add_edge("sentiment_analyser", "technical_analyser")
workflow.add_edge("technical_analyser", "fundamental_analyser")
workflow.add_edge("fundamental_analyser", "expert")
workflow.add_edge("expert", END)

app = workflow.compile()
inputs = {"history": "", "company": company, "prop_sentiment": "", "prop_technical": "", "prop_fundamental": "", "prop_expert": ""}

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"]==os.getenv("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

st.header("Comprehensive Analysis Partner")
st.write("Hello! Good day! We are team of specialists, Sentiment Analyser (S) , Technical Analyser (T), Fundamental Analyser(F) and Expert(E) in the field of financial markets.  Which Company do you want to analyze ? Please provide the respective code for the company. For example for Apple Inc, please provide as AAPL")

if company:    
    st.chat_message("User").write(company)
    data = yf.Ticker(company).history(period="1mo", interval="1d")
    if data.empty:
        st.chat_message("Assistant").write(llm("You are Yahoo finance expert. suggest the stock exchange code from that?", f"Company Name: {company}"))
    else:
        for s in app.stream(inputs):
         if "prop_sentiment" in list(s.values())[0]:
          st.chat_message("Sentiment Analyser").write(list(s.values())[0]["prop_sentiment"])
         if "prop_technical" in list(s.values())[0]:
          st.chat_message("Technical Analyser").write(list(s.values())[0]["prop_technical"])
         if "prop_fundamental" in list(s.values())[0]:
          st.chat_message("Fundamental Analyser").write(list(s.values())[0]["prop_fundamental"])
         if "prop_expert" in list(s.values())[0]:
          st.chat_message("Expert").write(list(s.values())[0]["prop_expert"])

