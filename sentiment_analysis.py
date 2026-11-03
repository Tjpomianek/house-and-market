import ast
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from textblob import TextBlob
import statistics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import seaborn as sns
BASE = Path(__file__).resolve().parent
FIGURES = BASE

FILENAME_stock = BASE / 'stock_data.csv'
FILENAME_WHITE_HOUSE = BASE / 'Whitehouse_scrape_APR_6.csv'

scaler = MinMaxScaler()


def clean_content(text):
    """The scraper saved each document as a list of paragraphs written as
    text. This joins the paragraphs back into one plain string."""
    try:
        parts = ast.literal_eval(text)
        if isinstance(parts, list):
            return " ".join(str(part) for part in parts)
    except (ValueError, SyntaxError):
        pass
    return str(text)

def add_sentiment_to_df(df):
    sent = []
    for i in range(len(df)):
        Blob = TextBlob(df.loc[i, 'Content'])
        polarity = Blob.sentiment.polarity
        sent.append(polarity)
    df['Sentiment'] = sent
    return df


def sentiment_list(df):
    dct = {}
    for i in range(len(df)):
        date = df.loc[i, 'Date']
        sentiment = df.loc[i, 'Sentiment']
        if date in dct:
            dct[date].append(sentiment)
        else:
            dct[date] = [sentiment]
    sent_dct = {}
    for key, value in dct.items():
        sent_dct[key] = ((statistics.mean(value) + 1) / 2) # normalizing
    return sent_dct

