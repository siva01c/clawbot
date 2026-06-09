import argparse
import json
import os
import random
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import chromadb
import gradio as gr
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MODEL = "gpt-4o-mini"
COOKIES_DIR = Path("cookies")
POSTS_PATH = Path("posts.json")


def random_sleep(min_seconds: float = 2, max_seconds: float = 5) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


def save_cookies(driver: uc.Chrome, filename: str = "linkedin_cookies.txt") -> None:
    COOKIES_DIR.mkdir(exist_ok=True)
    path = COOKIES_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        for cookie in driver.get_cookies():
            file.write(f"{cookie['name']}={cookie['value']}\n")
    print(f"Cookies saved to {path}")


def load_cookies(driver: uc.Chrome, filename: str = "linkedin_cookies.txt") -> bool:
    path = COOKIES_DIR / filename
    if not path.exists():
        return False

    driver.get("https://www.linkedin.com")
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            name, value = line.strip().split("=", 1)
            try:
                driver.add_cookie({"name": name, "value": value, "domain": ".linkedin.com"})
            except Exception as error:
                print(f"Could not load cookie '{name}': {error}")
    return True


def get_driver(headless: bool = True, chrome_version: int = 134):
    selenium_remote_url = os.getenv("SELENIUM_REMOTE_URL")
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    if selenium_remote_url:
        print(f"Using remote Selenium browser at: {selenium_remote_url}")
        return webdriver.Remote(command_executor=selenium_remote_url, options=options)

    print("Using local undetected-chromedriver browser")
    uc_options = uc.ChromeOptions()
    for argument in options.arguments:
        uc_options.add_argument(argument)
    return uc.Chrome(options=uc_options, version_main=chrome_version)


def linkedin_login(driver: uc.Chrome, username: str, password: str) -> bool:
    if load_cookies(driver):
        driver.get("https://www.linkedin.com/feed/")
        if "/feed" in driver.current_url:
            print("Logged in with existing cookies")
            return True

    driver.get("https://www.linkedin.com/login")
    username_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
    password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "password")))

    username_field.clear()
    password_field.clear()

    for char in username:
        username_field.send_keys(char)
        random_sleep(0.05, 0.15)

    for char in password:
        password_field.send_keys(char)
        random_sleep(0.05, 0.15)

    driver.find_element(By.XPATH, "//button[contains(@class, 'btn__primary--large')]").click()

    try:
        WebDriverWait(driver, 45).until(
            lambda active_driver: urlparse(active_driver.current_url).netloc == "www.linkedin.com"
            and ("/feed" in active_driver.current_url or "/checkpoint" in active_driver.current_url)
        )
    except TimeoutException:
        print(f"Login timeout. Current URL: {driver.current_url}")
        return False

    if "/checkpoint" in driver.current_url:
        print("LinkedIn security checkpoint detected. Complete verification then rerun.")
        return False

    save_cookies(driver)
    print("LinkedIn login successful")
    return True


