from scraper import scrape_all_codes


results = scrape_all_codes()


for game, codes in results.items():

    print(f"\n{'=' * 50}")
    print(game)
    print(f"{'=' * 50}")

    for item in codes:

        print(f"\nCode : {item['code']}")

        print("Récompenses :")

        for reward in item["rewards"]:

            print(f"  - {reward}")
