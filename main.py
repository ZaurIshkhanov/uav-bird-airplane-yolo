import json
import random
import time

import requests

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote


DATASET_DIR = Path("dataset")

CLASSES = [
    "uav",
    "bird",
    "airplane"
]

IMAGES_PER_CLASS = 5

SEARCH_QUERIES = {
    "uav": [
        "UAV drone flying",
        "quadcopter drone sky",
        "military UAV flying"
    ],

    "bird": [
        "bird flying sky",
        "bird in flight",
        "flying bird"
    ],

    "airplane": [
        "airplane flying sky",
        "passenger airplane flight",
        "aircraft flying"
    ]
}

def create_dataset_folders():
    for class_name in CLASSES:
        folder = DATASET_DIR / "raw" / class_name
        folder.mkdir(parents=True, exist_ok=True)

        print(f"Создана папка: {folder}")

def get_image_urls(query, offset=0):
    search_url = (
    "https://www.bing.com/images/search?"
    f"q={quote(query)}&first={offset}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        search_url,
        headers=headers,
        timeout=10
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    image_elements = soup.find_all(
        "a",
        class_="iusc"
    )

    urls = []

    for element in image_elements:
        data = json.loads(
            element.get("m", "{}")
        )

        image_url = data.get("murl")

        if image_url:
            urls.append(image_url)

    return urls

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url, timeout=10)

        if response.status_code == 200:

            with open(save_path, "wb") as file:
                file.write(response.content)

            return True

    except Exception as error:
        print(f"Ошибка загрузки: {error}")

    return False

def download_class_images(class_name, queries, limit):
    class_dir = DATASET_DIR / "raw" / class_name
    class_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    seen_urls = set()

    print(f"\n=== Скачивание класса: {class_name} ===")

    for query in queries:
        offset = 0

        while downloaded < limit:
            print(f"Поиск: {query}, offset: {offset}")

            image_urls = get_image_urls(
                query,
                offset
            )

            if not image_urls:
                break

            for image_url in image_urls:
                if downloaded >= limit:
                    break

                if image_url in seen_urls:
                    continue

                seen_urls.add(image_url)

                filename = (
                    class_dir /
                    f"{class_name}_{downloaded:04d}.jpg"
                )

                success = download_image(
                    image_url,
                    filename
                )

                if success:
                    downloaded += 1

                    print(
                        f"[{downloaded}/{limit}] "
                        f"{filename.name}"
                    )

                    time.sleep(
                        random.uniform(0.2, 0.7)
                    )

            offset += len(image_urls)

        if downloaded >= limit:
            break

    print(
        f"Готово: {class_name} — "
        f"{downloaded} изображений"
    )

def main():
    print("=== UAV / Bird / Airplane YOLO Project ===")

    create_dataset_folders()

    for class_name in CLASSES:
        download_class_images(
            class_name=class_name,
            queries=SEARCH_QUERIES[class_name],
            limit=IMAGES_PER_CLASS
        )


if __name__ == "__main__":
    main()