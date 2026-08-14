from scraper import scrape_all_codes


results = scrape_all_codes()

for game, codes in results.items():
    print(f"\n{game} : {len(codes)} codes")

    for code in codes:
        print(f"  - {code}")
