"""
Created on Sat Feb  2 15:02:55 2024

@author: John Chui
"""

import requests

def get_fpl_data():
    # FPL API for general data (players, teams, etc.)
    fpl_data_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(fpl_data_url)
    fpl_data = response.json()
    
    # FPL API for fixtures data
    fixtures_url = "https://fantasy.premierleague.com/api/fixtures/"
    response_fixtures = requests.get(fixtures_url)
    fixtures_data = response_fixtures.json()
    
    return fpl_data, fixtures_data

def assess_fixture_difficulty(team_id, fixtures_data, upcoming_games=5):
    # Get fixtures for a team (home and away)
    team_fixtures = [fixture for fixture in fixtures_data if fixture['team_h'] == team_id or fixture['team_a'] == team_id]
    
    difficulty = 0
    for fixture in team_fixtures[:upcoming_games]:  # Consider the next few fixtures (default is 5)
        if fixture['team_h'] == team_id:
            difficulty += fixture['team_h_difficulty']
        elif fixture['team_a'] == team_id:
            difficulty += fixture['team_a_difficulty']
    
    return difficulty

def filter_players(players_data, position=None, max_price=None, min_games=5):
    filtered_players = players_data
    
    # Filter by position (1 = GK, 2 = DEF, 3 = MID, 4 = FWD)
    if position:
        filtered_players = [player for player in filtered_players if player['element_type'] == position]
    
    # Filter by price
    if max_price:
        filtered_players = [player for player in filtered_players if player['now_cost'] <= max_price * 10]
    
    # Filter by players who played a minimum number of games
    filtered_players = [player for player in filtered_players if player['minutes'] >= min_games * 90]
    
    return filtered_players

def recommend_future_players(players_data, fixtures_data, position=None, max_price=None, num_players=5, upcoming_games=5):
    """
    Recommend players based on their current form, stats, and upcoming fixture difficulty.
    """
    filtered_players = filter_players(players_data, position, max_price)
    recommendations = []

    for player in filtered_players:
        team_id = player['team']
        fixture_difficulty = assess_fixture_difficulty(team_id, fixtures_data, upcoming_games)
        
        # Convert form to float
        player_form = float(player['form']) if player['form'] else 0.0

        # Calculate points per game
        games_played = player['minutes'] / 90
        points_per_game = player['total_points'] / games_played if games_played > 0 else 0

        # Weighted formula to calculate future potential
        # (More weight to form, points per game and less to fixture difficulty)
        score = ((player_form * 2) + points_per_game) / fixture_difficulty
        
        # Only include players who are available
        if player['status'] == 'a':
            recommendations.append((player['web_name'], player['now_cost'] / 10, player_form, points_per_game, fixture_difficulty, score))
    
    # Sort by the calculated score
    recommendations.sort(key=lambda x: x[5], reverse=True)
    
    return recommendations[:num_players]

def display_recommendations(recommendations):
    print("Top Player Recommendations for Future Gameweeks:")
    for player_name, price, form, points_per_game, fixture_difficulty, score in recommendations:
        print(f"Player: {player_name}, Price: {price}m, Form: {form}, Points/Game: {points_per_game:.2f}, "
              f"Fixture Difficulty: {fixture_difficulty}, Score: {score:.2f}")

def get_user_input():
    # Get position input (optional)
    position = input("Enter position (1=GK, 2=DEF, 3=MID, 4=FWD) or leave blank for all: ")
    position = int(position) if position else None
    
    # Get price range input (optional)
    max_price = input("Enter maximum price per player (in million, e.g., 7.5) or leave blank for no limit: ")
    max_price = float(max_price) if max_price else None
    
    return position, max_price

if __name__ == "__main__":
    fpl_data, fixtures_data = get_fpl_data()
    players_data = fpl_data['elements']

    # Get user inputs
    position, max_price = get_user_input()

    # Get and display the top future player recommendations
    top_future_recommendations = recommend_future_players(players_data, fixtures_data, position, max_price)
    display_recommendations(top_future_recommendations)
