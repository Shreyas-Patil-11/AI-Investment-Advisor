from typing import Dict

class DecisionAgent:
    def __init__(self):
        pass
    
    def run(self, context: Dict) -> Dict:
        """Main run method for MCP integration"""
        try:
            # Extract data from context
            market_data = context.get("market_data", {})
            news_analysis = context.get("news_analysis", {})
            technical_analysis = context.get("technical_analysis", {})
            risk_assessment = context.get("risk_assessment", {})
            
            symbol = market_data.get("symbol", "Unknown")
            news_sentiment = news_analysis.get("sentiment", "neutral")
            technical_signal = technical_analysis.get("signal", "neutral")
            risk_level = risk_assessment.get("risk_level", "moderate")
            
            # Generate final recommendation
            recommendation = self._make_decision(
                technical_analysis.get("indicators", {}),
                news_sentiment,
                risk_level,
                technical_signal
            )
            
            # Store result in context
            result = {
                "symbol": symbol,
                "news_sentiment": news_sentiment,
                "technical_signal": technical_signal,
                "risk_level": risk_level,
                "recommendation": recommendation,
                "confidence": self._calculate_confidence(news_sentiment, technical_signal, risk_level),
                "reasoning": self._generate_reasoning(news_sentiment, technical_signal, risk_level, recommendation)
            }
            
            context["final_decision"] = result
            return result
            
        except Exception as e:
            print(f"Decision making error: {e}")
            result = {
                "symbol": "Unknown",
                "news_sentiment": "neutral",
                "technical_signal": "neutral",
                "risk_level": "moderate",
                "recommendation": "Hold",
                "confidence": "Low",
                "reasoning": f"Error in analysis: {str(e)}"
            }
            context["final_decision"] = result
            return result

    def recommend(self, technical, news, risk_level):
        """Legacy method for backward compatibility"""
        # Simple rule-based for demo purposes
        close = technical.get("Close", 0)
        rsi = technical.get("RSI_14", 50)
        
        # Handle news DataFrame or dict
        try:
            if hasattr(news, 'empty'):
                positive_news = not news.empty and any("positive" in str(n).lower() for n in news["summary"].fillna("") if str(n).strip())
            else:
                positive_news = news.get("sentiment", "neutral") == "positive"
        except Exception:
            positive_news = False

        if risk_level == "high":
            return "Avoid"

        if rsi < 30 and positive_news:
            return "Buy"
        elif rsi > 70:
            return "Sell"
        else:
            return "Hold"
    
    def _make_decision(self, technical_indicators: dict, news_sentiment: str, risk_level: str, technical_signal: str) -> str:
        """Make final investment decision based on all inputs"""
        
        # High risk override
        if risk_level == "high":
            return "Avoid"
        
        # Score-based decision system
        score = 0
        
        # Technical analysis contribution (40%)
        if technical_signal == "buy":
            score += 2
        elif technical_signal == "sell":
            score -= 2
        
        # News sentiment contribution (30%)
        if news_sentiment == "positive":
            score += 1.5
        elif news_sentiment == "negative":
            score -= 1.5
        
        # Risk level adjustment (30%)
        if risk_level == "low":
            score += 1
        elif risk_level == "moderate":
            score += 0
        else:  # high risk already handled above
            score -= 1
        
        # RSI specific check
        rsi = technical_indicators.get("RSI_14", 50)
        if rsi < 25:  # Extremely oversold
            score += 1
        elif rsi > 75:  # Extremely overbought
            score -= 1
        
        # Price momentum check
        price_change_5d = technical_indicators.get("Price_Change_5D", 0)
        if price_change_5d > 10:  # Strong upward momentum
            score += 0.5
        elif price_change_5d < -10:  # Strong downward momentum
            score -= 0.5
        
        # Decision thresholds
        if score >= 2:
            return "Strong Buy"
        elif score >= 1:
            return "Buy"
        elif score <= -2:
            return "Strong Sell"
        elif score <= -1:
            return "Sell"
        else:
            return "Hold"
    
    def _calculate_confidence(self, news_sentiment: str, technical_signal: str, risk_level: str) -> str:
        """Calculate confidence level of the recommendation"""
        alignment_count = 0
        
        # Check alignment between signals
        if news_sentiment in ["positive", "negative"] and technical_signal in ["buy", "sell"]:
            if (news_sentiment == "positive" and technical_signal == "buy") or \
               (news_sentiment == "negative" and technical_signal == "sell"):
                alignment_count += 2
            else:
                alignment_count -= 1
        
        if risk_level == "low":
            alignment_count += 1
        elif risk_level == "high":
            alignment_count -= 1
        
        if alignment_count >= 2:
            return "High"
        elif alignment_count >= 0:
            return "Medium"
        else:
            return "Low"
    
    def _generate_reasoning(self, news_sentiment: str, technical_signal: str, risk_level: str, recommendation: str) -> str:
        """Generate human-readable reasoning for the recommendation"""
        reasons = []
        
        if risk_level == "high":
            reasons.append("High portfolio risk detected")
        
        if technical_signal == "buy":
            reasons.append("Technical indicators suggest upward trend")
        elif technical_signal == "sell":
            reasons.append("Technical indicators suggest downward trend")
        
        if news_sentiment == "positive":
            reasons.append("Positive news sentiment")
        elif news_sentiment == "negative":
            reasons.append("Negative news sentiment")
        
        if not reasons:
            reasons.append("Mixed or neutral signals across all indicators")
        
        return f"Recommendation: {recommendation}. " + "; ".join(reasons) + "."
    
