# The White House and the Stock Market
 
Original course project by Teddy Pomianek, Neil Keltcher, and Bryan Ma. Revised analysis by Teddy Pomianek.
 
## About the Project
 
This project examines whether the tone of White House publications is related to movements in the stock market.
 
We collected every article, statement, fact sheet, remark, and presidential action published on the White House website between January 20 and April 4, 2025. Each document was scored for positive or negative sentiment, and those scores were compared with the opening price of VOO, an ETF that tracks the S&P 500.
 
## Findings
 
The revised analysis did not find a meaningful relationship between White House sentiment and market movement.
 
- Directional agreement between sentiment and VOO's price was measured on the same day and at delays of up to 8 trading observations. Agreement ranged from approximately 0.37 to 0.58, which is consistent with random chance.
- The largest deviation occurred at a delay of 1, where prices moved opposite to the previous day's sentiment change approximately 63% of the time. Given only about 50 observations and nine delays tested, a single result of this size is likely to occur by chance.
- VOO declined from late February into April, but sentiment did not follow a corresponding trend, and the daily movements did not align.
- K-means divided the documents into two groups based on word usage. When the same documents were colored by the following trading day's price movement, no pattern was visible.
## Methodology
 
- Scraped publication dates and text from the White House website using BeautifulSoup and Requests.
- Joined each document's paragraphs into plain text and removed 50 duplicate documents, leaving 453.
- Retrieved daily VOO prices using yfinance.
- Scored each document's sentiment with TextBlob, which assigns a polarity from -1 (negative) to 1 (positive), and averaged the scores for each day.
- Joined sentiment and prices on date, keeping the 53 trading days that had at least one publication.
- Compared the direction of daily sentiment and price changes at delays of 0 to 8 trading observations.
- Converted the text into TF-IDF features, reduced them to two dimensions with PCA, and grouped the documents with K-means.
## Visualizations
 
### Stock Price and Sentiment
 
VOO's opening price and average daily sentiment, both scaled from 0 to 1 so they can be displayed on the same chart.
 
![Stock price and sentiment](price_sentiment.png)
 
### Daily Changes
 
Daily changes in VOO's price and in sentiment. Both series are scaled to fall between -1 and 1, so values above 0 represent increases and values below 0 represent decreases.
 
![Daily changes](daily_changes.png)
 
### Directional Agreement at Different Delays
 
The proportion of observations in which sentiment and price moved in the same direction. A delay of 0 compares changes on the same day. A delay of 1 compares the previous observation's sentiment change with the current price change, and so on. The dashed line at 0.5 represents the agreement expected from random chance.
 
Because the analysis uses opening prices, which are set before most same-day publications, a delay of 1 is the first comparison in which sentiment precedes the price change.
 
Delays are counted in trading observations rather than calendar days, since only trading days with at least one publication are kept.
 
![Directional agreement](lag_agreement.png)
 
### PCA and K-Means
 
Each point represents a document, positioned according to its word usage. Documents with similar language appear close together. The colors indicate the two groups identified by K-means, which reflect differences in topic and wording rather than positive or negative tone.
 
![PCA and K-means](pca_kmeans.png)
 
### Document Groups and Stock Movement
 
The same chart, colored by whether VOO's price rose at the first market open following each document's publication. Documents published on weekends are matched to the following Monday.
 
![PCA and stock movement](pca_stock_movement.png)
 
## Revisions to the Original Project
 
The [original report](Project_Report.pdf) and the [original code](https://github.com/bryanma24/house-and-market) are our group's course submission. After the course, I reviewed the code, found several errors, and revised the analysis. The graphs and conclusions here differ from the report.
 
### Errors corrected
 
- **Sentiment and prices were misaligned.** The scraped data is stored newest first. The original code kept that order when building the daily sentiment series, then paired it by position with prices stored oldest first. As a result, each day's price was compared with sentiment from a different date. The revised code joins the two series on date.
- **The direction measure compared the wrong quantity.** The original code checked whether each day's change was larger than the previous day's change, rather than whether price and sentiment rose or fell. The revised code compares the sign of each day's price change with the sign of each day's sentiment change.
- **The lag ran in the wrong direction.** The original shift compared each sentiment change with an earlier price change, which tests whether price leads sentiment. Positions before the start of the series also wrapped around to the end of the list. The revised code shifts sentiment so it precedes price and drops observations without a match.
- **Documents were matched to the same day's price change.** The document chart compared each document with that day's opening price change, which is set before most same-day publications, and dropped weekend documents. Documents are now matched to the next trading day's change, and weekend documents to the following Monday.
- **Duplicates and text format.** 50 duplicate documents were removed, and each document's paragraph list was joined into plain text before scoring.
### Other changes
 
- Set a fixed random seed for K-means so the results are reproducible.
- Saved all figures to files and saved the price data to `stock_data.csv` so the analysis can be rerun without downloading.
- Removed the annualized volatility analysis included in the report.
### Differences from the report's description
 
- The report's title references linear regression, but no regression model was fit.
- The report describes daily returns calculated from closing prices, but the code used opening prices. The revised analysis uses opening prices throughout.
- The report concluded that a clear positive relationship existed based on visual inspection of the graphs. With the errors corrected, measuring how often the two series moved in the same direction does not support that conclusion.
## Files
 
| File                          | Description                                                     |
|-------------------------------|-----------------------------------------------------------------|
| `whitehouse_scrape.py`        | Scrapes text and publication dates from the White House website |
| `stock_data.py`               | Downloads VOO prices and saves them to `stock_data.csv`         |
| `sentiment_analysis.py`       | Runs the analysis and saves the graphs                          |
| `Whitehouse_scrape_APR_6.csv` | White House documents, scraped April 6, 2025                    |
| `stock_data.csv`              | Daily VOO prices                                                |
| `*.png`                       | Graphs displayed in this README                                 |
| `Project_Report.pdf`          | Original course report                                          |
| `requirements.txt`            | Required Python packages                                        |
 
## How to Run
 
```
pip install -r requirements.txt
python sentiment_analysis.py
```
 
The graphs are saved to the project folder and replace those displayed in this README. To download new stock data, run `python stock_data.py`. The scraper does not need to be rerun, as the original dataset is included and the White House website has changed since the data was collected.
 
## Limitations
 
This was an exploratory project covering a short period of 53 trading days. TextBlob is a general-purpose sentiment tool and was not designed for political or financial language. White House publications are written by the administration, so their tone is not a neutral measure of events. Even if a pattern had been observed, it would not demonstrate that White House statements cause or predict market movements.
 
