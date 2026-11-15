import random
from collections import Counter
from django.shortcuts import render, redirect

def index(request):
    return render(request, "webapp/home.html")

def create_deck():

    suits = ["hearts", "diamond", "clubs", "spade"]

    ranks = [
        "1",
        "2", "3", "4", "5",
        "6", "7", "8", "9", "10",
        "J", "Q", "K"
    ]

    deck = []

    for suit in suits:
        for rank in ranks:
            deck.append(f"{rank}_{suit}.png")

    random.shuffle(deck)

    return deck

def check_rank_win(hand):

    values = [card.split("_")[0] for card in hand]

    counts = Counter(values)

    return sorted(counts.values()) == [2, 3]

def check_winner(hand):

    return check_rank_win(hand)

    # or check_suit_win(hand)

def five_cards(request):

    if "deck" not in request.session:

        deck = create_deck()

        hand = []

        for _ in range(5):
            hand.append(deck.pop())

        discard_pile = [deck.pop()]

        request.session["deck"] = deck
        request.session["hand"] = hand
        request.session["discard_pile"] = discard_pile
        request.session["selected_card"] = None

    hand = request.session["hand"]
    deck = request.session["deck"]
    discard_pile = request.session["discard_pile"]

    winner = check_winner(hand)

    if winner:

        request.session.flush()

        return render(
            request,
            "webapp/5_cards.html",
            {
                "winner": True
            }
        )

    return render(
        request,
        "webapp/5_cards.html",
        {
            "hand": hand,
            "deck_count": len(deck),
           "discard_card": discard_pile[-1] if discard_pile else None,
            "selected_card": request.session.get("selected_card"),
            "winner": False
        }
    )

def draw_from_deck(request):

    deck = request.session["deck"]

    if deck:

        request.session["selected_card"] = deck.pop()

        request.session["deck"] = deck

    return redirect("five_cards")

def take_discard(request):
    discard_pile = request.session.get("discard_pile", [])

    if discard_pile:
        selected_card = discard_pile.pop()

        request.session["selected_card"] = selected_card
        request.session["discard_pile"] = discard_pile

    return redirect("five_cards")

def replace_card(request, position):

    selected_card = request.session.get("selected_card")

    if not selected_card:
        return redirect("five_cards")

    hand = request.session["hand"]
    discard_pile = request.session["discard_pile"]

    old_card = hand[position]

    hand[position] = selected_card

    discard_pile.append(old_card)

    request.session["hand"] = hand
    request.session["discard_pile"] = discard_pile
    request.session["selected_card"] = None

    return redirect("five_cards")

def reset_game(request):

    request.session.flush()

    return redirect("five_cards")

def discard_selected(request):

    selected_card = request.session.get("selected_card")

    if selected_card:

        discard_pile = request.session.get("discard_pile", [])

        discard_pile.append(selected_card)

        request.session["discard_pile"] = discard_pile
        request.session["selected_card"] = None

    return redirect("five_cards")

def sekaku(request):

    if "sekaku_piles" not in request.session:

        deck = create_deck()

        piles = [
            deck[0:13],
            deck[13:26],
            deck[26:39],
            deck[39:52],
        ]

        request.session["sekaku_piles"] = piles
        request.session["sekaku_discard"] = []
        request.session["sekaku_hand"] = []

    piles = request.session["sekaku_piles"]
    discard = request.session["sekaku_discard"]
    hand = request.session["sekaku_hand"]

    game_over = all(len(pile) == 0 for pile in piles)

    return render(
        request,
        "webapp/sekaku.html",
        {
            "piles": piles,
            "discard": discard[-1] if discard else None,
            "hand": hand,
            "game_over": game_over,
            "score": len(hand),
        },
    )

