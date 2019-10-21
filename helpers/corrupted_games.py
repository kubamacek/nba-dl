import pandas as pd
game_inventory = pd.read_csv('~/nba-dl/data/game-inventory/all-games.csv')

corrupted_games = []
dups_gameid = game_inventory.pivot_table(index=["GAME_ID"], aggfunc='size')
for item in dups_gameid.iteritems():
    if item[1] != 2:
        corrupted_games.append(item[0])

print("Corrupted games:")
print(corrupted_games)

for item, row in game_inventory.iterrows():
    if row["GAME_ID"] in corrupted_games:
        game_inventory = game_inventory.drop(item)

<<<<<<< HEAD
game_inventory.to_csv('~/nba-dl/data/game-inventory/all-games-corrected.csv', index=False)
=======
game_inventory.to_csv('~/nba-dl/data/game-inventory/all-games-corrected.csv')
>>>>>>> 2c7cec03d3cd1caabf0aaac981c9a313dc4a0611
