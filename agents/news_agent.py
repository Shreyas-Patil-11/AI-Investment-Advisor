import yfinance as yf
import pandas as pd
from typing import Dict

class NewsAgent:
    def __init__(self):
        pass
    
    def run(self, context: Dict):
        """Main run method for MCP integration"""
        try:
            market_data = context.get("market_data", {})
            symbol = market_data.get("symbol", "")
            
            if not symbol:
                context["news_analysis"] = {
                    "sentiment": "neutral",
                    "news_count": 0,
                    "summary": "No symbol provided for news analysis"
                }
                return
            
            news_df = self.get_news(symbol)
            sentiment = self._analyze_sentiment(news_df)
            
            context["news_analysis"] = {
                "sentiment": sentiment,
                "news_count": len(news_df),
                "summary": self._generate_summary(news_df),
                "raw_news": news_df
            }
            
        except Exception as e:
            print(f"News analysis error: {e}")
            context["news_analysis"] = {
                "sentiment": "neutral",
                "news_count": 0,
                "summary": f"Error fetching news: {str(e)}"
            }

    def get_news(self, symbol: str) -> pd.DataFrame:
        """Fetch news for a given stock symbol"""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            news_items = ticker.news
            records = []
            
            for item in news_items[:10]:  # Limit to recent 10 news items
                try:
                    # Handle different news item structures
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    publisher = item.get("publisher", "")
                    
                    # Try alternative structure
                    if not title and "content" in item:
                        content = item["content"]
                        title = content.get("title", "")
                        summary = content.get("summary", "")
                        if "provider" in content:
                            publisher = content["provider"].get("displayName", "")
                    
                    records.append({
                        "title": title,
                        "summary": summary,
                        "publisher": publisher,
                        "date": item.get("pubDate", item.get("providerPublishTime", "")),
                    })
                except Exception as item_error:
                    print(f"Error processing news item: {item_error}")
                    continue
                    
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return pd.DataFrame()
    
    def _analyze_sentiment(self, news_df: pd.DataFrame) -> str:
        """Simple sentiment analysis based on keywords"""
        if news_df.empty:
            return "neutral"
        
        positive_words = ['growth', 'profit', 'gain', 'rise', 'up', 'strong', 'positive', 'buy', 'bullish', 'outperform']
        negative_words = ['loss', 'decline', 'fall', 'down', 'weak', 'negative', 'sell', 'bearish', 'underperform', 'risk']
        
        positive_score = 0
        negative_score = 0
        
        for _, row in news_df.iterrows():
            text = f"{row.get('title', '')} {row.get('summary', '')}".lower()
            
            for word in positive_words:
                positive_score += text.count(word)
            
            for word in negative_words:
                negative_score += text.count(word)
        
        if positive_score > negative_score * 1.2:  # Bias towards positive
            return "positive"
        elif negative_score > positive_score * 1.2:  # Bias towards negative
            return "negative"
        else:
            return "neutral"
    
    def _generate_summary(self, news_df: pd.DataFrame) -> str:
        """Generate a brief summary of the news"""
        if news_df.empty:
            return "No recent news available"
        
        news_count = len(news_df)
        recent_titles = news_df['title'].head(3).tolist()
        recent_titles = [title for title in recent_titles if title and title.strip()]
        
        if recent_titles:
            titles_summary = "; ".join(recent_titles[:2])
            return f"{news_count} recent news items. Latest: {titles_summary}"
        else:
            return f"{news_count} recent news items available"
