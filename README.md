# 📈 Nasdaq 100 — Segnale IA Giornaliero

Sito web che mostra ogni sera il segnale del modello XGBoost sul Nasdaq 100.
Si aggiorna automaticamente ogni giorno feriale alle 23:00 UTC tramite GitHub Actions.

---

## 🚀 Setup in 5 passi

### 1. Crea un account GitHub
Vai su [github.com](https://github.com) e registrati (è gratis).

### 2. Crea un nuovo repository
- Clicca su **New repository**
- Nome: `nasdaq-signal`
- Visibilità: **Public** (necessario per GitHub Pages gratis)
- Clicca **Create repository**

### 3. Carica i file
Carica tutti questi file nel repository mantenendo la struttura:

```
nasdaq-signal/
├── generate_signal.py
├── .github/
│   └── workflows/
│       └── daily_signal.yml
└── docs/
    ├── index.html
    └── signal.json
```

Puoi farlo trascinando i file direttamente su GitHub.

### 4. Attiva GitHub Pages
- Vai su **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main` / `docs`
- Clicca **Save**

Dopo 1-2 minuti il sito sarà online su:
`https://TUO-USERNAME.github.io/nasdaq-signal/`

### 5. Esegui il workflow manualmente la prima volta
- Vai su **Actions** → **Aggiorna Segnale Nasdaq 100**
- Clicca **Run workflow**
- Aspetta ~2 minuti

Da quel momento il sito si aggiorna automaticamente ogni sera!

---

## 📁 Struttura file

| File | Descrizione |
|------|-------------|
| `generate_signal.py` | Script Python che addestra il modello e genera il segnale |
| `.github/workflows/daily_signal.yml` | Automazione GitHub Actions (esecuzione giornaliera) |
| `docs/index.html` | Sito web |
| `docs/signal.json` | Dati del segnale (aggiornati automaticamente) |

---

## ⚠️ Disclaimer
Questo progetto è a scopo educativo e sperimentale.
Non costituisce consulenza finanziaria.
