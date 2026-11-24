# Apps Support & Privacy

Repository centrale per le pagine di **Supporto** e **Privacy Policy** pubblicate su GitHub Pages all'indirizzo:

`https://kaliber94.github.io/apps-support/`

## Come funziona

Tutte le pagine HTML statiche sono generate da `build.py` (Python 3, nessuna dipendenza esterna) a partire da:

- `apps.json`: elenco delle app, email di supporto, lingue supportate e date di aggiornamento.
- `content/<slug>/privacy.<lang>.md`: testo in Markdown della Privacy Policy per ciascuna app e lingua.
- `assets/style.css`: stile condiviso tra tutte le pagine (supporta Light & Dark Mode).

Dopo aver modificato `apps.json` o un file Markdown, rigenera le pagine HTML con:

```bash
python3 build.py
```

Poi fai commit e push su `main`.

## Aggiungere una nuova app

1. Aggiungi un nuovo blocco nell'array `"apps"` di `apps.json` (con `slug`, `name`, `email`, `languages` come `["it", "en"]` + eventuali lingue extra; imposta `"has_privacy": false` se l'app ha solo la pagina di supporto).
2. Se `"has_privacy": true`, crea i file Markdown in `content/<slug>/privacy.<lang>.md` (es. `privacy.it.md`, `privacy.en.md`).
3. Esegui `python3 build.py`, verifica e fai push su GitHub.

## Attivare GitHub Pages (prima volta)

1. Vai su GitHub nella repo `kaliber94/apps-support` → **Settings** → **Pages**.
2. In **Build and deployment** → **Source**, scegli **Deploy from a branch**.
3. Seleziona branch **`main`** e cartella **`/ (root)`**, poi clicca **Save**.
