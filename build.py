#!/usr/bin/env python3
"""Generatore statico per pagine Support & Privacy Policy (GitHub Pages).

Usa solo la libreria standard Python 3.
Modifica `apps.json` e i file Markdown in `content/<slug>/privacy.<lang>.md`,
poi esegui `python3 build.py` per rigenerare tutte le pagine HTML statiche.

Convenzione URL:
- Ogni app ha la propria home in /<slug>/<lang>/ (con redirect da /<slug>/ a /<slug>/<default_lang>/),
  con box dedicati a Supporto e (se attiva) Privacy Policy.
- Ogni pagina include sempre il codice lingua nell'URL:
  /<slug>/<lang>/, /<slug>/support/<lang>/ e /<slug>/privacy/<lang>/
- Le directory senza lingua (/<slug>/, /<slug>/support/ e /<slug>/privacy/) reindirizzano
  automaticamente alla lingua di default (es. `en`).
- La root `/` non espone l'elenco delle app: ogni app è raggiungibile solo tramite link diretto.
"""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "apps.json"
CONTENT_DIR = ROOT / "content"

# Dizionario traduzioni UI condivise (aggiungi qui eventuali nuove lingue)
LANG_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "name": "English",
        "hub_badge": "Support & Privacy",
        "hub_title": "{app} – Support & Privacy",
        "hub_title_support_only": "{app} – Support",
        "hub_meta": "Official support and privacy policy pages for {app}.",
        "hub_meta_support_only": "Official support page for {app}.",
        "hub_lead": "Choose a section to get assistance or read the privacy policy.",
        "hub_lead_support_only": "Access official support resources for {app}.",
        "hub_support_desc": "Need help, have a question, or want to report an issue? Get in touch with us.",
        "hub_privacy_desc": "Learn how {app} handles your information and protects your privacy.",
        "hub_support_cta": "Open Support",
        "hub_privacy_cta": "Read Privacy Policy",
        "support_badge": "Support",
        "support_title": "Support – {app}",
        "support_heading": "{app} Support",
        "support_meta": "Official support page for the {app} app. Need help or want to report an issue? Contact us here.",
        "support_prompt": "Need help or want to report an issue?",
        "contact_label": "Contact us at:",
        "privacy_badge": "Privacy Policy",
        "privacy_title": "Privacy Policy – {app}",
        "privacy_heading": "{app} Privacy Policy",
        "privacy_meta": "Official privacy policy for the {app} app.",
        "privacy_link": "Read the Privacy Policy",
        "support_link": "Support page",
        "last_updated": "Last updated: {date}",
        "rights": "All rights reserved",
        "missing_privacy": "The privacy policy for {app} will be published shortly. For any questions, please contact us at {email}.",
    },
    "it": {
        "name": "Italiano",
        "hub_badge": "Supporto e Privacy",
        "hub_title": "{app} – Supporto e Privacy",
        "hub_title_support_only": "{app} – Supporto",
        "hub_meta": "Pagine ufficiali di supporto e informativa sulla privacy di {app}.",
        "hub_meta_support_only": "Pagina di supporto ufficiale di {app}.",
        "hub_lead": "Scegli una sezione per ricevere assistenza o consultare l’informativa sulla privacy.",
        "hub_lead_support_only": "Accedi al supporto ufficiale per {app}.",
        "hub_support_desc": "Hai bisogno di aiuto, hai una domanda o vuoi segnalare un problema? Contattaci.",
        "hub_privacy_desc": "Scopri come {app} gestisce le informazioni e tutela la tua privacy.",
        "hub_support_cta": "Vai al Supporto",
        "hub_privacy_cta": "Leggi la Privacy Policy",
        "support_badge": "Supporto",
        "support_title": "Supporto – {app}",
        "support_heading": "Supporto {app}",
        "support_meta": "Pagina di supporto ufficiale dell’app {app}. Hai bisogno di assistenza? Contattaci qui.",
        "support_prompt": "Hai bisogno di assistenza o vuoi segnalare un problema?",
        "contact_label": "Scrivici a:",
        "privacy_badge": "Privacy Policy",
        "privacy_title": "Privacy Policy – {app}",
        "privacy_heading": "Privacy Policy – {app}",
        "privacy_meta": "Informativa sulla privacy ufficiale dell’app {app}.",
        "privacy_link": "Leggi la Privacy Policy",
        "support_link": "Pagina di supporto",
        "last_updated": "Ultimo aggiornamento: {date}",
        "rights": "Tutti i diritti riservati",
        "missing_privacy": "L’informativa sulla privacy per {app} sarà disponibile a breve. Per qualsiasi domanda puoi contattarci all’indirizzo {email}.",
    },
    "es": {
        "name": "Español",
        "hub_badge": "Soporte y Privacidad",
        "hub_title": "{app} – Soporte y Privacidad",
        "hub_title_support_only": "{app} – Soporte",
        "hub_meta": "Páginas oficiales de soporte y política de privacidad de {app}.",
        "hub_meta_support_only": "Página oficial de soporte de {app}.",
        "hub_lead": "Elige una sección para recibir ayuda o consultar la política de privacidad.",
        "hub_lead_support_only": "Accede al soporte oficial de {app}.",
        "hub_support_desc": "¿Necesitas ayuda, tienes una pregunta o quieres reportar un problema? Contáctanos.",
        "hub_privacy_desc": "Descubre cómo {app} trata la información y protege tu privacidad.",
        "hub_support_cta": "Ir al Soporte",
        "hub_privacy_cta": "Leer la Privacidad",
        "support_badge": "Soporte",
        "support_title": "Soporte – {app}",
        "support_heading": "Soporte de {app}",
        "support_meta": "Página oficial de soporte de la app {app}. ¿Necesitas ayuda? Contáctanos aquí.",
        "support_prompt": "¿Necesitas ayuda o quieres reportar un problema?",
        "contact_label": "Escríbenos a:",
        "privacy_badge": "Política de Privacidad",
        "privacy_title": "Política de Privacidad – {app}",
        "privacy_heading": "Política de Privacidad – {app}",
        "privacy_meta": "Política de privacidad oficial de la app {app}.",
        "privacy_link": "Leer la Política de Privacidad",
        "support_link": "Página de soporte",
        "last_updated": "Última actualización: {date}",
        "rights": "Todos los derechos reservados",
        "missing_privacy": "La política de privacidad de {app} estará disponible pronto. Si tienes preguntas, escríbenos a {email}.",
    },
    "fr": {
        "name": "Français",
        "hub_badge": "Assistance et Confidentialité",
        "hub_title": "{app} – Assistance et Confidentialité",
        "hub_title_support_only": "{app} – Assistance",
        "hub_meta": "Pages officielles d’assistance et de politique de confidentialité pour {app}.",
        "hub_meta_support_only": "Page d’assistance officielle pour {app}.",
        "hub_lead": "Choisissez une section pour obtenir de l’aide ou consulter la politique de confidentialité.",
        "hub_lead_support_only": "Accédez à l’assistance officielle de {app}.",
        "hub_support_desc": "Besoin d’aide, une question ou un problème à signaler ? Contactez-nous.",
        "hub_privacy_desc": "Découvrez comment {app} traite les informations et protège votre vie privée.",
        "hub_support_cta": "Ouvrir l’assistance",
        "hub_privacy_cta": "Lire la confidentialité",
        "support_badge": "Assistance",
        "support_title": "Assistance – {app}",
        "support_heading": "Assistance {app}",
        "support_meta": "Page d’assistance officielle de l’app {app}. Besoin d’aide ? Contactez-nous ici.",
        "support_prompt": "Besoin d’aide ou envie de signaler un problème ?",
        "contact_label": "Écrivez-nous à :",
        "privacy_badge": "Confidentialité",
        "privacy_title": "Politique de confidentialité – {app}",
        "privacy_heading": "Politique de confidentialité – {app}",
        "privacy_meta": "Politique de confidentialité officielle de l’app {app}.",
        "privacy_link": "Lire la politique de confidentialité",
        "support_link": "Page d’assistance",
        "last_updated": "Dernière mise à jour : {date}",
        "rights": "Tous droits réservés",
        "missing_privacy": "La politique de confidentialité de {app} sera bientôt publiée. Pour toute question, contactez-nous à {email}.",
    },
    "de": {
        "name": "Deutsch",
        "hub_badge": "Support & Datenschutz",
        "hub_title": "{app} – Support & Datenschutz",
        "hub_title_support_only": "{app} – Support",
        "hub_meta": "Offizielle Support- und Datenschutzseiten für {app}.",
        "hub_meta_support_only": "Offizielle Support-Seite für {app}.",
        "hub_lead": "Wählen Sie einen Bereich für Hilfe oder die Datenschutzerklärung.",
        "hub_lead_support_only": "Offizieller Support für {app}.",
        "hub_support_desc": "Brauchen Sie Hilfe oder möchten Sie ein Problem melden? Kontaktieren Sie uns.",
        "hub_privacy_desc": "Erfahren Sie, wie {app} Ihre Daten behandelt und Ihre Privatsphäre schützt.",
        "hub_support_cta": "Support öffnen",
        "hub_privacy_cta": "Datenschutz lesen",
        "support_badge": "Support",
        "support_title": "Support – {app}",
        "support_heading": "{app} Support",
        "support_meta": "Offizielle Support-Seite für die App {app}. Brauchen Sie Hilfe? Kontaktieren Sie uns hier.",
        "support_prompt": "Brauchen Sie Hilfe oder möchten Sie ein Problem melden?",
        "contact_label": "Schreiben Sie uns an:",
        "privacy_badge": "Datenschutz",
        "privacy_title": "Datenschutzerklärung – {app}",
        "privacy_heading": "Datenschutzerklärung – {app}",
        "privacy_meta": "Offizielle Datenschutzerklärung für die App {app}.",
        "privacy_link": "Datenschutzerklärung lesen",
        "support_link": "Support-Seite",
        "last_updated": "Zuletzt aktualisiert: {date}",
        "rights": "Alle Rechte vorbehalten",
        "missing_privacy": "Die Datenschutzerklärung für {app} wird in Kürze veröffentlicht. Bei Fragen erreichen Sie uns unter {email}.",
    },
}

EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
SAFE_URL_PREFIXES = ("http://", "https://", "mailto:", "/", "./", "../", "#")


def t(lang: str, key: str, **kwargs: str) -> str:
    table = LANG_STRINGS.get(lang, LANG_STRINGS["en"])
    text = table.get(key, LANG_STRINGS["en"][key])
    return text.format(**kwargs) if kwargs else text


def rel_dir_url(from_dir: str, to_dir: str) -> str:
    """Restituisce l'URL relativo pulito con slash finale tra due cartelle."""
    src = from_dir or "."
    dst = to_dir or "."
    rel = os.path.relpath(dst, src).replace(os.sep, "/")
    if rel == ".":
        return "./"
    return f"{rel}/"


def rel_file_url(from_dir: str, to_file: str) -> str:
    """Restituisce l'URL relativo verso un file statico (es. assets/style.css)."""
    src = from_dir or "."
    return os.path.relpath(to_file, src).replace(os.sep, "/")


def app_hub_dir(slug: str, lang: str) -> str:
    """Restituisce il percorso della pagina hub della singola app con lingua esplicita."""
    return f"{slug}/{lang}"


def section_dir(slug: str, section: str, lang: str) -> str:
    """Restituisce sempre il percorso con la lingua esplicita nell'URL."""
    return f"{slug}/{section}/{lang}"


