import random
from database import update_score


class NumberGame:
    def __init__(self):
        self.number_to_guess = random.randint(1, 100)

    def check_guess(self, guess: int) -> str:
        if guess < self.number_to_guess:
            return "Больше!"
        elif guess > self.number_to_guess:
            return "Меньше!"
        else:
            update_score(user_id, 10)  # Награда за победу
            return "Ты угадал! +10 очков."
