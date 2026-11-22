# PDF → web study guide

How `src/content/ss02.json`, `src/content/ss03.json` and the figures in `public/guides/` were made from the study-guide PDFs.

The PDFs' Bangla and Arabic text cannot be extracted reliably (the embedded font maps produce garbled characters), so
the converter replaces every Bangla/Arabic run with a placeholder, and the correct text is kept in `fixes-<slug>.json`
(keyed by the garbled text, transcribed by hand from page images). A value starting with `!` is inserted as raw HTML.

```bash
pip install pymupdf pillow
# convert: <pdf> <slug> <out dir> <pages to skip: cover, table of contents>
python3 conv.py Standard_02.pdf ss02 out 1,4,5
# images of every Bangla/Arabic snippet still to transcribe, written to crops/
python3 crops.py
# write {placeholder id: correct text} to f.json, then merge it into fixes-ss02.json
python3 addfix.py ss02 f.json
# render to the JSON the site loads
python3 render.py ss02 out/ss02.json fixes-ss02.json && cp out/ss02.json ../../src/content/
cp out/img/*.png ../../public/guides/
```

Then add the guide to `src/guides.ts`.