def lazy_load_posts(driver: uc.Chrome, max_scrolls: int = 200) -> None:
    last_height = driver.execute_script("return document.body.scrollHeight")
    posts_count = len(driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2__control-menu-container"))

    for i in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight/4);")
        random_sleep(1.5, 3)

        if i % 4 == 3:
            new_posts_count = len(driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2__control-menu-container"))
            new_height = driver.execute_script("return document.body.scrollHeight")
            print(f"Scroll {i + 1}/{max_scrolls} | posts={new_posts_count} | height={new_height}")

            if new_posts_count == posts_count and new_height == last_height:
                print("No new posts loaded, stopping scroll")
                break

            posts_count = new_posts_count
            last_height = new_height

    driver.execute_script("window.scrollTo(0, 0);")


def get_posts(driver: uc.Chrome, target_name: str) -> dict[str, dict[str, str]]:
    posts: dict[str, dict[str, str]] = {}
    containers = driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2__control-menu-container")
    print(f"Found {len(containers)} potential post containers")

    for index, container in enumerate(containers):
        try:
            try:
                post_element = container.find_element(By.CLASS_NAME, "update-components-text")
                post_html = post_element.find_element(By.CSS_SELECTOR, "span[dir='ltr']").get_attribute("innerHTML")
                metadata_element = container.find_element(
                    By.CSS_SELECTOR,
                    "span.update-components-actor__sub-description.text-body-xsmall.t-black--light",
                )
                metadata_html = metadata_element.find_element(By.CSS_SELECTOR, "span.visually-hidden").get_attribute(
                    "innerHTML"
                )
            except NoSuchElementException:
                post_html = container.find_element(
                    By.CSS_SELECTOR, ".feed-shared-update-v2__description-wrapper"
                ).get_attribute("innerHTML")
                metadata_html = container.find_element(By.CSS_SELECTOR, ".feed-shared-actor__meta").text

            text = BeautifulSoup(post_html, "html.parser").get_text("\n", strip=True)
            metadata = BeautifulSoup(metadata_html, "html.parser").get_text("\n", strip=True)

            if not text.strip():
                continue

            unique_key = str(abs(hash(f"{metadata}|{text}")))
            posts[unique_key] = {"user": target_name, "metadata": metadata, "text": text}
        except Exception as error:
            print(f"Skipping post #{index}: {error}")

    print(f"Extracted {len(posts)} posts")
    return posts


class RagChat:
    def __init__(self, json_path: Path, target_name: str) -> None:
        self.target_name = target_name
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        os.makedirs("./chromadb", exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path="./chromadb")
        self.linkedin = self.chroma_client.get_or_create_collection(name="linkedin_posts")

        self.data = self.load_json_data(json_path)
        self.index_data(str(json_path))

    def load_json_data(self, json_path: Path) -> dict[str, Any]:
        with json_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def index_data(self, source_name: str) -> None:
        for idx, (post_id, post_data) in enumerate(self.data.items()):
            chroma_id = f"topic_{idx}"
            if self.linkedin.get(ids=[chroma_id]).get("ids"):
                continue

            document = "\n\n".join(
                [
                    f"User: {post_data.get('user', '')}",
                    f"Text: {post_data.get('text', '')}",
                    f"Metadata: {post_data.get('metadata', '')}",
                ]
            )

            self.linkedin.add(
                documents=[document],
                metadatas=[{"source": source_name, "index": idx, "title": post_id}],
                ids=[chroma_id],
            )

    def chat_completion(self, system_prompt: str, prompt: str) -> str:
        completion = self.openai.chat.completions.create(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content or "No response generated"

    def retrieve_context(self, query: str, top_k: int = 10) -> list[str]:
        results = self.linkedin.query(query_texts=[query], n_results=top_k)
        return results.get("documents", [[]])[0]

    def generate_response(self, user_prompt: str) -> str:
        contexts = self.retrieve_context(user_prompt)
        knowledge = " ".join(contexts) if contexts else ""

        system_prompt = (
            f"You are a personal assistant analyzing LinkedIn posts by {self.target_name}. "
            "Do not make up answers. Use only the knowledge base. "
            "If there is not enough info, answer: I don't know. "
            f"Knowledge base: {knowledge}"
        )
        return self.chat_completion(system_prompt, user_prompt)


def run_scraper(headless: bool) -> None:
    username = os.getenv("LINKEDIN_USER")
    password = os.getenv("LINKEDIN_PASSWORD")
    target_name = os.getenv("LINKEDIN_TARGET_NAME", "LinkedIn User")
    target_username = os.getenv("LINKEDIN_TARGET_USERNAME")

    if not username or not password or not target_username:
        raise ValueError("Missing required env vars: LINKEDIN_USER, LINKEDIN_PASSWORD, LINKEDIN_TARGET_USERNAME")

    driver = get_driver(headless=headless)
    try:
        if not linkedin_login(driver, username, password):
            raise RuntimeError("Unable to login to LinkedIn")

        driver.get(f"https://www.linkedin.com/in/{target_username}/recent-activity/all/")
        random_sleep(2, 4)
        lazy_load_posts(driver)
        posts = get_posts(driver, target_name=target_name)

        with POSTS_PATH.open("w", encoding="utf-8") as file:
            json.dump(posts, file, ensure_ascii=False, indent=2)
        print(f"Saved posts to {POSTS_PATH}")
    finally:
        driver.quit()


def run_chat(host: str, port: int, share: bool) -> None:
    if not POSTS_PATH.exists():
        raise FileNotFoundError("posts.json not found. Run scrape mode first.")

    target_name = os.getenv("LINKEDIN_TARGET_NAME", "LinkedIn User")
    rag = RagChat(POSTS_PATH, target_name=target_name)

    def respond(message: str, _history: list[dict[str, str]]) -> str:
        return rag.generate_response(message)

    demo = gr.ChatInterface(
        fn=respond,
        title="LinkedIn RAG Knowledge Base Chat",
        description="Ask questions about the content in posts.json",
        examples=["Summarize all posts", "What topics does this person discuss most often?"],
        theme="monochrome",
        chatbot=gr.Chatbot(type="messages"),
        type="messages",
    )
    demo.launch(server_name=host, server_port=port, share=share)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LinkedIn scraper + RAG chat converted from notebook")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scrape = subparsers.add_parser("scrape", help="Scrape LinkedIn posts into posts.json")
    scrape.add_argument("--headed", action="store_true", help="Run browser in headed mode")

    chat = subparsers.add_parser("chat", help="Run Gradio chat over posts.json")
    chat.add_argument("--host", default="0.0.0.0")
    chat.add_argument("--port", type=int, default=7860)
    chat.add_argument("--share", action="store_true")

    subparsers.add_parser("all", help="Run scrape then start chat")

    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    if args.command == "scrape":
        run_scraper(headless=not args.headed)
    elif args.command == "chat":
        run_chat(host=args.host, port=args.port, share=args.share)
    elif args.command == "all":
        run_scraper(headless=True)
        run_chat(host="0.0.0.0", port=7860, share=False)


if __name__ == "__main__":
    main()
