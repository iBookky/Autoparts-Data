import re
import json

# 1. Read index.html and extract all data-i18n and data-i18n-placeholder keys
with open('/Users/ibookky/Autoparts/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

data_i18n_keys = set(re.findall(r'data-i18n="([^"]+)"', html_content))
data_i18n_placeholder_keys = set(re.findall(r'data-i18n-placeholder="([^"]+)"', html_content))
all_html_keys = data_i18n_keys.union(data_i18n_placeholder_keys)

print(f"Total data-i18n keys in index.html: {len(data_i18n_keys)}")
print(f"Total data-i18n-placeholder keys in index.html: {len(data_i18n_placeholder_keys)}")
print(f"Total unique keys referenced in index.html: {len(all_html_keys)}")

# 2. Read frontend/js/i18n.js and parse TH and EN dictionaries
with open('/Users/ibookky/Autoparts/frontend/js/i18n.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Extract keys in th and en
# Simple parser for "key": "value"
th_match = re.search(r'th:\s*\{(.*?)\n\s*\},?\s*en:', js_content, re.DOTALL)
en_match = re.search(r'en:\s*\{(.*?)\n\s*\}\s*\};', js_content, re.DOTALL)

if not th_match or not en_match:
    print("ERROR: Could not parse TH and EN dictionaries in i18n.js")
    exit(1)

th_block = th_match.group(1)
en_block = en_match.group(1)

th_keys = set(re.findall(r'["\']([^"\']+)["\']\s*:', th_block))
en_keys = set(re.findall(r'["\']([^"\']+)["\']\s*:', en_block))

print(f"Total keys in I18N_DICTIONARY.th: {len(th_keys)}")
print(f"Total keys in I18N_DICTIONARY.en: {len(en_keys)}")

missing_in_th = all_html_keys - th_keys
missing_in_en = all_html_keys - en_keys
diff_th_en = th_keys.symmetric_difference(en_keys)

print("\n--- Missing in TH dictionary ---")
for k in sorted(missing_in_th):
    print("  -", k)

print("\n--- Missing in EN dictionary ---")
for k in sorted(missing_in_en):
    print("  -", k)

print("\n--- Difference between TH and EN keys ---")
for k in sorted(diff_th_en):
    print("  -", k)