def play_pile(request, pile):

    piles = request.session["sekaku_piles"]
    discard = request.session["sekaku_discard"]
    hand = request.session["sekaku_hand"]

    chosen_pile = piles[pile]

    if not chosen_pile:
        return redirect("sekaku")

    played_card = chosen_pile.pop()

    if discard:

        top_discard = discard[-1]

        played_suit = played_card.replace(".png", "").split("_")[1]
        discard_suit = top_discard.replace(".png", "").split("_")[1]

        if played_suit == discard_suit:

            hand.extend(discard)
            hand.append(played_card)
            discard = []
        else:

            discard.append(played_card)

    request.session["sekaku_piles"] = piles
    request.session["sekaku_discard"] = discard
    request.session["sekaku_hand"] = hand

    return redirect("sekaku")

def reset_sekaku(request):

    request.session.pop("sekaku_piles", None)
    request.session.pop("sekaku_discard", None)
    request.session.pop("sekaku_hand", None)

    return redirect("sekaku")

def create_topten_deck():

    suits = ["hearts", "diamond", "clubs", "spade"]

    ranks = [
        "1", "2", "3", "4", "5",
        "6", "7", "8", "9", "10"
    ]

    deck = []

    for suit in suits:
        for rank in ranks:
            deck.append(f"{rank}_{suit}.png")

    random.shuffle(deck)

    return deck

def topten(request):

    if "topten_deck" not in request.session:

        request.session["topten_deck"] = create_topten_deck()
        request.session["topten_area"] = []
        request.session["topten_score"] = 0
        request.session["topten_collection"] = []
        request.session["selected_indexes"] = []
        request.session["running_total"] = 0

    return render(
        request,
        "webapp/topten.html",
        {
            "area": request.session["topten_area"],
            "collection": request.session["topten_collection"],
            "score": request.session["topten_score"],
            "deck_count": len(request.session["topten_deck"]),
            "running_total": request.session.get("running_total", 0),
        }
    )

def draw_topten(request):

    deck = request.session["topten_deck"]
    area = request.session["topten_area"]
    collection = request.session["topten_collection"]

    if deck:

        card = deck.pop()
        area.append(card)

        request.session["topten_deck"] = deck
        request.session["topten_area"] = area
        request.session["topten_collection"] = collection

    return redirect("topten")

def select_topten(request, index):

    area = request.session["topten_area"]
    selected = request.session.get("selected_indexes", [])
    collection = request.session["topten_collection"]

    selected.append(index)

    total = 0

    for i in selected:
        total += int(area[i].split("_")[0])

    # SUCCESS
    if total == 10:

        cards_to_move = []
        cards_to_move.sort(
        key=lambda card: int(card.split("_")[0])
        )

        for i in selected:
            cards_to_move.append(area[i])

        for card in cards_to_move:
            collection.append(card)

        for i in sorted(selected, reverse=True):
            area.pop(i)

        request.session["topten_score"] += 1

        selected = []
        total = 0

    # FAILED
    elif total > 10:

        selected = []
        total = 0

    request.session["topten_area"] = area
    request.session["topten_collection"] = collection
    request.session["selected_indexes"] = selected
    request.session["running_total"] = total

    return redirect("topten")

def make_ten(request):

    pile = request.session["topten_pile"]
    selected = request.session["topten_selected"]

    total = 0

    for i in selected:
        value = int(pile[i].split("_")[0])
        total += value

    if total == 10:

        hand = request.session["topten_hand"]

        for i in selected:

            hand.append(pile[i])

            hand.sort(
            key=lambda x: int(x.split("_")[0]),
            reverse=True
        )

        for i in sorted(selected, reverse=True):
            pile.pop(i)

    request.session["topten_hand"] = hand

    request.session["topten_score"] += 1

    return redirect("topten")

def reset_topten(request):

    request.session.pop("topten_deck", None)
    request.session.pop("topten_pile", None)
    request.session.pop("topten_selected", None)
    request.session.pop("topten_score", None)

    return redirect("topten")