def format_inline(text: str) -> str:
    """Converte formattazione inline Markdown in HTML sicuro."""
    parts = re.split(r"(`[^`]+`)", text)
    rendered: list[str] = []

    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            rendered.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue

        escaped = html.escape(part, quote=True)
        placeholders: list[str] = []

        def _replace_link(match: re.Match[str]) -> str:
            label = match.group(1)
            raw_url = html.unescape(match.group(2)).strip()
            if not raw_url.startswith(SAFE_URL_PREFIXES):
                return match.group(0)
            attrs = ' target="_blank" rel="noopener noreferrer"' if raw_url.startswith(("http://", "https://")) else ""
            token = f"__LINK_{len(placeholders)}__"
            placeholders.append(f'<a href="{html.escape(raw_url, quote=True)}"{attrs}>{label}</a>')
            return token

        escaped = LINK_RE.sub(_replace_link, escaped)
        escaped = BOLD_RE.sub(r"<strong>\1</strong>", escaped)
        escaped = ITALIC_RE.sub(r"<em>\1</em>", escaped)
        escaped = EMAIL_RE.sub(r'<a href="mailto:\1">\1</a>', escaped)

        for idx, anchor in enumerate(placeholders):
            escaped = escaped.replace(f"__LINK_{idx}__", anchor)

        rendered.append(escaped)

    return "".join(rendered)


