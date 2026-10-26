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
FIGURES = BASE / 'figures'
FIGURES.mkdir(exist_ok=True)

FILENAME_stock = BASE / 'stock_data.csv'
FILENAME_WHITE_HOUSE = BASE / 'Whitehouse_scrape_APR_6.csv'

scaler = MinMaxScaler()

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

def keep_same(df1, dct):
    new_lst = []
    date_lst = []
    for i in range(len(df1)):
        # Format the timestamp as string in a specific format
        date_lst.append(str(df1.loc[i + 1, 'Date']))  # or another format
    for key, value in dct.items():
        date = str(key)
        if date in date_lst:
            new_lst.append(value)
    return new_lst

def difference(lst):
    dif_lst = []
    for i in range(2, len(lst)):
        dif = lst[i - 1] - lst[i]
        if dif < 0:
            dif_lst.append(1)
        else:
            dif_lst.append(0)
    return dif_lst
def main():

    # Reading in the data
    WHITE_HOUSE_data = pd.read_csv(FILENAME_WHITE_HOUSE)
    Stock_data = pd.read_csv(FILENAME_stock)

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

    df["Daily Return"] = ((df['stock_price'].diff()))

    df["Sent change"] = (df['sentiment_n'].diff())
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    df['Daily Return'] = (scaler.fit_transform(df[['Daily Return']]) - 0.5)
    #df['Sent change'] = scaler.fit_transform(df[['Sent change']])

    #print(df)
    plt.plot(df['stock_n'], label = "Stock price")
    plt.plot(df['sentiment_n'], label = "Sentiment")
    plt.xticks([0, 26, 53], ["2025-01-21", "2025-02-26", "2025-04-04"])
    plt.title('Normalized stock vs Normalized Sentiment Polarity value')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'price_sentiment.png', dpi=180)
    plt.close()
    
    # fix this plot
    plt.plot(df['Daily Return'], label = 'Daily Return')
    plt.plot(df['Sent change'], label = 'Sentiment change')
    plt.xticks([1, 26, 53], ["2025-01-22", "2025-02-26", "2025-04-04"])
    plt.title("Daily change of stock and Sentiment polarity value Normalized")
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
    plt.bar([0, 1, 2, 3, 4, 5, 6, 7, 8], corr)
    plt.title('Directional agreement between sentiment and price changes')
    plt.ylabel('Proportion with the same direction')
    plt.xlabel('Sentiment leads price by N trading observations')
    plt.tight_layout()
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
    sns.scatterplot(
        x="pca1", y="pca2",
        data=WHITE_HOUSE_data,
        hue=km.labels_,
        palette="plasma", s=150
    )
    plt.title("KMeans Clustering")
    plt.tight_layout()
    plt.savefig(FIGURES / 'pca_kmeans.png', dpi=180)
    plt.close()

    # Create a new scatter plot colored by stock movement
    # Create a mapping of dates to stock movements
    price_change = df['stock_price'].diff()
    stock_movement_dict = dict(zip(df.loc[price_change.notna(), 'Date'],
                                   price_change.dropna() > 0))
    
    # Map each press release date to its corresponding stock movement
    WHITE_HOUSE_data['Stock_Movement'] = WHITE_HOUSE_data['Date'].map(stock_movement_dict)
    
    # Filter out rows where Stock_Movement is NaN
    valid_data = WHITE_HOUSE_data.dropna(subset=['Stock_Movement'])
    
    # Create separate scatter plots for up and down movements
    up_data = valid_data[valid_data['Stock_Movement'] == True]
    down_data = valid_data[valid_data['Stock_Movement'] == False]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(
        up_data["pca1"], 
        up_data["pca2"],
        c='green',
        label='Stock Up',
        s=150,

    )
    plt.scatter(
        down_data["pca1"],
        down_data["pca2"],
        c='red',
        label='Stock Down or Unchanged',
        s=150,

    )
    plt.title("K-Means Features Colored by Stock Movement")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / 'pca_stock_movement.png', dpi=180)
    plt.close()

    print("Saved plots in", FIGURES)

if __name__ == "__main__":
    main()