def dice(request):

    if "dice_set" not in request.session:

        request.session["dice_set"] = None
        request.session["dice1"] = 1
        request.session["dice2"] = 1
        request.session["message"] = "Roll the dice!"
        request.session["game_over"] = False

    return render(
        request,
        "webapp/dice.html",
        {
            "dice1": request.session["dice1"],
            "dice2": request.session["dice2"],
            "dice_set": request.session["dice_set"],
            "message": request.session["message"],
            "game_over": request.session["game_over"],
        }
    )

def roll_dice(request):

    if request.session.get("game_over"):
        return redirect("dice")

    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)

    total = dice1 + dice2

    request.session["dice1"] = dice1
    request.session["dice2"] = dice2

    current_set = request.session.get("dice_set")

    if current_set is None:

        if total == 7:

            request.session["message"] = (
                f"You rolled {total}! Instant Win!"
            )

            request.session["game_over"] = True

        else:

            request.session["dice_set"] = total

            request.session["message"] = (
                f"Your set is {total}. Roll again!"
            )

    else:

        if total == current_set:

            request.session["message"] = (
                f"You rolled {total}! You Win!"
            )

            request.session["game_over"] = True

        else:

            request.session["message"] = (
                f"You rolled {total}. Keep rolling..."
            )

    return redirect("dice")

def reset_dice(request):

    request.session.pop("dice_set", None)
    request.session.pop("dice1", None)
    request.session.pop("dice2", None)
    request.session.pop("message", None)
    request.session.pop("game_over", None)

    return redirect("dice")

def race100(request):

    challenge_cards = {
    1: "JACKPOT",
    2: "GO BACK 3",
    3: "KEEP 10% OF BET",
    4: "INCREASE BET OR GO BACK 3",
    5: "HALF MOVEMENT FOR 3 TURNS",
    6: "PLAY FOR OPPONENT",
    7: "CHOOSE OPPONENT",
    8: "SKIP NEXT 3 MOVES",
    9: "WIN IN 20 MOVES FOR DOUBLE",
    10: "DOUBLE MOVEMENT FOR 3 TURNS",
}

    if "race_pos" not in request.session:

        request.session["race_pos"] = 0
        request.session["race_entered"] = False
        request.session["race_roll"] = 1
        request.session["race_message"] = (
            "Roll a 6 to enter the race."
        )
        request.session["skip_turns"] = 0
        request.session["slow_turns"] = 0
        request.session["double_turns"] = 0

    if "race_cards" not in request.session:

        spaces = random.sample(range(2, 100), 10)

        race_cards = {}

        for i, space in enumerate(spaces, start=1):
            race_cards[str(space)] = i

        request.session["race_cards"] = race_cards

    board = []

    for row in range(10):

        start = row * 10 + 1
        end = start + 10

        numbers = list(range(start, end))

        if row % 2 == 1:
            numbers.reverse()

        board.append(numbers)

    board.reverse()

    return render(
        request,
        "webapp/race100.html",
        {
            "position": request.session["race_pos"],
            "entered": request.session["race_entered"],
            "roll": request.session["race_roll"],
            "message": request.session["race_message"],
            "board": board,
            "race_cards": request.session["race_cards"],
        }
    )

