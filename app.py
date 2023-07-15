from flask import Flask, request, jsonify, render_template_string

from flask_cors import CORS
import random



# Add your Poker functions here
def hand_value(hand):
  ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
  suits = ['h', 'd', 'c', 's']
  royal_flush = (14, 13, 12, 11, 10)
  worst_straight_flush = (14, 5, 4, 3, 2)
  straight_flush_value = 0

  suit_counts = {}
  for suit in suits:
    count = 0
    for card in hand:
      if card[1] == suit:
        count += 1
    suit_counts[suit] = count
  flush = [rank for rank, count in suit_counts.items() if count >= 5]

  if flush:
    flush_rank_counts = {}
    for rank in ranks:
      count = 0
      for card in hand:
        if card[0] == rank and card[1] == flush[0]:
          count += 1
      flush_rank_counts[rank] = count

    flush_rank_values = {}
    for i, rank in enumerate(ranks, start=2):
      flush_rank_values[rank] = i

    flush_single_cards = sorted(
      (rank for rank, count in flush_rank_counts.items() if count == 1),
      key=flush_rank_values.get,
      reverse=True)
    flush_single_cards = tuple(flush_rank_values[rank]
                               for rank in flush_single_cards)
    straight_flush = ()
    for x in range(0, len(flush_single_cards) - 1):
      if flush_single_cards[x] - 1 == flush_single_cards[x + 1]:
        count += 1
        straight_flush += (flush_single_cards[x], )
      else:
        count = 0
      if count == 4:
        straight_flush_value += 1
    flush_single_cards = flush_single_cards[:5]

    if flush_single_cards == royal_flush:
      return (10, )
    elif straight_flush_value == 1:
      return (9, ) + (straight_flush[0], )
    elif flush_single_cards == worst_straight_flush:
      return (9, 5)
    else:
      return (6, ) + flush_single_cards

  rank_counts = {}
  for rank in ranks:
    count = 0
    for card in hand:
      if card[0] == rank:
        count += 1
    rank_counts[rank] = count

  rank_values = {}
  for i, rank in enumerate(ranks, start=2):
    rank_values[rank] = i

  straight_ranks = [rank for rank in ranks if rank_counts[rank]]
  if len(straight_ranks) >= 5:
    for i in range(len(straight_ranks) - 4):
      if ranks.index(straight_ranks[i + 4]) - ranks.index(
          straight_ranks[i]) == 4:
        return (5, rank_values[straight_ranks[i + 4]])

  pairs = [rank for rank, count in rank_counts.items() if count == 2]

  three_of_a_kind = [rank for rank, count in rank_counts.items() if count == 3]

  four_of_a_kind = [rank for rank, count in rank_counts.items() if count == 4]

  single_cards = sorted(
    (rank for rank, count in rank_counts.items() if count == 1),
    key=rank_values.get,
    reverse=True)

  if four_of_a_kind:
    return (8, rank_values[four_of_a_kind[0]]) + tuple(
      rank_values[rank] for rank in single_cards)
  elif three_of_a_kind and pairs:
    return (7, rank_values[three_of_a_kind[0]], rank_values[pairs[0]])
  elif three_of_a_kind:
    return (4, rank_values[three_of_a_kind[0]]) + tuple(
      rank_values[rank] for rank in single_cards)
  elif len(pairs) == 2:
    high_pair, low_pair = sorted(pairs, key=rank_values.get, reverse=True)
    return (3, rank_values[high_pair], rank_values[low_pair]) + tuple(
      rank_values[rank] for rank in single_cards)
  elif len(pairs) == 1:
    return (2, rank_values[pairs[0]]) + tuple(rank_values[rank]
                                              for rank in single_cards)
  else:
    return (1, ) + tuple(rank_values[rank] for rank in single_cards)
  pass


def simulate_game_with_known_cards(hole_cards, opponent_hands, community_cards,
                  num_simulations):
  ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
  suits = ['h', 'd', 'c', 's']
  deck = [rank + suit for rank in ranks for suit in suits]

  # Remove the player's hole cards from the deck
  for card in hole_cards:
    deck.remove(card)

  # Remove opponents' hole cards from the deck
  for opponent_hand in opponent_hands:
    for card in opponent_hand:
      deck.remove(card)

  for card in community_cards:
    deck.remove(card)

  win_count = 0
  for _ in range(num_simulations):
    # Draw the flop, turn, and river cards
    rest_of_community_cards = random.sample(deck, 5 - len(community_cards))

    # Create the final hands by combining the hole cards and community cards
    player_hand = hole_cards + rest_of_community_cards + community_cards
    opponent_final_hands = [
      opponent_hand + rest_of_community_cards + community_cards
      for opponent_hand in opponent_hands
    ]

    # Evaluate the hands
    player_value = hand_value(player_hand)
    opponent_values = [
      hand_value(opponent_hand) for opponent_hand in opponent_final_hands
    ]

    # Check if the player's hand is better than all opponents' hands
    if all(player_value > opponent_value
           for opponent_value in opponent_values):
      win_count += 1

  return win_count / num_simulations
  pass

# Initialize your Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for this application

# @app.route('/')
# def home():
#     with open("!HandEvaluator.html", "r") as file:   # assuming your HTML file is named 'index.html'
#         html = file.read()
#     return render_template_string(html)

# @app.route('/calculate', methods=['POST'])
# def calculate():
#     # Get data from request
#     hands = request.get_json()

#     print(f"Received data: {hands}")  # Debug log

#     # Rest of your code...


# Define a route and method for your function
@app.route('/calculate', methods=['POST'])
def calculate():
    # Get data from request
    hands = request.get_json()

    # Get player's cards
    hole_cards = hands['player']

    # Get opponents' cards
    opponent_hands = [hand for id, hand in hands.items() if id != 'player' and id != "flop"]


    community_cards = hands["flop"]


    # Calculate win rate
    win_rate = simulate_game_with_known_cards(hole_cards, opponent_hands,community_cards, num_simulations=10000)

    # Convert to string percentage
    win_rate = f'{win_rate * 100:.2f}'

    # Return the response as JSON
    return jsonify(win_rate + "%")

# Run the application
if __name__ == "__main__":
    app.run(port=5000, use_reloader=False)  # You can specify any port you want here

