import pathlib


def test_no_merchant_selector_in_static_files():
    root = pathlib.Path(__file__).parent.parent / 'static'
    assert root.exists(), f"static directory not found: {root}"
    files = list(root.rglob('*'))
    matches = []
    for f in files:
        if f.is_file() and f.suffix in ('.js', '.css', '.html'):
            text = f.read_text(encoding='utf-8', errors='ignore')
            if 'merchant-selector' in text:
                matches.append(str(f))

    assert matches == [
    ], f"Found leftover merchant-selector references in: {matches}"
