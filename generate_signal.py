import json
import warnings
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
import xgboost as xgb

warnings.filterwarnings('ignore')
np.random.seed(42)

print("📥 Download dati...")
df = yf.download('^NDX', period='5y', interval='1d', auto_adjust=True, progress=False)
df.columns = df.columns.droplevel(1) if df.columns.nlevels > 1 else df.columns
df = df[['Open','High','Low','Close','Volume']].dropna()

vix = yf.download('^VIX',     period='5y', interval='1d', auto_adjust=True, progress=False)['Close'].squeeze().rename('VIX')
tnx = yf.download('^TNX',     period='5y', interval='1d', auto_adjust=True, progress=False)['Close'].squeeze().rename('TNX')
dxy = yf.download('DX-Y.NYB', period='5y', interval='1d', auto_adjust=True, progress=False)['Close'].squeeze().rename('DXY')

def add_features(df):
    d = df.copy()
    for w in [5, 10, 20, 50, 200]:
        d[f'SMA_{w}'] = d['Close'].rolling(w).mean()
        d[f'EMA_{w}'] = d['Close'].ewm(span=w, adjust=False).mean()
    d['ROC_5']  = d['Close'].pct_change(5)  * 100
    d['ROC_20'] = d['Close'].pct_change(20) * 100
    delta = d['Close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    d['RSI_14'] = 100 - (100 / (1 + gain / (loss + 1e-9)))
    ema12 = d['Close'].ewm(span=12, adjust=False).mean()
    ema26 = d['Close'].ewm(span=26, adjust=False).mean()
    d['MACD']        = ema12 - ema26
    d['MACD_signal'] = d['MACD'].ewm(span=9, adjust=False).mean()
    sma20 = d['Close'].rolling(20).mean()
    std20 = d['Close'].rolling(20).std()
    d['BB_width'] = (sma20 + 2*std20 - (sma20 - 2*std20)) / sma20 * 100
    d['BB_pos']   = (d['Close'] - (sma20 - 2*std20)) / (4*std20 + 1e-9)
    d['Volume_ratio'] = d['Volume'] / (d['Volume'].rolling(20).mean() + 1)
    for lag in [1, 2, 3, 5, 10]:
        d[f'ret_lag_{lag}'] = d['Close'].pct_change(lag) * 100
    d['vol_5']  = d['Close'].pct_change().rolling(5).std()  * 100
    d['vol_20'] = d['Close'].pct_change().rolling(20).std() * 100
    d = d.join(vix, how='left')
    d = d.join(tnx, how='left')
    d = d.join(dxy, how='left')
    d['VIX'] = d['VIX'].ffill()
    d['TNX'] = d['TNX'].ffill()
    d['DXY'] = d['DXY'].ffill()
    d['VIX_change'] = d['VIX'].pct_change() * 100
    d['TNX_change'] = d['TNX'].pct_change() * 100
    d['DayOfWeek'] = d.index.dayofweek
    d['Month']     = d.index.month
    d['Target'] = (d['Close'].pct_change(-1) > 0).astype(int)
    return d.dropna()

df_feat = add_features(df)
FEAT = [c for c in df_feat.columns if c not in ['Open','High','Low','Close','Volume','Target']]

split = int(len(df_feat) * 0.80)
train = df_feat.iloc[:split]
X_tr, y_tr = train[FEAT], train['Target']

scale_pos = (y_tr == 0).sum() / (y_tr == 1).sum()
model = xgb.XGBClassifier(
    n_estimators=400, learning_rate=0.03, max_depth=4,
    subsample=0.8, colsample_bytree=0.7,
    scale_pos_weight=scale_pos,
    random_state=42, verbosity=0, eval_metric='logloss'
)
model.fit(X_tr, y_tr)

oggi = df_feat[FEAT].iloc[-1:]
proba = model.predict_proba(oggi)[0, 1]

THRESHOLD = 0.54
segnale   = "LONG" if proba >= THRESHOLD else "FLAT"
emoji     = "🟢" if segnale == "LONG" else "🔴"

ultimi = df.tail(7)[['Close']].copy()
ultimi['data']  = ultimi.index.strftime('%d/%m')
ultimi['close'] = ultimi['Close'].round(0).astype(int)
storico = ultimi[['data','close']].to_dict(orient='records')

rsi    = round(float(df_feat['RSI_14'].iloc[-1]), 1)
macd   = round(float(df_feat['MACD'].iloc[-1]), 1)
vix_v  = round(float(df_feat['VIX'].iloc[-1]), 1)
bb_pos = round(float(df_feat['BB_pos'].iloc[-1]) * 100, 1)

output = {
    "aggiornato":   datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC'),
    "data_analisi": df_feat.index[-1].strftime('%d/%m/%Y'),
    "ultimo_close": int(df.loc[df_feat.index[-1], 'Close']),
    "probabilita":  round(proba * 100, 1),
    "soglia":       round(THRESHOLD * 100, 1),
    "segnale":      segnale,
    "emoji":        emoji,
    "storico":      storico,
    "indicatori": {
        "RSI_14": rsi,
        "MACD":   macd,
        "VIX":    vix_v,
        "BB_pos": bb_pos
    }
}

with open('docs/docs/signal.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"{emoji} Segnale: {segnale}  |  Probabilità: {proba*100:.1f}%")
