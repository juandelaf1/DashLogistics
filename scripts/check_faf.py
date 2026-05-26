import requests, re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get("https://www.bts.gov/faf", headers=headers, timeout=30)
html = r.text

# Find ZIP links
links = set()
for m in re.finditer(r'href="([^"]+\.zip[^"]*)"', html, re.I):
    href = m.group(1)
    if "state" in href.lower() or "2018" in href:
        if href.startswith("/"):
            href = "https://www.bts.gov" + href
        links.add(href)

for l in links:
    print(l)

if not links:
    print("No ZIP links found. All hrefs containing FAF:")
    for m in re.finditer(r'href="([^"]*faf[^"]*)"', html, re.I):
        print(f"  {m.group(1)[:120]}")
