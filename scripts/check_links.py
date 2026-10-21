"""Check every external link in index.html and report its status and final URL."""
import html
import re
import sys
import urllib.error
import urllib.request

SKIP = ("fonts.googleapis.com", "fonts.gstatic.com")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def check(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read(200_000).decode("utf-8", "ignore")
            m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            title = html.unescape(m.group(1)).strip()[:90] if m else ""
            return resp.status, resp.geturl(), title
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # DNS failure, timeout, TLS error
        return "ERR", url, type(e).__name__ + ": " + str(e)[:80]


def main():
    text = open("index.html", encoding="utf-8").read()
    urls = sorted({html.unescape(u) for u in re.findall(r'href="(https?://[^"]+)"', text)})
    urls = [u for u in urls if not any(s in u for s in SKIP)]
    bad = 0
    for url in urls:
        status, final, title = check(url)
        ok = isinstance(status, int) and status < 400
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {status} {url}")
        if final != url:
            print(f"       -> {final}")
        if title:
            print(f"       title: {title}")
    print(f"\n{len(urls) - bad}/{len(urls)} links OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
