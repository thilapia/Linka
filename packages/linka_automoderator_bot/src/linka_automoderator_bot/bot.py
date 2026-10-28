"""Existing moderation rules with explicit client and database configuration."""

from importlib.resources import files
import json
import logging
from pathlib import Path
import re
import sqlite3
import time

from linka_bots_sdk import LinkaBotSdk

logger = logging.getLogger(__name__)
SCAN_INTERVAL = 120

# Termos de ódio/spam gravíssimos para bloquear SEMPRE (mesmo se o words.json falhar)
CRITICAL_HATE_WORDS = [
    "hitler",
    "nigger",
    "niggers",
    "n1gger",
    "n1gg3r",
    "niga",
    "nigga",
    "nazism",
    "nazi",
    "heil",
    "white supremacy",
    "white supramacy",
    "kkk",
]

# Palavras normais em PT/ES para garantir que NUNCA sejam bloqueadas
IGNORE_WORDS = {"cara", "como", "estan", "estais", "hola", "bien", "escaravelho"}

# Carrega palavras do words.json se existir
json_words = []
json_words = json.loads(files(__package__).joinpath("words.json").read_text(encoding="utf-8"))

# Junta tudo, limpa os ignorados e termos de 1~2 letras
all_bad_words = set(CRITICAL_HATE_WORDS + json_words)
valid_words = [w for w in all_bad_words if w.lower() not in IGNORE_WORDS and len(w) > 2]

# Compila Regex para palavras exatas
pattern_str = r"\b(" + "|".join(map(re.escape, valid_words)) + r")\b"
bad_words_regex = re.compile(pattern_str, re.IGNORECASE)

# Expressão para detectar português informal
PT_WORDS = {
    "olá",
    "opa",
    "eai",
    "bom",
    "dia",
    "tarde",
    "noite",
    "você",
    "tudo",
    "bem",
    "mano",
    "não",
    "sim",
    "obrigado",
    "vlw",
}
pt_regex = re.compile(r"\b(" + "|".join(map(re.escape, PT_WORDS)) + r")\b", re.IGNORECASE)

response_for_pt = (
    "Olá... aqui no linka recomendamos que fale inglês sabe, comunidade pequena e "
    "a maioria fala se puder se adaptar ao ingles ou conversar com outro que fala tambem ajudaria"
)

response_deleted_post = (
    "Your post was removed for violating the community guidelines "
    "(available at https://linkaProject.pythonanywhere.com/tos)\n"
    "If you believe this was a mistake, contact linka.plataform@gmail.com\n"
    "I am a bot, beep boop."
)

# Evita o envio repetido de avisos de idioma para os mesmos posts
WARNED_POSTS = set()


def normalize_text(text: str) -> str:
    """Substitui caracteres de leetspeak comuns para impedir desvios."""
    substitutions = {"@": "a", "4": "a", "1": "i", "!": "i", "0": "o", "3": "e", "$": "s"}
    normalized = text.lower()
    for char, replacement in substitutions.items():
        normalized = normalized.replace(char, replacement)
    return normalized


def moderate_once(client, database_path):
    """Moderate a single feed pass in the explicitly selected local database."""
    database_path = Path(database_path).expanduser().resolve()
    if not database_path.is_file():
        raise FileNotFoundError(f"Backend post database not found: {database_path}")
    feed = client.view_posts()
    if feed is None:
        return
    for post in feed:
        post_id = post["id"]
        text_post = post.get("text_post", "")
        username = post.get("username", "")
        if username == "AutoModerator" or "[ This post was removed" in text_post:
            continue
        normalized_post = normalize_text(text_post)
        if bad_words_regex.search(text_post) or bad_words_regex.search(normalized_post):
            # Direct local writes are a privileged bot concern, never an SDK API.
            with sqlite3.connect(database_path) as conn:
                conn.execute(
                    "UPDATE posts SET text_post = ? WHERE id = ?", (response_deleted_post, post_id)
                )
            logger.info("Post #%s moderated for a ToS violation", post_id)
            continue
        if pt_regex.search(text_post) and post_id not in WARNED_POSTS:
            WARNED_POSTS.add(post_id)
            logger.info("Language warning for post #%s", post_id)


def main(config_path, database_path):
    client = LinkaBotSdk(config_path=config_path)
    while True:
        try:
            moderate_once(client, database_path)
        except Exception:
            logger.exception("AutoModerator scan failed")
        time.sleep(SCAN_INTERVAL)
