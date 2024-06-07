import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

# Step 1: Gather historical stock price data for the company
def get_stock_data(ticker, period="1y", interval="1d"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    return df

# Step 2: Apply technical analysis indicators
def apply_technical_indicators(df):
    df['SMA_50'] = ta.sma(df['Close'], length=50)  # Simple Moving Average
    df['SMA_200'] = ta.sma(df['Close'], length=200)  # Simple Moving Average
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = ta.macd(df['Close'])  # MACD
    df['RSI'] = ta.rsi(df['Close'])  # Relative Strength Index
    # Bollinger Bands
    df['BB_upper'] = ta.bbands(df['Close'])['BBU_5_2.0']
    df['BB_middle'] = ta.bbands(df['Close'])['BBM_5_2.0']
    df['BB_lower'] = ta.bbands(df['Close'])['BBL_5_2.0'] 
    return df

# Step 3: Implement trading strategies based on technical analysis signals
def generate_signals(df):
    df['Signal'] = 'Hold'
    df['Buy_Price'] = None
    df['Sell_Price'] = None
    
    for i in range(200, len(df)):
        buy_conditions = [
            df['Close'][i] > df['SMA_50'][i],  # Price above 50-day SMA
            df['Close'][i] > df['SMA_200'][i],  # Price above 200-day SMA
            df['MACD'][i] > df['MACD_signal'][i],  # MACD above MACD signal
            df['RSI'][i] < 30,  # RSI indicates oversold conditions
            df['Close'][i] < df['BB_lower'][i]  # Price below lower Bollinger Band
        ]
        
        sell_conditions = [
            df['Close'][i] < df['SMA_50'][i],  # Price below 50-day SMA
            df['Close'][i] < df['SMA_200'][i],  # Price below 200-day SMA
            df['MACD'][i] < df['MACD_signal'][i],  # MACD below MACD signal
            df['RSI'][i] > 70,  # RSI indicates overbought conditions
            df['Close'][i] > df['BB_upper'][i]  # Price above upper Bollinger Band
        ]
        
        if all(buy_conditions):
            df.at[df.index[i], 'Signal'] = 'Buy'
            df.at[df.index[i], 'Buy_Price'] = df['Close'][i]
        elif all(sell_conditions):
            df.at[df.index[i], 'Signal'] = 'Sell'
            df.at[df.index[i], 'Sell_Price'] = df['Close'][i]
    
    return df

# Visualization
def plot_signals(df, ticker):
    plt.figure(figsize=(14, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['SMA_50'], label='50-Day SMA')
    plt.plot(df['SMA_200'], label='200-Day SMA')
    plt.plot(df['BB_upper'], label='Bollinger Upper Band', linestyle='--')
    plt.plot(df['BB_middle'], label='Bollinger Middle Band', linestyle='--')
    plt.plot(df['BB_lower'], label='Bollinger Lower Band', linestyle='--')
    plt.scatter(df[df['Position'] == 1].index, df[df['Position'] == 1]['Close'], label='Buy Signal', marker='^', color='g')
    plt.scatter(df[df['Position'] == -1].index, df[df['Position'] == -1]['Close'], label='Sell Signal', marker='v', color='r')
    plt.title(f'{ticker} Price and Technical Indicators')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(df['MACD'], label='MACD')
    plt.plot(df['MACD_signal'], label='MACD Signal')
    plt.bar(df.index, df['MACD_hist'], label='MACD Histogram', color='gray')
    plt.title('MACD')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def TechincalAnalysis(Company):
    df = get_stock_data(Company)
    df = apply_technical_indicators(df)
    return df
    
# # Main function to run the technical analyzer
# def main():
#     ticker = "RELIANCE"
#     df = get_stock_data(ticker)
#     df = apply_technical_indicators(df)
#     df = generate_signals(df)
#     # plot_signals(df, ticker)
#     print(df['Signal'])

# if __name__ == "__main__":
#     main()
