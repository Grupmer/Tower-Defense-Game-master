# Game Project Overview

This project showcases a tower defense game we designed, focusing on strategic gameplay and optimization. The game involves placing towers to eliminate different types of monsters, each with unique attributes like health, armor, and magic resistance. The primary goal is to develop an effective placement strategy using the available resources to maximize tower efficiency and ensure monsters are defeated before they reach their destination.

## Key Features

	1.	Core Algorithms:
	The heart of this project lies in the implementation of Dynamic Programming (DP), Greedy algorithms, and Q learning. These algorithms are essential for solving the placement optimization problem, ensuring the most cost-effective tower deployment. You can explore these implementations in detail within the algorithm folder.
	2.	Game Elements:
	Towers: Various types of towers with unique abilities, such as physical damage and magic damage, are available for placement. Each tower has specific characteristics, including attack speed, cost, and suitability against different monster types.
	Monsters: Monsters are designed with distinct traits like high armor, magic resistance, or low health, requiring players to carefully select towers to counter them effectively.
	3.	Position Strategy:
	Monsters spend varying amounts of time at each position along the path. Players must strategically place towers at the right positions to maximize damage within the limited time monsters stay in each zone.

# How to Run the Game Demo

Running the game demo is simple and requires minimal setup. Follow the steps below to experience the project:
1. Ensure all necessary dependencies are installed. You can check the requirements.txt file for the required libraries.
2. Navigate to the project directory in your terminal.
3. Run the following command:

   python run.py

This will start the game demo, allowing you to test the gameplay and observe how the DP and Greedy algorithms optimize the tower placement.

## Folder Structure

algorithm/: Contains the core DP and Greedy algorithms that power the game’s optimization strategies.

enemies/: Defines the monster types and their attributes.

towers/: Includes definitions of tower types and their characteristics.

menu/ and main_menu/: Handles the game interface and menu interactions.

game_assets/: Stores visual or sound assets used in the game.

# Future Improvements

While the current game demo highlights strategic optimization and core gameplay, there is room for expanding the game with features like:

Enhanced visuals and animations.
Additional tower and monster types for increased complexity.
Advanced AI for generating dynamic challenges.

