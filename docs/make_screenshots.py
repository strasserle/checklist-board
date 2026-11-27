# Renders index.html with a stubbed database and demo rows and saves one screenshot per theme.
# Needs: pip install playwright; playwright install chromium. Run: python docs/make_screenshots.py
import sys, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "screenshots")
from playwright.sync_api import sync_playwright
src = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
now = "2026-11-26T08:00:00.000Z"
def r(i, title, area, status, who, rank, detail="", note=""):
    return {"id": f"d{i}", "data": dict(title=title, area=area, status=status, who=who, rank=rank, detail=detail, note=note, createdAt=now, updatedAt=now, updatedBy="Claude" if who == "Claude" else "Me")}
rows = [
  r(1, "Add CSV export to the results table", "frontend", "doing", "Claude", 1000),
  r(2, "Write the API endpoint for saved filters", "backend", "todo", "Claude", 2000),
  r(3, "Rename columns in the sample sheet", "data", "todo", "Claude", 3000),
  r(4, "Fix the legend overlapping the plot", "frontend", "test", "Me", 1000, "Moved the legend below the plot; checked at three window widths."),
  r(5, "Dark-mode colours for the tooltips", "frontend", "test", "Me", 2000),
  r(6, "Try a second colour scale", "ideas", "later", "Claude", 1000),
  r(7, "Draft the methods outline", "writing", "todo", "Me", 1000),
  r(8, "Decide on the final dataset", "decide", "todo", "Me", 2000),
  r(9, "Set up the project repo", "backend", "done", "Me", 9000),
]
stub = """<script>
var __rows = %s;
window.claude = { use: function(){ return Promise.resolve({ collection: function(){ return {
  onSnapshot: function(cb){ cb({ docs: __rows.map(function(x){ return { id: x.id, data: function(){ return x.data; } }; }) }); },
  doc: function(){ return { update: function(){ return Promise.resolve(); }, delete: function(){ return Promise.resolve(); } }; },
  add: function(){ return Promise.resolve(); } }; } }); } };
</script>""" % json.dumps(rows)
page = "<!doctype html><html><head><meta charset=utf8><meta name=viewport content='width=device-width,initial-scale=1'></head><body>" + stub + src + "</body></html>"
open(os.path.join(OUT, "_demo.html"), "w", encoding="utf8").write(page)
with sync_playwright() as p:
    b = p.chromium.launch()
    for theme in ["light", "dark", "cute", "maritime", "hudri-wudri"]:
        ctx = b.new_context(viewport={"width": 1100, "height": 900}, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file:///" + os.path.join(OUT, "_demo.html"))
        [pg.click("#themeBtn") for _ in range({"light":0,"dark":1,"cute":2,"maritime":3,"hudri-wudri":4}[theme])]
        pg.wait_for_timeout(1500)
        pg.screenshot(path=os.path.join(OUT, f"{theme}.png"), full_page=True)
        print(theme, "errors:", errs)
        ctx.close()
    b.close()
