#! /usr/bin/env python3

import requests
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class n8nHandler(FileSystemEventHandler):
    def __init__(self, url, method="POST"):
        super().__init__()
        self._url = url
        self._method = method

    def on_created(self, event):
        ftype = "Directory" if event.is_directory else "File"
        print(f"{ftype} created: {event.src_path}")
        if not event.is_directory:
            self._send_request(event.src_path)

    def on_modified(self, event):
        ftype = "Directory" if event.is_directory else "File"
        print(f"{ftype} modified: {event.src_path}")

    def _send_request(self, path):
        print(f"Sending \"{path}\" to {self._url}")
        response = requests.request(
            method=self._method,
            url=self._url,
            files={"new_file": open(path, "rb")},
            headers={"Content-Type": "application/binary"},
        )

        content = response.json()
        code = content.get("code", "unknown")
        msg = content.get("message", "")
        hint = content.get("hint", "")

        if response.status_code != 200:
            print(f"ERROR ({code=})")
            print(msg)
            print(f"HINT: {hint}")
        else:
            print("SUCCESS")
            print(msg)

def main(args):

    base_url = f"{args.host}:{args.port}{args.hook_path}"
    if args.is_test:
        base_url += "-test"

    url = f"{base_url}/{args.hook_uuid}"
    observer = Observer()

    handler = n8nHandler(url=url, method=args.method)
    observer.schedule(handler, path=args.path, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="n8n Webhook Example")

    parser.add_argument("--host", type=str, default="http://localhost")
    parser.add_argument("--port", type=int, default=5678)
    parser.add_argument("--hook_uuid", "-uuid", type=str,
                        default="caa9b92e-e9ee-466a-a2cc-85d1fb6a2a8a",
                        help="The UUID of the n8n webhook")

    parser.add_argument("--hook_path", type=str, default="/webhook")
    parser.add_argument("--method", "-m", type=str, default="POST", choices=["GET", "POST", "PUT", "DELETE"])
    parser.add_argument("--is_test", "-test", action="store_true", help="Run in test mode")

    parser.add_argument("--path", "-p", type=str, default="folder", help="Path to the document directory")

    main(parser.parse_args())
