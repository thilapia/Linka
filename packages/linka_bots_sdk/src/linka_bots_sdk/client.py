"""Reusable HTTP bot client with explicit configuration and lazy authentication."""

import json
from pathlib import Path

import requests

from . import token_manager


class LinkaBotSdk:
    def __init__(self, config_path):
        self.config_path = Path(config_path).expanduser().resolve()
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        if not all(config.get(key) for key in ("url", "username", "password")):
            raise ValueError("Bot configuration requires url, username and password")
        self.name = config["username"]
        self.password = config["password"]
        self.url = config["url"].rstrip("/")
        self.token = None

    def _ensure_token(self):
        if not self.token:
            self.token = token_manager.new_session(self.url, self.name, self.password)
            if not self.token:
                raise RuntimeError("Unable to create bot session")

    def _get_bearer_headers(self) -> dict:
        self._ensure_token()
        token_str = (
            self.token.get("token")
            if isinstance(self.token, dict)
            else str(self.token)
            if self.token
            else ""
        )
        return {"Authorization": f"Bearer {token_str}"}

    def comment(self, text, post_id):
        try:
            payload = {"username": self.name, "text_comment": text, "post_id": post_id}
            requests.post(self.url + "/comments", json=payload, headers=self._get_bearer_headers())
        except:
            pass

    def view_posts(self) -> list:
        try:
            response = requests.get(url=self.url + "/feed", timeout=10)
            if response.status_code == 200:
                return response.json()  # Retorna o JSON (lista de dicts)
            return []
        except Exception as e:
            print(f"[SDK Error] Failed to fetch feed: {e}")
            return []

    def view_friends(self) -> list:
        try:
            self._ensure_token()
            my_name = str(self.name) if self.name else ""
            token_str = (
                self.token.get("token")
                if isinstance(self.token, dict)
                else str(self.token)
                if self.token
                else ""
            )
            payload = {"username": my_name, "token": token_str}
            response = requests.post(
                f"{self.url}/friends", json=payload, headers=self._get_bearer_headers(), timeout=10
            )
            if response.status_code == 200:
                friends_pairs = response.json().get("friends", [])
                list_friends = []
                for pair in friends_pairs:
                    if isinstance(pair, (list, tuple)):
                        for user in pair:
                            if user and isinstance(user, str) and user.lower() != my_name.lower():
                                if user not in list_friends:
                                    list_friends.append(user)
                return list_friends
            print(
                f"[SDK Error] Failed to fetch friends. Status: {response.status_code} | {response.text}"
            )
            return []
        except Exception as e:
            print(f"[SDK Error] Connection error in view_friends: {e}")
            return []

    def send_chat(self, message: str, receiver: str) -> bool:
        try:
            response = requests.post(
                f"{self.url}/send-message",
                json={"sender": self.name, "receiver": receiver, "message": message},
                headers=self._get_bearer_headers(),
                timeout=10,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"[SDK Error] Error sending message to {receiver}: {e}")
            return False

    def get_last_message(self, receiver: str):
        try:
            response = requests.post(
                f"{self.url}/view",
                json={"user1": self.name, "user2": receiver},
                headers=self._get_bearer_headers(),
                timeout=10,
            )
            if response.status_code == 200:
                messages_array = response.json().get("messages", [])
                if messages_array:
                    return messages_array[-1].get("message")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[SDK Error] Error fetching message history with {receiver}: {e}")
            return None
