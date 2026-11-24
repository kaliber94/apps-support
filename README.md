# Apps Support & Privacy

Repository centrale per le pagine di **Supporto** e **Privacy Policy** pubblicate su GitHub Pages all'indirizzo:

`https://kaliber94.github.io/apps-support/`

## Convenzione URL

- La root `/` non mostra l'elenco delle app: ogni app è raggiungibile solo tramite link diretto.
- La lingua di default è **`en`** e il codice lingua è sempre esplicito nell'URL:
  - `/<slug>/<lang>/` (pagina hub della singola app con box Supporto e, se attiva, Privacy Policy)
  - `/<slug>/support/<lang>/` (es. `/mr-advisor/support/en/`, `/mr-advisor/support/it/`, `/mr-advisor/support/fr/`)
  - `/<slug>/privacy/<lang>/` (es. `/mr-advisor/privacy/en/`, `/mr-advisor/privacy/it/`, `/mr-advisor/privacy/fr/`)
- Gli URL senza lingua (`/<slug>/`, `/<slug>/support/` e `/<slug>/privacy/`) reindirizzano automaticamente a `en/`.

## Come funziona

Tutte le pagine HTML statiche sono generate da `build.py` (Python 3, nessuna dipendenza esterna) a partire da:

- `apps.json`: elenco delle app, email di supporto, lingue supportate (`default_language: "en"`), flag `has_privacy` e date di aggiornamento.
- `content/<slug>/privacy.<lang>.md`: testo in Markdown della Privacy Policy per ciascuna app e lingua.
- `assets/style.css`: stile condiviso tra tutte le pagine (supporta Light & Dark Mode).

Dopo aver modificato `apps.json` o un file Markdown, rigenera le pagine HTML con:

```bash
python3 build.py
```

Poi fai commit e push su `main`.

## Aggiungere una nuova app

1. Aggiungi un nuovo blocco nell'array `"apps"` di `apps.json` (con `slug`, `name`, `email`, `default_language: "en"`, `languages` come `["en", "it"]` + eventuali lingue extra; imposta `"has_privacy": false` se l'app ha solo la pagina di supporto).
2. Se `"has_privacy": true`, crea i file Markdown in `content/<slug>/privacy.<lang>.md` (es. `privacy.en.md`, `privacy.it.md`).
3. Esegui `python3 build.py`, verifica e fai commit/push su GitHub.
