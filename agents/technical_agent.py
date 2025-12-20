import yfinance as yf
import pandas as pd
from typing import Dict
import numpy as np

class TechnicalAgent:
    def __init__(self, period_months=6):
        self.period = period_months
    
    def run(self, context: Dict):
        """Main run method for MCP integration"""
        try:
            market_data = context.get("market_data", {})
            symbol = market_data.get("symbol", "")
            
            if not symbol:
                context["technical_analysis"] = {
                    "signal": "neutral",
                    "indicators": {},
                    "summary": "No symbol provided for technical analysis"
                }
                return
            
            indicators = self.get_technical_indicators(symbol)
            signal = self._generate_signal(indicators)
            
            context["technical_analysis"] = {
                "signal": signal,
                "indicators": indicators,
                "summary": self._generate_summary(indicators, signal)
            }
            
        except Exception as e:
            print(f"Technical analysis error: {e}")
            context["technical_analysis"] = {
                "signal": "neutral",
                "indicators": {},
                "summary": f"Error in technical analysis: {str(e)}"
            }

    def get_technical_indicators(self, symbol: str) -> dict:
        """Calculate technical indicators for a stock"""
        try:
            data = yf.download(f"{symbol}.NS", period=f"{self.period}mo", interval="1d", progress=False)
            if data.empty:
                return {}

            close = data["Close"]
            high = data["High"]
            low = data["Low"]
            volume = data["Volume"]
            
            # Calculate various technical indicators
            sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else close.mean()
            sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else close.mean()
            rsi = self.calculate_rsi(close).iloc[-1] if len(close) >= 14 else 50
            
            # Bollinger Bands
            bb_upper, bb_lower = self.calculate_bollinger_bands(close)
            
            # MACD
            macd_line, macd_signal = self.calculate_macd(close)
            
            # Price change percentage with safe indexing
            try:
                price_change_1d = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100) if len(close) > 1 else 0
            except (IndexError, ZeroDivisionError):
                price_change_1d = 0
                
            try:
                price_change_5d = ((close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] * 100) if len(close) > 5 else 0
            except (IndexError, ZeroDivisionError):
                price_change_5d = 0

            # Ensure all values are scalars (float/int)
            return {
                "Close": float(close.iloc[-1]),
                "SMA_20": float(sma_20) if pd.notna(sma_20) else 0.0,
                "SMA_50": float(sma_50) if pd.notna(sma_50) else 0.0,
                "RSI_14": float(rsi) if pd.notna(rsi) else 50.0,
                "BB_Upper": float(bb_upper) if pd.notna(bb_upper) else 0.0,
                "BB_Lower": float(bb_lower) if pd.notna(bb_lower) else 0.0,
                "MACD": float(macd_line) if pd.notna(macd_line) else 0.0,
                "MACD_Signal": float(macd_signal) if pd.notna(macd_signal) else 0.0,
                "Volume": float(volume.iloc[-1]) if len(volume) > 0 and pd.notna(volume.iloc[-1]) else 0.0,
                "Price_Change_1D": float(price_change_1d),
                "Price_Change_5D": float(price_change_5d)
            }
            
        except Exception as e:
            print(f"Error calculating technical indicators for {symbol}: {e}")
            return {}

    def calculate_rsi(self, series, period=14):
        """Calculate RSI (Relative Strength Index)"""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, series, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        try:
            if len(series) < period:
                sma = series.mean()
                std = series.std()
            else:
                sma = series.rolling(window=period).mean().iloc[-1]
                std = series.rolling(window=period).std().iloc[-1]
            
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            return upper_band, lower_band
        except:
            return series.iloc[-1] * 1.02, series.iloc[-1] * 0.98
    
    def calculate_macd(self, series, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            if len(series) < slow:
                return 0, 0
            
            ema_fast = series.ewm(span=fast).mean()
            ema_slow = series.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            macd_signal = macd_line.ewm(span=signal).mean()
            
            return macd_line.iloc[-1], macd_signal.iloc[-1]
        except:
            return 0, 0
    
    def _generate_signal(self, indicators: dict) -> str:
        """Generate trading signal based on technical indicators"""
        if not indicators:
            return "neutral"
        
        signals = []
        
        # RSI Signal
        rsi = indicators.get("RSI_14", 50)
        if rsi < 30:
            signals.append("buy")
        elif rsi > 70:
            signals.append("sell")
        else:
            signals.append("neutral")
        
        # SMA Signal - ensure all values are scalars
        close = float(indicators.get("Close", 0))
        sma_20 = float(indicators.get("SMA_20", 0))
        sma_50 = float(indicators.get("SMA_50", 0))
        
        if close > 0 and sma_20 > 0 and sma_50 > 0:
            if close > sma_20 > sma_50:
                signals.append("buy")
            elif close < sma_20 < sma_50:
                signals.append("sell")
            else:
                signals.append("neutral")
        else:
            signals.append("neutral")
        
        # MACD Signal - ensure scalar values
        macd = float(indicators.get("MACD", 0))
        macd_signal = float(indicators.get("MACD_Signal", 0))
        
        if macd > macd_signal and macd > 0:
            signals.append("buy")
        elif macd < macd_signal and macd < 0:
            signals.append("sell")
        else:
            signals.append("neutral")
        
        # Combine signals
        buy_count = signals.count("buy")
        sell_count = signals.count("sell")
        
        if buy_count > sell_count:
            return "buy"
        elif sell_count > buy_count:
            return "sell"
        else:
            return "neutral"
    
    def _generate_summary(self, indicators: dict, signal: str) -> str:
        """Generate a summary of technical analysis"""
        if not indicators:
            return "No technical data available"
        
        rsi = indicators.get("RSI_14", 50)
        price_change_1d = indicators.get("Price_Change_1D", 0)
        
        rsi_status = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
        trend = "bullish" if price_change_1d > 2 else "bearish" if price_change_1d < -2 else "sideways"
        
        return f"Signal: {signal.upper()}, RSI: {rsi:.1f} ({rsi_status}), Trend: {trend}, 1D Change: {price_change_1d:.2f}%"