def main():

    # Reading in the data
    WHITE_HOUSE_data = pd.read_csv(FILENAME_WHITE_HOUSE)
    Stock_data = pd.read_csv(FILENAME_stock)

    # Joining paragraphs into plain text and removing duplicate documents
    WHITE_HOUSE_data['Content'] = WHITE_HOUSE_data['Content'].apply(clean_content)
    WHITE_HOUSE_data = WHITE_HOUSE_data[WHITE_HOUSE_data['Content'].str.strip() != '']
    WHITE_HOUSE_data = WHITE_HOUSE_data.drop_duplicates().reset_index(drop=True)

    # Cleaning the data
    Stock_data['Open'] = pd.to_numeric(Stock_data['Open'])
    Stock_data = Stock_data.sort_values('Date').reset_index(drop=True)

    # Normalizing
    Stock_data['normalize'] = scaler.fit_transform(Stock_data[['Open']])
    # turning from a string to a float
    Stock_data.loc[:, 'normalize'] = Stock_data.loc[:, 'normalize'].astype(float)
    Stock_data.loc[:, 'Open'] = Stock_data.loc[:, 'Open'].astype(float)

    # Turning the dates in datetime data types
    WHITE_HOUSE_data['Date'] = pd.to_datetime(WHITE_HOUSE_data['Date'])
    Stock_data['Date'] = pd.to_datetime(Stock_data['Date'])

    #Adding a sentiment column to df
    WHITE_HOUSE_data = add_sentiment_to_df(WHITE_HOUSE_data)

    # Getting the sentiment list. Join same dates, then normalize
    sent_dct = sentiment_list(WHITE_HOUSE_data)

    #Keeping the same dates
    sent_df = pd.DataFrame(list(sent_dct.items()), columns=['Date', 'Sentiment'])
    df = Stock_data.merge(sent_df, on='Date').sort_values('Date').reset_index(drop=True)
    df = df.rename(columns={'Open': 'stock_price', 'normalize': 'stock_n'})
    df['sentiment_n'] = scaler.fit_transform(df[['Sentiment']])

    # Daily changes, each divided by its largest absolute value so both
    # fit between -1 and 1 and keep their sign (above 0 = increase)
    df["Price change"] = df['stock_price'].pct_change()
    df["Sent change"] = df['sentiment_n'].diff()
    df["Price change"] = df["Price change"] / df["Price change"].abs().max()
    df["Sent change"] = df["Sent change"] / df["Sent change"].abs().max()

    tick_positions = sorted(set([0, len(df) // 2, len(df) - 1]))
    tick_dates = df.loc[tick_positions, 'Date'].dt.strftime('%Y-%m-%d')
    plt.plot(df['stock_n'], label = "Stock price")
    plt.plot(df['sentiment_n'], label = "Sentiment")
    plt.xticks(tick_positions, tick_dates)
    plt.title('Normalized VOO Opening Price vs Normalized Sentiment')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'price_sentiment.png', dpi=180)
    plt.close()
    
    # Plotting daily changes
    plt.plot(df['Price change'], label = 'Price change')
    plt.plot(df['Sent change'], label = 'Sentiment change')
    plt.xticks(tick_positions, tick_dates)
    plt.axhline(0, color='gray', linewidth=0.8)
    plt.title("Daily Change in VOO Price and Sentiment (Scaled)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'daily_changes.png', dpi=180)
    plt.close()

    # finding the directional agreement
    d1 = np.sign(df['stock_price'].diff())
    d2 = np.sign(df['sentiment_n'].diff())

    corr = []
    for j in range(9):
        pairs = pd.concat([d1, d2.shift(j)], axis=1).dropna()
        corr.append((pairs.iloc[:, 0] == pairs.iloc[:, 1]).mean())
    print(corr)
    plt.bar(range(9), corr)
    plt.axhline(0.5, color='gray', linestyle='--', label='Random chance')
    plt.xticks(range(9))
    plt.ylim(0, 1)
    plt.title('Directional Agreement Between Sentiment and Price Changes')
    plt.ylabel('Proportion with the same direction')
    plt.xlabel('Sentiment leads price by N trading observations')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'lag_agreement.png', dpi=180)
    plt.close()

    vectorizer = TfidfVectorizer(stop_words="english")
    vec_catch = vectorizer.fit_transform(WHITE_HOUSE_data['Content'])

    # Reduce dimensions
    pca = PCA(n_components=2, svd_solver='full')
    reduced = pca.fit_transform(vec_catch.toarray())

    # Assign PCA results back to WHITE_HOUSE_data
    WHITE_HOUSE_data[["pca1", "pca2"]] = reduced
    #print(WHITE_HOUSE_data)

    # Run KMeans
    K = 2
    km = KMeans(n_clusters=K, random_state=42, n_init=10)
    km.fit(WHITE_HOUSE_data[["pca1", "pca2"]])

    # Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x="pca1", y="pca2",
        data=WHITE_HOUSE_data,
        hue=km.labels_,
        palette="plasma", s=150
    )
    plt.title("K-Means Clusters of Documents (TF-IDF and PCA)")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.legend(title="Cluster")
    plt.tight_layout()
    plt.savefig(FIGURES / 'pca_kmeans.png', dpi=180)
    plt.close()

    # Color each document by the first open-to-open price move that comes
    # after its publication date. Opening prices are set before most
    # same-day publications, so the next trading day's open is the first
    # price that could reflect the document. Weekend documents are matched
    # to the following Monday.
    trading = Stock_data[['Date', 'Open']].sort_values('Date').reset_index(drop=True)
    trading['open_change'] = trading['Open'].diff()
    trading = trading.rename(columns={'Date': 'Trade_Date'})

    docs = WHITE_HOUSE_data[['Date']].reset_index().sort_values('Date')
    matched = pd.merge_asof(
        docs, trading[['Trade_Date', 'open_change']],
        left_on='Date', right_on='Trade_Date',
        direction='forward', allow_exact_matches=False
    ).set_index('index')

    WHITE_HOUSE_data['Stock_Movement'] = matched['open_change'].gt(0).where(
        matched['open_change'].notna())

    # Filter out documents with no following trading day in the data
    valid_data = WHITE_HOUSE_data.dropna(subset=['Stock_Movement'])
    
    # Create separate scatter plots for up and down movements
    up_data = valid_data[valid_data['Stock_Movement'] == True]
    down_data = valid_data[valid_data['Stock_Movement'] == False]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(
        up_data["pca1"], 
        up_data["pca2"],
        c='green',
        label='Price Up',
        s=150,

    )
    plt.scatter(
        down_data["pca1"],
        down_data["pca2"],
        c='red',
        label='Price Down or Unchanged',
        s=150,

    )
    plt.title("Documents Colored by Next Trading Day's VOO Price Movement")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'pca_stock_movement.png', dpi=180)
    plt.close()

    print("Saved plots in", FIGURES)

if __name__ == "__main__":
    main()
