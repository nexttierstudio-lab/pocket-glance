"""Builds the site and serves it on localhost, so you can check it before publishing.

    python tools/serve.py              # build, then serve at http://localhost:8765/
    python tools/serve.py --port 9000  # another port
    python tools/serve.py --no-build   # serve what is already built
    python tools/serve.py --open       # also open the homepage in your browser

Stop it with Ctrl+C. Only this computer can reach it (it listens on 127.0.0.1).
Every link on the site is relative, so pages behave the same here as on GitHub Pages.
"""
import argparse
import functools
import http.server
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "privacy.html", "terms.html", "help.html"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-build", action="store_true", help="skip tools/site/build.py")
    ap.add_argument("--open", action="store_true", help="open the homepage in a browser")
    args = ap.parse_args()

    if not args.no_build:
        print("Building the homepage in every language...")
        if subprocess.run([sys.executable, str(ROOT / "tools" / "site" / "build.py")], cwd=ROOT).returncode:
            sys.exit("Build failed, fix the error above and run again.")

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    except OSError as e:
        sys.exit(f"Port {args.port} is busy ({e}). Try: python tools/serve.py --port {args.port + 1}")

    url = f"http://localhost:{args.port}/"
    print(f"\nServing {ROOT} at {url}")
    for page in PAGES[1:]:
        print(f"  {url}{page}")
    print(f"  {url}es/  (and the other language folders)")
    print("Press Ctrl+C to stop.\n")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
