import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Initialize the Sentiment Intensity Analyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Function to get news articles from NewsAPI
def get_news(api_key, company, from_date, to_date):
    url = f"https://newsapi.org/v2/everything?q={company}&from={from_date}&to={to_date}&sortBy=popularity&apiKey={api_key}"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles']
    return articles

# Function to scrape additional news sources
def scrape_news(company, num_articles=5):
    url = f"https://www.google.com/search?q={company}+news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find_all('h3', limit=num_articles)
    news_articles = []
    for headline in headlines:
        news_articles.append({
            'title': headline.get_text(),
            'url': headline.find_parent('a')['href'] if headline.find_parent('a')!=None else headline.find_parent('a')
        })
    return news_articles

# Function to analyze sentiment
def analyze_sentiment(articles):
    sentiment_scores = []
    sentiment = {}
    for article in articles:
        title = article['title']
        if "publishedAt" in article:
            sentiment['date'] = article['publishedAt']
        else:
            sentiment['date'] = "2024-06-01T18:01:11Z"
        sentiment = sia.polarity_scores(title)
        sentiment_scores.append(sentiment)
    return sentiment_scores

# Function to plot sentiment
def plot_sentiment(sentiment_scores):
    df = pd.DataFrame(sentiment_scores)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df['compound'].plot(kind='bar', color=df['compound'].apply(lambda x: 'g' if x >= 0 else 'r'))
    plt.title('Sentiment Analysis of News Articles')
    plt.ylabel('Sentiment Score')
    plt.xlabel('Date')
    plt.show()

# Function to generate buy/sell signals
def generate_signals(sentiment_scores, threshold=0.05):
    df = pd.DataFrame(sentiment_scores)
    avg_sentiment = df['compound'].mean()
    if avg_sentiment > threshold:
        signal = "Buy"
    elif avg_sentiment < -threshold:
        signal = "Sell"
    else:
        signal = "Hold"
    return signal

def SentimentAnalysis(Company):
    api_key = 'a1cd39cdca034e529a2c0c67de2dd7c2'  # Replace with your NewsAPI key
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')
     # Get news articles
    news_articles = get_news(api_key, Company, from_date, to_date)
    # Scrape additional news
    scraped_articles = scrape_news(Company)
    news_articles.extend(scraped_articles)
    # Analyze sentiment
    sentiment_scores = analyze_sentiment(news_articles)

    df = pd.DataFrame(sentiment_scores)
    avg_sentiment = df['compound'].mean()
    return {"average_sentiment_score": avg_sentiment, "recommendation": generate_signals(sentiment_scores)}
# Main function
# def main():
#     api_key = 'a1cd39cdca034e529a2c0c67de2dd7c2'  # Replace with your NewsAPI key
#     company = 'NFG'
#     from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
#     to_date = datetime.now().strftime('%Y-%m-%d')

#     # Get news articles
#     news_articles = get_news(api_key, company, from_date, to_date)
    
#     # Scrape additional news
#     scraped_articles = scrape_news(company)
#     news_articles.extend(scraped_articles)

#     # Analyze sentiment
#     sentiment_scores = analyze_sentiment(news_articles)

#     # Print sentiment analysis
#     for article, sentiment in zip(news_articles, sentiment_scores):
#         print(f"Title: {article['title']}")
#         print(f"Sentiment: {sentiment}")
#         print()

#     # Plot sentiment
#     # plot_sentiment(sentiment_scores)
#     generate_signals(sentiment_scores)

# if __name__ == '__main__':
#     main()