def race100_roll(request):

    roll = random.randint(1, 6)
    skip_turns = request.session.get("skip_turns", 0)

    if skip_turns > 0:

        request.session["skip_turns"] = skip_turns - 1

        request.session["race_message"] = (
        f"🎴 Turn skipped! {skip_turns - 1} skips remaining."
    )

        return redirect("race100")

    request.session["race_roll"] = roll

    entered = request.session["race_entered"]
    position = request.session["race_pos"]

    if not entered:

        if roll == 6:

            request.session["race_entered"] = True
            request.session["race_pos"] = 1

            request.session["race_message"] = (
                "You rolled a 6 and entered the race!"
            )

        else:

            request.session["race_message"] = (
                f"You rolled {roll}. Need a 6."
            )

    else:
        slow_turns = request.session.get("slow_turns", 0)

        if slow_turns > 0:

            roll = roll // 2

            request.session["slow_turns"] = slow_turns - 1

        double_turns = request.session.get("double_turns", 0)

        if double_turns > 0:

            roll = roll * 2

            request.session["double_turns"] = double_turns - 1

        position += roll
        cards = request.session.get("race_cards", {})
        cards = request.session.get("race_cards", {})

        if str(position) in cards:

            card_number = cards[str(position)]

            if card_number == 1:

                position = 100

                request.session["race_message"] = (
                "🎴 JACKPOT! You jump to 100!"
                )

            elif card_number == 2:

                position -= 3

                request.session["race_message"] = (
                "🎴 GO BACK 3 SPACES!"
                )

            elif card_number == 5:

                request.session["slow_turns"] = 3

                request.session["race_message"] = (
                "🎴 Half movement for next 3 turns!"
                )
            elif card_number == 8:

                request.session["skip_turns"] = 3

                request.session["race_message"] = (
                "🎴 Skip your next 3 turns!"
             )
            elif card_number == 10:

                request.session["double_turns"] = 3

                request.session["race_message"] = (
                "🎴 Double movement for next 3 turns!"
            )
            if str(position) in cards:

                card_number = cards[str(position)]

            request.session["race_message"] = (
                f"You landed on Challenge Card {card_number}"
            )

        else:

            request.session["race_message"] = (
            f"You moved {roll} spaces."
        )

    if not entered:

        if roll == 6:

            request.session["race_entered"] = True
            request.session["race_pos"] = 1

            request.session["race_message"] = (
            "You rolled a 6 and entered the race!"
            )

        else:

            request.session["race_message"] = (
                f"You rolled {roll}. Need a 6."
            )

    else:

        new_position = position

        if new_position > 100:

            request.session["race_message"] = (
            f"You rolled {roll}. Need exactly {100 - position} to win!"
        )

        else:

            position = new_position

        if position == 100:

            request.session["race_message"] = (
                "🏆 YOU WIN!"
            )

        else:

            request.session["race_message"] = (
                f"You moved {roll} spaces."
            )

        request.session["race_pos"] = position
    return redirect("race100")

def race100_reset(request):

    request.session.pop("race_pos", None)
    request.session.pop("race_entered", None)
    request.session.pop("race_roll", None)
    request.session.pop("race_message", None)

    return redirect("race100")

def slots(request):

    if "slot1" not in request.session:

        request.session["slot1"] = "❔"
        request.session["slot2"] = "❔"
        request.session["slot3"] = "❔"

        request.session["message"] = (
            "Press Start"
        )

    return render(
        request,
        "webapp/slots.html",
        {
            "slot1": request.session["slot1"],
            "slot2": request.session["slot2"],
            "slot3": request.session["slot3"],
            "message": request.session["message"],
        }
    )

def spin_slots(request):

    symbols = [
        "🍒",
        "🍋",
        "🔔",
        "⭐",
        "💎",
    ]

    slot1 = random.choice(symbols)
    slot2 = random.choice(symbols)
    slot3 = random.choice(symbols)

    request.session["slot1"] = slot1
    request.session["slot2"] = slot2
    request.session["slot3"] = slot3

    if slot1 == slot2 == slot3:

        if slot1 == "💎":

            request.session["message"] = (
                "🎰 GEMINI PLAY JACKPOT!"
            )

        else:

            request.session["message"] = (
                "🎉 YOU WIN!"
            )

    elif (
        slot1 == slot2
        or slot1 == slot3
        or slot2 == slot3
    ):

        request.session["message"] = (
            "🎲 Two Matches - Play Again!"
        )

    else:

        request.session["message"] = (
            "Try Again"
        )

    return redirect("slots")