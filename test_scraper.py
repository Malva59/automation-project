from scraper import scrape_genshin_codes
from database import get_new_codes


codes = scrape_genshin_codes()

new_codes = get_new_codes(codes)

print(f"Codes trouvés : {len(codes)}")
print(f"Nouveaux codes : {len(new_codes)}")

for code in new_codes:
    print(f"Nouveau : {code}")
