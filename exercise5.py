#Devang Bafna and Ziya Aydin
#Exercise 5
class football_players:
    """
    """
    def __init__(self, name = "unknown", team = "unknown", assists = 0, score_list=[]):
        self.name = name
        self.team = team
        self.assists = assists
        self.score_list = score_list
    
    def __str__(self):
        return f'{self.name} plays for {self.team} and has assisted {self.assists} times and has scored against {self.score_list} .'

    def __add__(self, other):
        assists = (self.assists + other.assists) 
        print(f"Total assists is {assists}")

    def score(self, other):
        import random
        if random.random() < 0.70:
            print((f"{self.name} scores against {other.name}")) 
            self.score_list.append(other.name)
        else:
            print(f"{self.name} could not score against {other.name}!")

CR7 = football_players("Cristiano Ronaldo", "Manchester United", 7, score_list=[])
# print(CR7)
LM10 = football_players("Lionel Messi", "PSG", 8, score_list=[])
# print(LM10)
DB8 = football_players("Devang Bafna", "Bunty FC", 9, score_list=[])
ZA99 = football_players("Ziya Aydin", "Fenerbahce", 0, score_list=[])

CR7 + LM10

DB8.score(ZA99)
print(DB8)

CR7.score(ZA99)
print(CR7)

LM10.score(ZA99)
print(LM10)