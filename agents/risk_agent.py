import pandas as pd
from typing import List, Dict

class RiskAgent:
    def __init__(self):
        self.risk_thresholds = {
            "low": 0.3,
            "moderate": 0.6,
            "high": 1.0
        }
    
    def run(self, context: Dict):
        """Main run method for MCP integration"""
        try:
            user_profile = context.get("user_profile", {})
            investments = user_profile.get("history", [])
            current_value = user_profile.get("current_value", 0)
            risk_tolerance = user_profile.get("risk_tolerance", "moderate")
            
            risk_level = self.assess_risk(investments, current_value, risk_tolerance)
            
            # Update context with risk assessment
            context["risk_assessment"] = {
                "risk_level": risk_level,
                "risk_tolerance": risk_tolerance,
                "portfolio_volatility": self._calculate_portfolio_volatility(investments)
            }
            
        except Exception as e:
            print(f"Risk assessment error: {e}")
            context["risk_assessment"] = {
                "risk_level": "moderate",
                "risk_tolerance": "moderate",
                "portfolio_volatility": 0.5
            }
    
    def assess_risk(self, investments: List[Dict], current_value: float, risk_tolerance: str = "moderate") -> str:
        """Assess overall portfolio risk level"""
        if not investments or current_value <= 0:
            return "low"
        
        # Calculate total invested amount
        total_invested = sum(inv.get("invested", 0) for inv in investments)
        
        # Calculate portfolio loss percentage
        loss_percentage = (total_invested - current_value) / total_invested if total_invested > 0 else 0
        
        # Assess concentration risk
        concentration_risk = self._assess_concentration_risk(investments)
        
        # Calculate sector diversification risk
        sector_risk = self._assess_sector_risk(investments)
        
        # Combined risk score
        risk_score = (
            loss_percentage * 0.4 +  # Portfolio performance weight
            concentration_risk * 0.3 +  # Concentration risk weight
            sector_risk * 0.3  # Sector diversification weight
        )
        
        # Adjust based on user risk tolerance
        tolerance_multiplier = {
            "conservative": 0.7,
            "moderate": 1.0,
            "aggressive": 1.3
        }.get(risk_tolerance, 1.0)
        
        adjusted_score = risk_score * tolerance_multiplier
        
        # Determine risk level
        if adjusted_score <= self.risk_thresholds["low"]:
            return "low"
        elif adjusted_score <= self.risk_thresholds["moderate"]:
            return "moderate"
        else:
            return "high"
    
    def _assess_concentration_risk(self, investments: List[Dict]) -> float:
        """Calculate concentration risk based on portfolio distribution"""
        if not investments:
            return 0.0
        
        total_invested = sum(inv.get("invested", 0) for inv in investments)
        if total_invested == 0:
            return 0.0
        
        # Calculate concentration score (higher = more concentrated = riskier)
        concentration_scores = []
        for inv in investments:
            weight = inv.get("invested", 0) / total_invested
            concentration_scores.append(weight ** 2)
        
        # Herfindahl-Hirschman Index for concentration
        hhi = sum(concentration_scores)
        
        # Normalize to 0-1 scale (1 = maximum concentration)
        return min(hhi * 2, 1.0)
    
    def _assess_sector_risk(self, investments: List[Dict]) -> float:
        """Calculate sector diversification risk"""
        if not investments:
            return 0.0
        
        from data.mappings import stock_sectors
        
        sectors = set()
        for inv in investments:
            symbol = inv.get("company", "")
            sector = stock_sectors.get(symbol, "Unknown")
            sectors.add(sector)
        
        # Risk decreases with more sectors (better diversification)
        unique_sectors = len(sectors)
        max_sectors = len(set(stock_sectors.values()))
        
        # Return inverse diversification (high value = poor diversification = high risk)
        return max(0, 1.0 - (unique_sectors - 1) / max(1, max_sectors - 1))
    
    def _calculate_portfolio_volatility(self, investments: List[Dict]) -> float:
        """Estimate portfolio volatility based on sector composition"""
        if not investments:
            return 0.5
        
        from data.mappings import stock_sectors
        
        # Sector volatility estimates (higher = more volatile)
        sector_volatilities = {
            "Banking": 0.7,
            "Pharmaceuticals": 0.5,
            "Information Technology": 0.6,
            "Unknown": 0.8
        }
        
        total_invested = sum(inv.get("invested", 0) for inv in investments)
        if total_invested == 0:
            return 0.5
        
        weighted_volatility = 0
        for inv in investments:
            symbol = inv.get("company", "")
            sector = stock_sectors.get(symbol, "Unknown")
            weight = inv.get("invested", 0) / total_invested
            volatility = sector_volatilities.get(sector, 0.8)
            weighted_volatility += weight * volatility
        
        return min(weighted_volatility, 1.0)