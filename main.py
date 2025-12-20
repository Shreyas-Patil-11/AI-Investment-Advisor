# main.py - AI Investment Advisor with Enhanced User Interface
import streamlit as st
import pandas as pd
import traceback
import os

from mcp import MCPServer
from data.mappings import stock_symbols, stock_sectors

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_investments' not in st.session_state:
        st.session_state.user_investments = []
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None

def get_available_sectors():
    """Get comprehensive list of sectors"""
    # Combine predefined sectors with additional major sectors
    predefined_sectors = set(stock_sectors.values())
    additional_sectors = {
        "Technology", "Healthcare", "Energy", "Finance", "Consumer Goods", 
        "Telecommunications", "Real Estate", "Utilities", "Automotive", 
        "Aerospace", "Media", "Retail", "Construction", "Agriculture",
        "Mining", "Transportation", "Insurance", "Food & Beverage"
    }
    all_sectors = predefined_sectors.union(additional_sectors)
    return sorted(list(all_sectors))

def create_natural_language_input(user_data):
    """Convert user data to natural language for LLM processing"""
    investments_text = []
    total_invested = 0
    
    for inv in user_data['investments']:
        investments_text.append(f"₹{inv['amount']} in {inv['symbol']}")
        total_invested += inv['amount']
    
    sector_text = f"I want to invest in {user_data['sector_interest']} sector" if user_data['sector_interest'] else "I'm open to any sector"
    
    natural_input = f"""
    I have ₹{user_data['available_amount']} available for new investments.
    My previous investments: {', '.join(investments_text)}.
    My current portfolio is worth ₹{user_data['current_portfolio_value']}.
    Total amount I invested previously: ₹{total_invested}.
    My risk tolerance is {user_data['risk_tolerance']}.
    My investment timeline is {user_data['investment_timeline']}.
    {sector_text}.
    My investment goals are: {', '.join(user_data['investment_goals'])}.
    Please provide investment recommendations.
    """
    
    return natural_input.strip()

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Page configuration
    st.set_page_config(
        page_title="AI Investment Advisor", 
        page_icon="🧠", 
        layout="wide"
    )
    
    # Title and description
    st.title("🧠 AI Investment Advisor")
    st.markdown("### *Get personalized investment recommendations powered by Gemini 2.0 Pro*")
    
    # Hardcoded API key
    api_key = "Enter_your_gemini_api_key"
    
    # Sidebar for information only
    with st.sidebar:
        st.header("ℹ️ About")
        st.success("✅ AI System Ready")
        
        st.markdown("---")
        st.markdown("### 📖 How it works:")
        st.markdown("""
        1. **Input**: Share your investment details
        2. **Analysis**: AI analyzes market data & news
        3. **Recommendations**: Get personalized advice
        4. **Risk Assessment**: Understand portfolio risk
        """)
        
        st.markdown("---")
        st.markdown("### 🎯 Supported Analysis:")
        st.markdown("""
        - **Technical Analysis**: RSI, SMA, MACD, Bollinger Bands
        - **News Sentiment**: Real-time news analysis
        - **Risk Assessment**: Portfolio diversification
        - **Sector Analysis**: All major sectors supported
        - **Custom Stocks**: Add any company dynamically
        """)
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["📋 Investment Profile", "📊 Analysis Results"])
    
    with tab1:
        st.header("📋 Tell Us About Your Investment Profile")
        
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Financial Information")
            
            # Available amount for investment
            available_amount = st.number_input(
                "Available amount for new investment (₹)",
                min_value=1000,
                max_value=10000000,
                value=50000,
                step=1000,
                help="How much money do you have available to invest?"
            )
            
            # Current portfolio value
            current_portfolio_value = st.number_input(
                "Current total portfolio value (₹)",
                min_value=0,
                max_value=50000000,
                value=100000,
                step=1000,
                help="What is the current total value of all your investments?"
            )
            
            # Risk tolerance
            risk_tolerance = st.selectbox(
                "Risk Tolerance",
                ["Conservative", "Moderate", "Aggressive"],
                index=1,
                help="How much risk are you comfortable with?"
            )
            
            # Investment timeline
            investment_timeline = st.selectbox(
                "Investment Timeline",
                ["Short-term (< 1 year)", "Medium-term (1-3 years)", "Long-term (> 3 years)"],
                index=2,
                help="How long do you plan to hold these investments?"
            )
        
        with col2:
            st.subheader("📈 Investment History & Preferences")
            
            # Investment history management
            st.write("**Add your previous investments:**")
            
            # Add new investment - Dynamic company input
            st.write("**Option 1: Select from popular stocks**")
            new_col1, new_col2, new_col3 = st.columns([2, 1, 1])
            
            with new_col1:
                selected_stock = st.selectbox(
                    "Popular Stocks",
                    [""] + list(stock_symbols.keys()),
                    help="Choose from pre-defined popular stocks"
                )
            
            with new_col2:
                investment_amount_1 = st.number_input(
                    "Amount (₹)",
                    min_value=0,
                    value=10000,
                    step=1000,
                    key="amount_1"
                )
            
            with new_col3:
                st.write("")
                st.write("")
                if st.button("➕ Add Popular Stock"):
                    if selected_stock and investment_amount_1 > 0:
                        new_investment = {
                            'symbol': selected_stock,
                            'company': stock_symbols.get(selected_stock, selected_stock),
                            'amount': investment_amount_1
                        }
                        st.session_state.user_investments.append(new_investment)
                        st.success(f"Added {stock_symbols.get(selected_stock, selected_stock)} - ₹{investment_amount_1:,.0f}")
                        st.rerun()
                    else:
                        st.error("Please select a stock and enter amount > 0")
            
            st.write("**Option 2: Add any company manually**")
            custom_col1, custom_col2, custom_col3 = st.columns([2, 1, 1])
            
            with custom_col1:
                custom_company = st.text_input(
                    "Company Name",
                    placeholder="e.g., Apple Inc, Tesla, Microsoft",
                    help="Enter any company name or stock symbol"
                )
            
            with custom_col2:
                investment_amount_2 = st.number_input(
                    "Amount (₹)",
                    min_value=0,
                    value=10000,
                    step=1000,
                    key="amount_2"
                )
            
            with custom_col3:
                st.write("")
                st.write("")
                if st.button("➕ Add Custom Company"):
                    if custom_company.strip() and investment_amount_2 > 0:
                        # Create symbol from company name (first word + length)
                        company_clean = custom_company.strip().title()
                        symbol_generated = company_clean.replace(" ", "").upper()[:6]  # Max 6 chars
                        
                        new_investment = {
                            'symbol': symbol_generated,
                            'company': company_clean,
                            'amount': investment_amount_2
                        }
                        st.session_state.user_investments.append(new_investment)
                        st.success(f"Added {company_clean} ({symbol_generated}) - ₹{investment_amount_2:,.0f}")
                        st.rerun()
                    else:
                        st.error("Please enter company name and amount > 0")
            
            # Display current investments
            if st.session_state.user_investments:
                st.write("**Your Investment Portfolio:**")
                for i, inv in enumerate(st.session_state.user_investments):
                    inv_col1, inv_col2 = st.columns([4, 1])
                    with inv_col1:
                        st.write(f"• {inv['company']} ({inv['symbol']}): ₹{inv['amount']:,.0f}")
                    with inv_col2:
                        if st.button("🗑️", key=f"remove_{i}", help="Remove investment"):
                            st.session_state.user_investments.pop(i)
                            st.rerun()
                
                total_invested = sum(inv['amount'] for inv in st.session_state.user_investments)
                st.info(f"**Total Invested**: ₹{total_invested:,.0f}")
            else:
                st.info("No investments added yet. Add at least one to get recommendations.")
            
            # Sector preference
            sector_interest = st.selectbox(
                "Preferred sector for new investments",
                ["Any Sector"] + get_available_sectors(),
                help="Which sector interests you most?"
            )
            
            # Investment goals
            investment_goals = st.multiselect(
                "Investment Goals",
                ["Wealth Creation", "Regular Income", "Capital Preservation", "Tax Savings", "Retirement Planning"],
                default=["Wealth Creation"],
                help="What are your primary investment objectives?"
            )
        
        # Analysis button
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button(
                "🚀 Get Investment Recommendations", 
                type="primary",
                use_container_width=True
            ):
                # Validate inputs
                if not st.session_state.user_investments:
                    st.error("Please add at least one previous investment to get personalized recommendations.")
                else:
                    # Prepare user data
                    user_data = {
                        "available_amount": available_amount,
                        "current_portfolio_value": current_portfolio_value,
                        "risk_tolerance": risk_tolerance.lower(),
                        "investment_timeline": investment_timeline,
                        "investments": st.session_state.user_investments,
                        "sector_interest": sector_interest if sector_interest != "Any Sector" else None,
                        "investment_goals": investment_goals
                    }
                    
                    # Analyze investments
                    with st.spinner("🤖 Analyzing your portfolio and generating recommendations..."):
                        try:
                            # Initialize MCP server
                            server = MCPServer(api_key)
                            
                            # Create natural language input
                            natural_input = create_natural_language_input(user_data)
                            
                            # Show analysis input
                            with st.expander("🔍 Analysis Input", expanded=False):
                                st.text(natural_input)
                            
                            # Process with MCP server
                            result = server.process(natural_input)
                            
                            # Store results
                            st.session_state.analysis_result = result
                            st.session_state.analysis_done = True
                            
                            st.success("✅ Analysis completed! Check the 'Analysis Results' tab.")
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
                            with st.expander("Error Details"):
                                st.code(traceback.format_exc())
    
    with tab2:
        if st.session_state.analysis_done and st.session_state.analysis_result:
            display_analysis_results(st.session_state.analysis_result)
        else:
            st.info("📝 Please complete your investment profile and click 'Get Recommendations' to see analysis results.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>⚠️ <strong>Disclaimer:</strong> This is for educational purposes only. Not financial advice. 
        Always consult with a qualified financial advisor before making investment decisions.</p>
        <p>Built with ❤️ using Streamlit and Gemini 2.0 Pro</p>
    </div>
    """, unsafe_allow_html=True)

def display_analysis_results(result):
    """Display comprehensive analysis results"""
    st.header("📊 Your Personalized Investment Analysis")
    
    # Executive Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_level = result.get('portfolio_risk_level', 'Unknown').title()
        risk_color = "🔴" if risk_level == "High" else "🟡" if risk_level == "Moderate" else "🟢"
        st.metric("Portfolio Risk", f"{risk_color} {risk_level}")
    
    with col2:
        recommendations_count = len(result.get('recommendations', []))
        st.metric("Stocks Analyzed", f"{recommendations_count}")
    
    with col3:
        buy_count = sum(1 for r in result.get('recommendations', []) if 'Buy' in r.get('recommendation', ''))
        st.metric("Buy Recommendations", f"{buy_count}")
    
    with col4:
        hold_count = sum(1 for r in result.get('recommendations', []) if 'Hold' in r.get('recommendation', ''))
        st.metric("Hold Recommendations", f"{hold_count}")
    
    # Risk Assessment
    st.subheader("⚠️ Risk Assessment")
    risk_level = result.get('portfolio_risk_level', 'moderate')
    
    if risk_level == "high":
        st.error("""
        **🔴 HIGH RISK DETECTED**
        - Your portfolio shows significant risk factors
        - Consider diversification and risk management
        - Review underperforming investments
        """)
    elif risk_level == "moderate":
        st.warning("""
        **🟡 MODERATE RISK**
        - Balanced risk profile with room for optimization
        - Consider gradual diversification
        - Monitor portfolio performance regularly
        """)
    else:
        st.success("""
        **🟢 LOW RISK**
        - Well-balanced portfolio
        - Good diversification
        - Continue current strategy with regular reviews
        """)
    
    # Stock Recommendations
    st.subheader("🎯 Stock Recommendations")
    
    recommendations = result.get('recommendations', [])
    if recommendations:
        # Create tabs for different recommendation types
        buy_recs = [r for r in recommendations if 'Buy' in r.get('recommendation', '')]
        hold_recs = [r for r in recommendations if 'Hold' in r.get('recommendation', '')]
        sell_recs = [r for r in recommendations if 'Sell' in r.get('recommendation', '')]
        
        rec_tab1, rec_tab2, rec_tab3, rec_tab4 = st.tabs([
            f"🟢 Buy ({len(buy_recs)})", 
            f"🔵 Hold ({len(hold_recs)})", 
            f"🔴 Sell ({len(sell_recs)})",
            "📈 All Recommendations"
        ])
        
        with rec_tab1:
            if buy_recs:
                for rec in buy_recs:
                    display_stock_recommendation(rec, "success")
            else:
                st.info("No buy recommendations at this time.")
        
        with rec_tab2:
            if hold_recs:
                for rec in hold_recs:
                    display_stock_recommendation(rec, "info")
            else:
                st.info("No hold recommendations.")
        
        with rec_tab3:
            if sell_recs:
                for rec in sell_recs:
                    display_stock_recommendation(rec, "error")
            else:
                st.info("No sell recommendations.")
        
        with rec_tab4:
            # Table view of all recommendations
            df_data = []
            for rec in recommendations:
                df_data.append({
                    'Company': rec.get('company', 'N/A'),
                    'Symbol': rec.get('symbol', 'N/A'),
                    'Sector': rec.get('sector', 'N/A'),
                    'Recommendation': rec.get('recommendation', 'N/A'),
                    'Confidence': rec.get('confidence', 'N/A'),
                    'News Sentiment': rec.get('news_sentiment', 'N/A'),
                    'Technical Signal': rec.get('technical_signal', 'N/A')
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
    else:
        st.info("No specific recommendations generated. This may be due to market conditions or data availability.")
    
    # Analysis Summary
    summary = result.get('analysis_summary', '')
    if summary:
        st.subheader("📋 Analysis Summary")
        st.info(summary)
    
    # Parsed context for transparency
    with st.expander("🔍 Parsed Analysis Context", expanded=False):
        parsed_context = result.get('parsed_context', {})
        if parsed_context:
            st.json(parsed_context)
        else:
            st.write("No parsed context available")

def display_stock_recommendation(rec, card_type):
    """Display individual stock recommendation card"""
    # Color coding
    if card_type == "success":
        border_color = "#28a745"
        icon = "🟢"
    elif card_type == "error":
        border_color = "#dc3545"
        icon = "🔴"
    else:
        border_color = "#17a2b8"
        icon = "🔵"
    
    # Create expandable card
    with st.expander(f"{icon} {rec.get('company', 'N/A')} ({rec.get('symbol', 'N/A')}) - {rec.get('recommendation', 'N/A')}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Sector:** {rec.get('sector', 'N/A')}")
            st.write(f"**Recommendation:** {rec.get('recommendation', 'N/A')}")
            st.write(f"**Confidence:** {rec.get('confidence', 'N/A')}")
        
        with col2:
            st.write(f"**News Sentiment:** {rec.get('news_sentiment', 'N/A')}")
            st.write(f"**Technical Signal:** {rec.get('technical_signal', 'N/A')}")
        
        st.write(f"**Reasoning:** {rec.get('reasoning', 'Standard analysis')}")

if __name__ == "__main__":
    main()
