from duckduckgo_search import DDGS
from typing import List, Dict

class GrowthStockAgent:
    def __init__(self):
        pass

    def find_growing_stocks(self, sector: str, max_results=3) -> List[Dict]:
        query = f"Top growing companies in {sector} India 2025"
        results = DDGS().text(keywords=query, max_results=max_results)

        stocks = []
        for r in results:
            title = r.get("title", "")
            snippet = r.get("body", "")
            # crude extraction: find symbols in title (must improve for production)
            # For demo, assume user will verify recommended stocks
            stocks.append({"name": title, "reason": snippet})

            if len(stocks) >= max_results:
                break
        return stocks
