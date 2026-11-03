# The White House and the Stock Market

Created by Teddy Pomianek, Neil Keltcher, and Bryan Ma.

## About the Project

Does the tone of White House publications line up with how the stock market moves? That's the question we set out to answer.

We collected every article, statement, fact sheet, remark, and presidential action the White House published between January 20 and April 4, 2025. Then we scored how positive or negative each one sounded and compared those scores with the price of VOO, an ETF that tracks the S&P 500.

## What We Found

Short answer: we didn't find a meaningful connection.

- We checked how often sentiment and VOO's price moved in the same direction, both on the same day and with delays of up to 8 trading days. Agreement ranged from about 0.37 to 0.58, which is roughly what you'd expect from flipping a coin.
- The biggest outlier came at a delay of 1, where prices moved opposite to the previous day's sentiment about 63% of the time. With only about 50 observations and nine delays tested, one result like that is easy to get by chance.
- VOO dropped from late February into April, but sentiment didn't follow the same trend, and the day-to-day movements didn't line up.
- K-means sorted the documents into two groups based on their wording. When we colored those same documents by whether the market went up the next day, no pattern showed up.

## How We Did It

- Scraped publication dates and text from the White House website with BeautifulSoup and Requests.
- Cleaned the text and removed duplicate documents.
- Pulled daily VOO prices with yfinance.
- Scored each document's sentiment with TextBlob, which rates text from -1 (negative) to 1 (positive), and averaged the scores for each day.
- Kept only the dates that had both trading data and at least one publication.
- Compared the direction of daily sentiment and price changes at delays of 0 to 8 trading days.
- Turned the text into TF-IDF features, reduced them to two dimensions with PCA, and grouped the documents with K-means.

## Visualizations

### Stock Price and Sentiment

VOO's opening price and average daily sentiment, both scaled from 0 to 1 so they fit on the same chart.

![Stock price and sentiment](price_sentiment.png)

### Daily Changes

How much VOO's price and sentiment changed each day. Both are scaled to fit between -1 and 1, so anything above 0 is an increase and anything below 0 is a decrease.

![Daily changes](daily_changes.png)

### Directional Agreement at Different Delays

How often sentiment and price moved in the same direction. A delay of 0 compares the same day. A delay of 1 compares the previous day's sentiment change with today's price change, and so on. The dashed line at 0.5 shows what random chance would look like.

One thing to keep in mind: we used opening prices, and the market opens before most of the day's publications come out. That means a delay of 1 is the first real test of whether sentiment comes before a price move.

![Directional agreement](lag_agreement.png)

### PCA and K-Means

Each dot is a document, placed based on the words it uses. Documents that sound alike end up close together. The colors show the two groups K-means found, which reflect topics and wording rather than whether a document sounds positive or negative.

![PCA and K-means](pca_kmeans.png)

### Document Groups and Stock Movement

The same chart, but colored by whether VOO's price went up at the next market open after each document was published. Weekend documents are matched to the following Monday.

![PCA and stock movement](pca_stock_movement.png)

## Changes from the Original Report

The [original report](Project_Report.pdf) is what we turned in for class. Since then, we've revisited the analysis and fixed some problems, so the graphs and conclusions here are different:

- Fixed how publications were matched to trading days and corrected the delay calculation.
- Removed duplicate documents and cleaned up the text format.
- Matched documents to the next trading day's price move, since opening prices are set before most same-day publications.
- Used freshly downloaded VOO prices, and opening prices instead of closing prices.
- Dropped the annualized volatility analysis from the report.
- Added the PCA and K-means analysis, which isn't in the report.
- The report's title mentions linear regression, but we never actually fit a regression model.
- The report concluded there was a clear positive relationship. After the fixes, the data doesn't support that.

## Files

| File | Description |
| --- | --- |
| `whitehouse_scrape.py` | Scrapes text and publication dates from the White House website |
| `stock_data.py` | Downloads VOO prices and saves them to `stock_data.csv` |
| `sentiment_analysis.py` | Runs the analysis and saves the graphs |
| `Whitehouse_scrape_APR_6.csv` | White House documents, scraped April 6, 2025 |
| `stock_data.csv` | Daily VOO prices |
| `*.png` | Graphs shown in this README |
| `Project_Report.pdf` | Original course report |
| `requirements.txt` | Required Python packages |

## How to Run

```bash
pip install -r requirements.txt
python sentiment_analysis.py
```

The graphs save to the project folder and replace the ones shown here. To download fresh stock data, run `python stock_data.py`. You don't need to rerun the scraper since the original data is included, and the White House site has changed since we collected it anyway.

## Limitations

This was an exploratory project with a short window of about 50 trading days. TextBlob is a general sentiment tool and wasn't built for political or financial language. White House publications are written by the administration itself, so their tone isn't a neutral read on what's happening. Even if we had found a pattern, it wouldn't prove that White House statements cause or predict market moves.