#!/usr/bin/env python

import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from dataclasses import dataclass

@dataclass
class Data:
    receipt_id: str
    issuer: str
    date: str
    net_price: float
    vat_pcent: float
    vat: float
    price_total: float


def process(data: str):
    print("Received data:")
    content = json.loads(data)
    data = Data(**content)
    print(data)


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        process(post_data.decode('utf-8'))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')

def main(args):
    server_address = (args.host, args.port)
    httpd = HTTPServer(server_address, Handler)
    print(f"Starting server on {args.host}:{args.port}")
    httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="n8n Webhook Callback Listener")

    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8088)
    main(parser.parse_args())
