import base64
import os

os.makedirs("images", exist_ok=True)

mapping = {
    "practice.b64.txt": "practice.jpg",
    "intimacy.b64.txt": "intimacy.jpg",
    "future_meeting.b64.txt": "future_meeting.jpg",
    "station_farewell.b64.txt": "station_farewell.jpg",
    "help_seeking.b64.txt": "help_seeking.jpg",
    "conflict.b64.txt": "conflict.jpg",
    "watch.b64.txt": "watch.jpg",
}

for src, dst in mapping.items():
    path = os.path.join("images", src)
    if not os.path.exists(path):
        print("缺少文件：", path)
        continue
    with open(path, encoding="utf-8") as f:
        b64 = f.read().strip()
    if "," in b64:
        b64 = b64.split(",")[1]
    with open(os.path.join("images", dst), "wb") as f:
        f.write(base64.b64decode(b64))
    print("已生成：", dst)