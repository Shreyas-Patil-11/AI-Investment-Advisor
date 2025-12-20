from agents.llm_parser import LLMParserAgent
from agents.growth_stock_agent import GrowthStockAgent
from agents.news_agent import NewsAgent
from agents.technical_agent import TechnicalAgent
from agents.risk_agent import RiskAgent
from agents.decision_agent import DecisionAgent
from data.mappings import stock_symbols, stock_sectors
from typing import Dict, List

class MCPServer:
    def __init__(self, llm_api_key: str):
        try:
            self.llm_parser = LLMParserAgent(llm_api_key)
            self.growth_agent = GrowthStockAgent()
            self.news_agent = NewsAgent()
            self.tech_agent = TechnicalAgent()
            self.risk_agent = RiskAgent()
            self.decision_agent = DecisionAgent()
            self.supported_symbols = list(stock_symbols.keys())
            print("MCP Server initialized successfully")
        except Exception as e:
            print(f"Error initializing MCP Server: {e}")
            raise

    def process(self, user_input: str) -> Dict:
        """Process user input and return investment recommendations"""
        try:
            # Parse user input using LLM
            parsed_context = self.llm_parser.parse(user_input)
            
            investments = parsed_context.get("investments", [])
            current_value = parsed_context.get("current_portfolio_value", 1000)  # Default value
            sector = parsed_context.get("sector_interest", None)
            
            # Create user profile context
            user_profile = {
                "history": investments,
                "current_value": current_value,
                "risk_tolerance": "moderate"
            }
            
            # Assess overall portfolio risk
            risk_level = self.risk_agent.assess_risk(investments, current_value)
            
            recommendations = []
            
            if sector:
                # Find stocks in specific sector
                target_stocks = [sym for sym, sect in stock_sectors.items() if sect.lower() == sector.lower()]
            else:
                # Use growth agent to find potential stocks
                try:
                    growth_stocks = self.growth_agent.find_growing_stocks(sector or "Technology")
                    target_stocks = self._extract_symbols_from_growth_data(growth_stocks)
                except Exception as e:
                    print(f"Growth agent error: {e}")
                    target_stocks = list(stock_symbols.keys())[:3]  # Fallback to first 3 stocks
            
            # Limit to supported stocks and max 5 recommendations
            target_stocks = [s for s in target_stocks if s in self.supported_symbols][:5]
            
            for symbol in target_stocks:
                try:
                    company_name = stock_symbols.get(symbol, symbol)
                    
                    # Create context for this stock
                    context = {
                        "user_profile": user_profile,
                        "market_data": {
                            "symbol": symbol,
                            "company_name": company_name,
                            "sector": stock_sectors.get(symbol, "Unknown")
                        },
                        "memory": []
                    }
                    
                    # Run all agents
                    self.news_agent.run(context)
                    self.tech_agent.run(context)
                    self.risk_agent.run(context)
                    result = self.decision_agent.run(context)
                    
                    recommendations.append({
                        "symbol": symbol,
                        "company": company_name,
                        "sector": stock_sectors.get(symbol, "Unknown"),
                        "recommendation": result.get("recommendation", "Hold"),
                        "confidence": result.get("confidence", "Medium"),
                        "news_sentiment": result.get("news_sentiment", "neutral"),
                        "technical_signal": result.get("technical_signal", "neutral"),
                        "reasoning": result.get("reasoning", "Standard analysis")
                    })
                    
                except Exception as stock_error:
                    print(f"Error analyzing {symbol}: {stock_error}")
                    recommendations.append({
                        "symbol": symbol,
                        "company": stock_symbols.get(symbol, symbol),
                        "sector": stock_sectors.get(symbol, "Unknown"),
                        "recommendation": "Hold",
                        "confidence": "Low",
                        "news_sentiment": "neutral",
                        "technical_signal": "neutral",
                        "reasoning": f"Analysis error: {str(stock_error)}"
                    })
            
            return {
                "user_input": user_input,
                "parsed_context": parsed_context,
                "portfolio_risk_level": risk_level,
                "recommendations_count": len(recommendations),
                "recommendations": recommendations,
                "sector_focus": sector,
                "analysis_summary": self._generate_summary(recommendations, risk_level)
            }
            
        except Exception as e:
            print(f"Error in MCP processing: {e}")
            return {
                "error": str(e),
                "user_input": user_input,
                "recommendations": [],
                "portfolio_risk_level": "unknown"
            }
    
    def analyze_single_stock(self, symbol: str) -> Dict:
        """Analyze a single stock symbol"""
        if symbol not in self.supported_symbols:
            return {
                "error": f"Stock {symbol} not supported. Supported stocks: {', '.join(self.supported_symbols)}"
            }
        
        try:
            company_name = stock_symbols.get(symbol, symbol)
            
            # Create default context
            context = {
                "user_profile": {
                    "history": [],
                    "current_value": 1000,
                    "risk_tolerance": "moderate"
                },
                "market_data": {
                    "symbol": symbol,
                    "company_name": company_name,
                    "sector": stock_sectors.get(symbol, "Unknown")
                },
                "memory": []
            }
            
            # Run all agents
            self.news_agent.run(context)
            self.tech_agent.run(context)
            self.risk_agent.run(context)
            result = self.decision_agent.run(context)
            
            return {
                "symbol": symbol,
                "company": company_name,
                "sector": stock_sectors.get(symbol, "Unknown"),
                "analysis": result,
                "detailed_data": {
                    "news": context.get("news_analysis", {}),
                    "technical": context.get("technical_analysis", {}),
                    "risk": context.get("risk_assessment", {})
                }
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "analysis": {"recommendation": "Hold", "confidence": "Low"}
            }
    
    def _extract_symbols_from_growth_data(self, growth_stocks: List[Dict]) -> List[str]:
        """Extract stock symbols from growth stock data"""
        symbols = []
        for stock in growth_stocks:
            name = stock.get("name", "").upper()
            for symbol in self.supported_symbols:
                if symbol in name or stock_symbols[symbol].upper() in name:
                    symbols.append(symbol)
                    break
        
        # If no matches found, return some default stocks
        if not symbols:
            symbols = self.supported_symbols[:3]
        
        return symbols
    
    def _generate_summary(self, recommendations: List[Dict], risk_level: str) -> str:
        """Generate a summary of the analysis"""
        if not recommendations:
            return f"Portfolio risk level: {risk_level}. No recommendations generated."
        
        buy_count = sum(1 for r in recommendations if 'Buy' in r.get('recommendation', ''))
        sell_count = sum(1 for r in recommendations if 'Sell' in r.get('recommendation', ''))
        hold_count = len(recommendations) - buy_count - sell_count
        
        return f"Portfolio risk: {risk_level}. Analysis of {len(recommendations)} stocks: {buy_count} Buy signals, {sell_count} Sell signals, {hold_count} Hold recommendations."
    
    def get_supported_stocks(self) -> Dict[str, str]:
        """Get list of supported stocks"""
        return stock_symbols.copy()
