import os
import pandas as pd
import numpy as np
import asyncio
from binance.client import Client
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import ta
import requests
from datetime import datetime
import time
from flask import Flask
from threading import Thread

print("🚀 Starting Advanced Crypto Trading Agent on Railway...")

# Flask app untuk health check
app = Flask('')

@app.route('/')
def home():
    return "🤖 Crypto Trading Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Token bot Telegram dari environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables!")
    exit(1)

class AdvancedTradingAgent:
    def __init__(self):
        try:
            self.client = Client()
            print("✅ Binance client initialized")
        except:
            print("⚠️ Using public Binance API")
    
    def get_ohlc_data(self, symbol='BTCUSDT', interval='1h', limit=100):
        """Get OHLC data from Binance"""
        try:
            # Try using python-binance first
            klines = self.client.get_historical_klines(
                symbol, interval, f"{limit} hours ago UTC"
            )
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades', 'ignore'
            ])
        except:
            # Fallback to public API
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            response = requests.get(url).json()
            df = pd.DataFrame(response, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'trades', 'taker_buy', 'ignore', 'ignore2'
            ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        return df

    def calculate_smc_indicators(self, df):
        """Smart Money Concepts Indicators"""
        # Market Structure Shift (MSS)
        df['higher_high'] = df['high'] > df['high'].shift(1)
        df['higher_low'] = df['low'] > df['low'].shift(1)
        df['lower_high'] = df['high'] < df['high'].shift(1)
        df['lower_low'] = df['low'] < df['low'].shift(1)
        
        # Determine trend
        df['bullish_mss'] = (df['higher_high'] & df['higher_low']).astype(int)
        df['bearish_mss'] = (df['lower_high'] & df['lower_low']).astype(int)
        
        # Order Blocks (simplified)
        df['bullish_ob'] = ((df['close'] > df['open']) & 
                           (df['close'].shift(1) < df['open'].shift(1))).astype(int)
        df['bearish_ob'] = ((df['close'] < df['open']) & 
                           (df['close'].shift(1) > df['open'].shift(1))).astype(int)
        
        # Liquidity Levels
        df['liquidity_high'] = df['high'].rolling(20).max()
        df['liquidity_low'] = df['low'].rolling(20).min()
        
        return df

    def calculate_ict_indicators(self, df):
        """ICT Concepts Implementation"""
        # Fair Value Gaps (FVG)
        df['fvg_bullish'] = ((df['low'].shift(1) > df['high'].shift(2)) & 
                           (df['low'] > df['high'].shift(2))).astype(int)
        df['fvg_bearish'] = ((df['high'].shift(1) < df['low'].shift(2)) & 
                           (df['high'] < df['low'].shift(2))).astype(int)
        
        # Market Structure
        df['break_of_structure'] = ((df['high'] > df['high'].shift(2)) | 
                                  (df['low'] < df['low'].shift(2))).astype(int)
        
        return df

    def calculate_price_action(self, df):
        """Price Action Analysis"""
        # Key Levels
        df['support'] = df['low'].rolling(10).min()
        df['resistance'] = df['high'].rolling(10).max()
        
        # Pattern Recognition (simplified)
        df['doji'] = (abs(df['close'] - df['open']) / (df['high'] - df['low']) < 0.1).astype(int)
        df['hammer'] = ((df['close'] > df['open']) & 
                       ((df['close'] - df['low']) > 2 * (df['high'] - df['close']))).astype(int)
        df['engulfing_bullish'] = ((df['close'] > df['open']) & 
                                 (df['close'].shift(1) < df['open'].shift(1)) & 
                                 (df['close'] > df['open'].shift(1))).astype(int)
        
        return df

    def get_advanced_analysis(self, symbol='BTCUSDT'):
        """Comprehensive Advanced Analysis"""
        try:
            print(f"🔍 Performing advanced analysis for {symbol}...")
            
            # Get data
            df = self.get_ohlc_data(symbol)
            
            if len(df) < 50:
                return {'error': 'Insufficient data for analysis'}
            
            # Calculate all indicators
            df = self.calculate_smc_indicators(df)
            df = self.calculate_ict_indicators(df)
            df = self.calculate_price_action(df)
            
            # Technical Indicators
            df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
            df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
            df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
            df['macd'] = ta.trend.MACD(df['close']).macd()
            
            # Current values
            current_price = df['close'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1]
            
            # SMC Analysis
            bullish_mss = df['bullish_mss'].iloc[-1]
            bearish_mss = df['bearish_mss'].iloc[-1]
            bullish_ob = df['bullish_ob'].iloc[-1]
            bearish_ob = df['bearish_ob'].iloc[-1]
            
            # ICT Analysis
            fvg_bullish = df['fvg_bullish'].iloc[-1]
            fvg_bearish = df['fvg_bearish'].iloc[-1]
            bos = df['break_of_structure'].iloc[-1]
            
            # Price Action
            support = df['support'].iloc[-1]
            resistance = df['resistance'].iloc[-1]
            doji = df['doji'].iloc[-1]
            hammer = df['hammer'].iloc[-1]
            engulfing_bullish = df['engulfing_bullish'].iloc[-1]
            
            # Generate signals
            signals = []
            
            # Trend Analysis
            if ema_20 > ema_50 and current_price > ema_20:
                trend = "🟢 STRONG UPTREND"
                signals.append("Trend: Bullish")
            elif ema_20 < ema_50 and current_price < ema_20:
                trend = "🔴 STRONG DOWNTREND"
                signals.append("Trend: Bearish")
            else:
                trend = "🟡 SIDEWAYS/RANGING"
                signals.append("Trend: Neutral")
            
            # SMC Signals
            if bullish_mss:
                signals.append("SMC: Bullish Market Structure Shift")
            if bearish_mss:
                signals.append("SMC: Bearish Market Structure Shift")
            if bullish_ob:
                signals.append("SMC: Bullish Order Block Present")
            if bearish_ob:
                signals.append("SMC: Bearish Order Block Present")
            
            # ICT Signals
            if fvg_bullish:
                signals.append("ICT: Bullish Fair Value Gap")
            if fvg_bearish:
                signals.append("ICT: Bearish Fair Value Gap")
            if bos:
                signals.append("ICT: Break of Structure Detected")
            
            # Price Action Signals
            if doji:
                signals.append("PA: Doji - Indecision")
            if hammer:
                signals.append("PA: Hammer - Potential Reversal")
            if engulfing_bullish:
                signals.append("PA: Bullish Engulfing")
            
            # RSI Analysis
            if rsi > 70:
                rsi_signal = "OVERBOUGHT"
                signals.append("RSI: Overbought - Caution")
            elif rsi < 30:
                rsi_signal = "OVERSOLD"
                signals.append("RSI: Oversold - Potential Opportunity")
            else:
                rsi_signal = "NEUTRAL"
            
            # Support/Resistance Analysis
            price_to_support = ((current_price - support) / support * 100)
            price_to_resistance = ((resistance - current_price) / current_price * 100)
            
            if price_to_support < 2:
                signals.append("Price: Near Strong Support")
            if price_to_resistance < 2:
                signals.append("Price: Near Strong Resistance")
            
            return {
                'symbol': symbol,
                'price': current_price,
                'trend': trend,
                'rsi': rsi,
                'rsi_signal': rsi_signal,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'support': support,
                'resistance': resistance,
                'signals': signals,
                'price_to_support_pct': price_to_support,
                'price_to_resistance_pct': price_to_resistance,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            return {'error': f"Analysis error: {str(e)}"}

class AdvancedTelegramBot:
    def __init__(self, token):
        self.token = token
        self.agent = AdvancedTradingAgent()
        print("✅ Advanced Telegram Bot initialized")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_text = """
🤖 **Advanced Crypto Trading Agent v2.0**

🎯 **Advanced Features:**
• SMC (Smart Money Concepts)
• ICT (Inner Circle Trader) Analysis  
• Price Action Patterns
• Multi-timeframe Analysis
• Advanced Risk Management

📊 **Commands:**
/start - Show this message
/analyze [SYMBOL] - Advanced analysis
/smc [SYMBOL] - SMC-focused analysis
/ict [SYMBOL] - ICT-focused analysis
/levels [SYMBOL] - Key levels only
/multi [SYMBOL] - Multi-timeframe analysis

🔍 **Examples:**
/analyze BTCUSDT
/smc ETHUSDT
/ict ADAUSDT
/multi SOLUSDT

⚡ **Now with professional trading concepts!**
        """
        await update.message.reply_text(welcome_text)
    
    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        symbol = context.args[0].upper() if context.args else 'BTCUSDT'
        
        await update.message.reply_text(f"🎯 Performing advanced analysis for {symbol}...")
        
        try:
            analysis = self.agent.get_advanced_analysis(symbol)
            
            if 'error' in analysis:
                await update.message.reply_text(f"❌ Error: {analysis['error']}")
                return
            
            # Create comprehensive message
            message = f"""
📊 **ADVANCED ANALYSIS - {analysis['symbol']}**
⏰ {analysis['timestamp']}

💰 **Price:** ${analysis['price']:,.2f}
📈 **Trend:** {analysis['trend']}
🎯 **RSI:** {analysis['rsi']:.1f} ({analysis['rsi_signal']})

🛡️ **Key Levels:**
• Support: ${analysis['support']:,.2f}
• Resistance: ${analysis['resistance']:,.2f}
• Distance to Support: {analysis['price_to_support_pct']:.1f}%
• Distance to Resistance: {analysis['price_to_resistance_pct']:.1f}%

⚡ **Technical Signals:**
"""
            
            # Add signals
            for signal in analysis['signals'][:8]:  # Limit to 8 signals
                message += f"• {signal}\n"
            
            if len(analysis['signals']) > 8:
                message += f"• ... and {len(analysis['signals']) - 8} more signals\n"
            
            message += """
💡 **Professional Insight:**
"""
            # Add professional insight based on signals
            bullish_signals = len([s for s in analysis['signals'] if 'bullish' in s.lower() or 'buy' in s.lower()])
            bearish_signals = len([s for s in analysis['signals'] if 'bearish' in s.lower() or 'sell' in s.lower()])
            
            if bullish_signals > bearish_signals + 2:
                message += "🟢 BULLISH BIAS - Look for long opportunities"
            elif bearish_signals > bullish_signals + 2:
                message += "🔴 BEARISH BIAS - Look for short opportunities"
            else:
                message += "🟡 NEUTRAL BIAS - Wait for clearer signals"
            
            message += f"\n\n📊 Signal Strength: {bullish_signals}👍 / {bearish_signals}👎"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Analysis error: {str(e)}")
    
    async def smc_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        symbol = context.args[0].upper() if context.args else 'BTCUSDT'
        
        await update.message.reply_text(f"🔍 Analyzing SMC concepts for {symbol}...")
        
        try:
            analysis = self.agent.get_advanced_analysis(symbol)
            
            if 'error' in analysis:
                await update.message.reply_text(f"❌ Error: {analysis['error']}")
                return
            
            smc_signals = [s for s in analysis['signals'] if 'SMC:' in s]
            
            message = f"""
🎯 **SMC ANALYSIS - {analysis['symbol']}**

💰 **Price:** ${analysis['price']:,.2f}
📈 **Market Structure:** {analysis['trend']}

🔄 **SMC Signals:**
"""
            for signal in smc_signals:
                message += f"• {signal.replace('SMC: ', '')}\n"
            
            if not smc_signals:
                message += "• No strong SMC signals detected\n"
            
            message += f"""
💧 **Liquidity Levels:**
• Support: ${analysis['support']:,.2f}
• Resistance: ${analysis['resistance']:,.2f}

🎯 **SMC Strategy:**
{'🟢 Look for BUY setups at support' if 'Bullish' in analysis['trend'] else '🔴 Look for SELL setups at resistance' if 'Bearish' in analysis['trend'] else '🟡 Trade range between support/resistance'}
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ SMC analysis error: {str(e)}")
    
    async def ict_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        symbol = context.args[0].upper() if context.args else 'BTCUSDT'
        
        await update.message.reply_text(f"🔍 Analyzing ICT concepts for {symbol}...")
        
        try:
            analysis = self.agent.get_advanced_analysis(symbol)
            
            if 'error' in analysis:
                await update.message.reply_text(f"❌ Error: {analysis['error']}")
                return
            
            ict_signals = [s for s in analysis['signals'] if 'ICT:' in s]
            
            message = f"""
⚡ **ICT ANALYSIS - {analysis['symbol']}**

💰 **Price:** ${analysis['price']:,.2f}
📈 **Market Condition:** {analysis['trend']}

🔍 **ICT Signals:**
"""
            for signal in ict_signals:
                message += f"• {signal.replace('ICT: ', '')}\n"
            
            if not ict_signals:
                message += "• No strong ICT signals detected\n"
            
            message += f"""
🎯 **Fair Value Gaps & Structure:**
• Current RSI: {analysis['rsi']:.1f}
• Key Support: ${analysis['support']:,.2f}
• Key Resistance: ${analysis['resistance']:,.2f}

💡 **ICT Insight:**
{'🟢 Look for long entries after FVG fills' if any('Bullish' in s for s in ict_signals) else '🔴 Look for short entries after FVG fills' if any('Bearish' in s for s in ict_signals) else '🟡 Wait for market structure clarity'}
            """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            await update.message.reply_text(f"❌ ICT analysis error: {str(e)}")
    
    async def multi_timeframe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        symbol = context.args[0].upper() if context.args else 'BTCUSDT'
        
        await update.message.reply_text(f"📊 Analyzing multiple timeframes for {symbol}...")
        
        try:
            # This would analyze multiple timeframes in real implementation
            message = f"""
⏰ **MULTI-TIMEFRAME ANALYSIS - {symbol}**

🕒 **1H Analysis:** Primary trend and key levels
🕓 **4H Analysis:** Medium-term direction  
🕔 **1D Analysis:** Long-term structure

⚡ **Coming Soon:**
• Real multi-timeframe correlation
• Higher timeframe confirmation
• Timeframe confluence analysis

🔧 *This feature is under development*
*Currently showing 1H analysis only*

💡 **Pro Tip:** Always check higher timeframes for better context!
            """
            
            await update.message.reply_text(message)
            
            # Also send current analysis
            await self.analyze(update, context)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Multi-timeframe error: {str(e)}")

    def run(self):
        """Run the bot"""
        try:
            application = Application.builder().token(self.token).build()
            
            # Add handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("analyze", self.analyze))
            application.add_handler(CommandHandler("smc", self.smc_analysis))
            application.add_handler(CommandHandler("ict", self.ict_analysis))
            application.add_handler(CommandHandler("multi", self.multi_timeframe))
            application.add_handler(CommandHandler("levels", self.smc_analysis))  # Alias
            
            print("🚀 Advanced Bot is running on Railway...")
            print("✅ Available commands: /start, /analyze, /smc, /ict, /multi, /levels")
            
            # Start Flask for health checks
            keep_alive()
            
            application.run_polling()
            
        except Exception as e:
            print(f"❌ Bot error: {e}")

# Main execution
if __name__ == "__main__":
    bot = AdvancedTelegramBot(BOT_TOKEN)
    bot.run()
