#!/usr/bin/env python
from src.server import app
import aiohttp.web

if __name__ == "__main__":
    aiohttp.web.run_app(app(), port=8080)