def markdown_to_html(md_text: str) -> tuple[str | None, str]:
    """Converte Markdown essenziale in HTML. Se inizia con '# Titolo', lo estrae come h1."""
    lines = md_text.replace("\r\n", "\n").split("\n")
    extracted_h1: str | None = None

    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines) and lines[idx].startswith("# ") and not lines[idx].startswith("## "):
        extracted_h1 = lines[idx][2:].strip()
        idx += 1

    blocks: list[str] = []
    n = len(lines)

    while idx < n:
        line = lines[idx]
        stripped = line.strip()

        if not stripped:
            idx += 1
            continue

        if stripped in ("---", "***", "___"):
            blocks.append("<hr>")
            idx += 1
            continue

        heading_match = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            blocks.append(f"<h{level}>{format_inline(heading_match.group(2).strip())}</h{level}>")
            idx += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while idx < n and lines[idx].strip().startswith(">"):
                quote_lines.append(lines[idx].strip().lstrip(">").strip())
                idx += 1
            quote_html = "<br>".join(format_inline(q) for q in quote_lines if q)
            blocks.append(f"<blockquote><p>{quote_html}</p></blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while idx < n and re.match(r"^[-*]\s+", lines[idx].strip()):
                item_text = re.sub(r"^[-*]\s+", "", lines[idx].strip())
                items.append(f"<li>{format_inline(item_text)}</li>")
                idx += 1
            blocks.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while idx < n and re.match(r"^\d+\.\s+", lines[idx].strip()):
                item_text = re.sub(r"^\d+\.\s+", "", lines[idx].strip())
                items.append(f"<li>{format_inline(item_text)}</li>")
                idx += 1
            blocks.append("<ol>\n" + "\n".join(items) + "\n</ol>")
            continue

        para_lines: list[str] = []
        while idx < n:
            cur = lines[idx].strip()
            if (
                not cur
                or cur in ("---", "***", "___")
                or cur.startswith(">")
                or re.match(r"^#{1,4}\s+", cur)
                or re.match(r"^[-*]\s+", cur)
                or re.match(r"^\d+\.\s+", cur)
            ):
                break
            para_lines.append(cur)
            idx += 1
        blocks.append(f"<p>{format_inline(' '.join(para_lines))}</p>")

    return extracted_h1, "\n".join(blocks)


def render_hreflangs(current_dir: str, lang_dirs: dict[str, str], default_lang: str) -> str:
    tags = []
    for lang, target_dir in lang_dirs.items():
        href = rel_dir_url(current_dir, target_dir)
        tags.append(f'  <link rel="alternate" hreflang="{html.escape(lang)}" href="{href}">')
    if default_lang in lang_dirs:
        default_href = rel_dir_url(current_dir, lang_dirs[default_lang])
        tags.append(f'  <link rel="alternate" hreflang="x-default" href="{default_href}">')
    return "\n".join(tags)


def render_lang_nav(current_lang: str, current_dir: str, lang_dirs: dict[str, str]) -> str:
    items = []
    for lang, target_dir in lang_dirs.items():
        label = html.escape(LANG_STRINGS.get(lang, {}).get("name", lang.upper()))
        if lang == current_lang:
            items.append(f'<span class="lang-active">{label}</span>')
        else:
            href = rel_dir_url(current_dir, target_dir)
            items.append(f'<a href="{href}">{label}</a>')
    sep = ' <span class="lang-sep" aria-hidden="true">·</span> '
    return f'<nav class="lang-nav" aria-label="Language">{sep.join(items)}</nav>'


def render_page(
    *,
    lang: str,
    title: str,
    description: str,
    css_href: str,
    hreflangs_html: str,
    body_class: str,
    card_class: str,
    body_html: str,
    extra_head: str = "",
) -> str:
    body_attr = f' class="{body_class}"' if body_class else ""
    extra_lines = f"\n{extra_head}" if extra_head else ""
    hreflang_lines = f"\n{hreflangs_html}" if hreflangs_html else ""
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">{extra_lines}{hreflang_lines}
  <link rel="stylesheet" href="{css_href}">
</head>
<body{body_attr}>
  <main class="{card_class}">
{body_html}
  </main>
</body>
</html>
"""


def render_redirect_page(*, lang: str, title: str, target_href: str, css_href: str) -> str:
    escaped_target = html.escape(target_href, quote=True)
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta http-equiv="refresh" content="0; url={escaped_target}">
  <link rel="canonical" href="{escaped_target}">
  <link rel="stylesheet" href="{css_href}">
  <script>window.location.replace({json.dumps(target_href)});</script>
</head>
<body>
  <main class="card card-support">
    <p class="lead">Redirecting…</p>
    <p><a href="{escaped_target}">Continue</a></p>
  </main>
</body>
</html>
"""


def write_html(rel_dir: str, content: str) -> Path:
    out_dir = ROOT / rel_dir if rel_dir else ROOT
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(content, encoding="utf-8")
    return out_file


def build() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    site = config["site"]
    apps = config["apps"]

    site_default_lang: str = site.get("default_language", "en")
    base_url: str = site.get("base_url", "").rstrip("/")
    generated: list[str] = []

    # 1. Root page neutra (nessun elenco app pubblico: accesso solo tramite link diretto)
    root_title = site.get("root_title", "App Support")
    root_heading = site.get("root_heading", "App Support")
    root_message = site.get(
        "root_message",
        "Please use the direct support or privacy policy link provided on the App Store or inside your app.",
    )
    year = site.get("copyright_year", 2026)
    owner = site.get("copyright_owner", "")
    root_footer = f"© {year} {owner} – {t(site_default_lang, 'rights')}" if owner else f"© {year}"

    root_body = f"""    <h1>{html.escape(root_heading)}</h1>
    <p class="lead">{html.escape(root_message)}</p>
    <footer>
      <span>{html.escape(root_footer)}</span>
    </footer>"""

    root_html = render_page(
        lang=site_default_lang,
        title=root_title,
        description=root_message,
        css_href="assets/style.css",
        hreflangs_html="",
        body_class="",
        card_class="card card-support",
        body_html=root_body,
        extra_head='  <meta name="robots" content="noindex, nofollow">',
    )
    out = write_html("", root_html)
    generated.append(str(out.relative_to(ROOT)))

    # 2. Per-app Support & Privacy Policy pages (sempre con /<lang>/ nell'URL)
    for app in apps:
        slug = app["slug"]
        app_name = app["name"]
        email = app.get("email", site["default_email"])
        app_langs: list[str] = app["languages"]
        app_def: str = app.get("default_language", site_default_lang)
        app_year = app.get("copyright_year", year)
        has_privacy: bool = app.get("has_privacy", True)

        hub_dirs = {l: app_hub_dir(slug, l) for l in app_langs}
        support_dirs = {l: section_dir(slug, "support", l) for l in app_langs}
        privacy_dirs = {l: section_dir(slug, "privacy", l) for l in app_langs} if has_privacy else {}

        # Redirect /<slug>/ -> /<slug>/<default_lang>/
        hub_title_key = "hub_title" if has_privacy else "hub_title_support_only"
        app_redirect = render_redirect_page(
            lang=app_def,
            title=t(app_def, hub_title_key, app=app_name),
            target_href=f"{app_def}/",
            css_href=rel_file_url(slug, "assets/style.css"),
        )
        out = write_html(slug, app_redirect)
        generated.append(str(out.relative_to(ROOT)))

        # Redirect /<slug>/support/ -> /<slug>/support/<default_lang>/
        sup_base_dir = f"{slug}/support"
        sup_redirect = render_redirect_page(
            lang=app_def,
            title=t(app_def, "support_title", app=app_name),
            target_href=f"{app_def}/",
            css_href=rel_file_url(sup_base_dir, "assets/style.css"),
        )
        out = write_html(sup_base_dir, sup_redirect)
        generated.append(str(out.relative_to(ROOT)))

        if has_privacy:
            # Redirect /<slug>/privacy/ -> /<slug>/privacy/<default_lang>/
            priv_base_dir = f"{slug}/privacy"
            priv_redirect = render_redirect_page(
                lang=app_def,
                title=t(app_def, "privacy_title", app=app_name),
                target_href=f"{app_def}/",
                css_href=rel_file_url(priv_base_dir, "assets/style.css"),
            )
            out = write_html(priv_base_dir, priv_redirect)
            generated.append(str(out.relative_to(ROOT)))

        for lang in app_langs:
            # --- App hub page (/<slug>/<lang>/) ---
            cur_hub_dir = hub_dirs[lang]
            hub_css_href = rel_file_url(cur_hub_dir, "assets/style.css")
            hub_hreflangs = render_hreflangs(cur_hub_dir, hub_dirs, app_def)
            hub_lang_nav = render_lang_nav(lang, cur_hub_dir, hub_dirs)
            hub_sup_href = rel_dir_url(cur_hub_dir, support_dirs[lang])

            hub_boxes = [
                f"""      <article class="app-item">
        <div>
          <h2>{html.escape(t(lang, 'support_badge'))}</h2>
          <p>{html.escape(t(lang, 'hub_support_desc', app=app_name))}</p>
        </div>
        <div class="app-actions">
          <a class="btn btn-primary" href="{hub_sup_href}">{html.escape(t(lang, 'hub_support_cta'))}</a>
        </div>
      </article>"""
            ]

            if has_privacy:
                hub_priv_href = rel_dir_url(cur_hub_dir, privacy_dirs[lang])
                hub_boxes.append(
                    f"""      <article class="app-item">
        <div>
          <h2>{html.escape(t(lang, 'privacy_badge'))}</h2>
          <p>{html.escape(t(lang, 'hub_privacy_desc', app=app_name))}</p>
        </div>
        <div class="app-actions">
          <a class="btn btn-secondary" href="{hub_priv_href}">{html.escape(t(lang, 'hub_privacy_cta'))}</a>
        </div>
      </article>"""
                )

            hub_badge_key = "hub_badge" if has_privacy else "support_badge"
            hub_meta_key = "hub_meta" if has_privacy else "hub_meta_support_only"
            hub_lead_key = "hub_lead" if has_privacy else "hub_lead_support_only"

            hub_body = f"""    <div class="topbar">
      <span class="eyebrow">{html.escape(t(lang, hub_badge_key))}</span>
      {hub_lang_nav}
    </div>
    <h1>{html.escape(app_name)}</h1>
    <p class="lead">{html.escape(t(lang, hub_lead_key, app=app_name))}</p>
    <section class="app-list">
{chr(10).join(hub_boxes)}
    </section>
    <footer>
      <span>© {app_year} {html.escape(app_name)} – {html.escape(t(lang, 'rights'))}</span>
    </footer>"""

            hub_html = render_page(
                lang=lang,
                title=t(lang, hub_title_key, app=app_name),
                description=t(lang, hub_meta_key, app=app_name),
                css_href=hub_css_href,
                hreflangs_html=hub_hreflangs,
                body_class="",
                card_class="card card-wide",
                body_html=hub_body,
            )
            out = write_html(cur_hub_dir, hub_html)
            generated.append(str(out.relative_to(ROOT)))

            # --- Support page ---
            cur_dir = support_dirs[lang]
            css_href = rel_file_url(cur_dir, "assets/style.css")
            hreflangs = render_hreflangs(cur_dir, support_dirs, app_def)
            lang_nav = render_lang_nav(lang, cur_dir, support_dirs)

            privacy_link_block = ""
            if has_privacy:
                privacy_href = rel_dir_url(cur_dir, privacy_dirs[lang])
                privacy_link_block = f"""
    <div class="secondary-links">
      <a href="{privacy_href}">{html.escape(t(lang, 'privacy_link'))}</a>
    </div>"""

            support_body = f"""    <div class="topbar topbar-center">
      {lang_nav}
    </div>
    <span class="eyebrow">{html.escape(t(lang, 'support_badge'))}</span>
    <h1>{html.escape(t(lang, 'support_heading', app=app_name))}</h1>
    <p class="lead">{html.escape(t(lang, 'support_prompt'))}</p>
    <div class="contact-box">
      <p class="contact-label">{html.escape(t(lang, 'contact_label'))}</p>
      <a class="email-button" href="mailto:{html.escape(email)}">{html.escape(email)}</a>
    </div>{privacy_link_block}
    <footer>
      <span>© {app_year} {html.escape(app_name)} – {html.escape(t(lang, 'rights'))}</span>
    </footer>"""

            support_html = render_page(
                lang=lang,
                title=t(lang, "support_title", app=app_name),
                description=t(lang, "support_meta", app=app_name),
                css_href=css_href,
                hreflangs_html=hreflangs,
                body_class="",
                card_class="card card-support",
                body_html=support_body,
            )
            out = write_html(cur_dir, support_html)
            generated.append(str(out.relative_to(ROOT)))

            if not has_privacy:
                continue

            # --- Privacy Policy page ---
            cur_dir = privacy_dirs[lang]
            css_href = rel_file_url(cur_dir, "assets/style.css")
            hreflangs = render_hreflangs(cur_dir, privacy_dirs, app_def)
            lang_nav = render_lang_nav(lang, cur_dir, privacy_dirs)
            support_href = rel_dir_url(cur_dir, support_dirs[lang])

            md_path = CONTENT_DIR / slug / f"privacy.{lang}.md"
            if md_path.exists():
                extracted_h1, prose_html = markdown_to_html(md_path.read_text(encoding="utf-8"))
            else:
                extracted_h1 = None
                prose_html = f"<p>{format_inline(t(lang, 'missing_privacy', app=app_name, email=email))}</p>"

            heading = extracted_h1 or t(lang, "privacy_heading", app=app_name)
            updated = (app.get("privacy_updated") or {}).get(lang, "").strip()
            updated_html = (
                f'\n    <p class="meta-date">{html.escape(t(lang, "last_updated", date=updated))}</p>'
                if updated
                else ""
            )

            privacy_body = f"""    <div class="topbar">
      <span class="eyebrow">{html.escape(t(lang, 'privacy_badge'))}</span>
      {lang_nav}
    </div>
    <h1>{html.escape(heading)}</h1>{updated_html}
    <article class="prose">
{prose_html}
    </article>
    <footer>
      <span>© {app_year} {html.escape(app_name)} – {html.escape(t(lang, 'rights'))}</span>
      <a href="{support_href}">{html.escape(t(lang, 'support_link'))}</a>
    </footer>"""

            privacy_html = render_page(
                lang=lang,
                title=t(lang, "privacy_title", app=app_name),
                description=t(lang, "privacy_meta", app=app_name),
                css_href=css_href,
                hreflangs_html=hreflangs,
                body_class="page-document",
                card_class="card card-wide",
                body_html=privacy_body,
            )
            out = write_html(cur_dir, privacy_html)
            generated.append(str(out.relative_to(ROOT)))

    print(f"Generazione completata: {len(generated)} pagine HTML aggiornate.")
    if base_url:
        print("\nURL GitHub Pages:")
        for app in apps:
            slug = app["slug"]
            has_privacy = app.get("has_privacy", True)
            print(f"\n  {app['name']} (default: {app.get('default_language', site_default_lang)}):")
            for lang in app["languages"]:
                hub = app_hub_dir(slug, lang)
                sup = section_dir(slug, "support", lang)
                print(f"    [{lang}] Home    : {base_url}/{hub}/")
                print(f"    [{lang}] Support : {base_url}/{sup}/")
                if has_privacy:
                    priv = section_dir(slug, "privacy", lang)
                    print(f"    [{lang}] Privacy : {base_url}/{priv}/")


if __name__ == "__main__":
    build()
