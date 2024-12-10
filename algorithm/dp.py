import math

class Tower:
    def __init__(self, damage, attack_speed, cost, name, is_magic=False):
        self.damage = damage
        self.attack_interval = attack_speed
        self.cost = cost
        self.name = name
        self.is_magic = is_magic
        self.dps = damage / attack_speed

class Monster:
    def __init__(self, hp, armor, magic_resist, name):
        self.hp = hp
        self.armor = armor
        self.magic_resist = magic_resist
        self.name = name

def init_game():
    """Initialize towers and monsters"""
    # Define dwelling time at each position
    position_times = {
        0: 3.71,    # First position stays for 3.71 seconds
        1: 6.00,    # Second position stays for 6.00 seconds
        2: 6.12,    # Third position stays for 6.12 seconds
        3: 6.02,    # Fourth position stays for 6.02 seconds
        4: 5.92     # Fifth position stays for 5.92 seconds
    }
    
    towers = [
        # Arrow Tower: Fast attack, cheap, suitable for low armor
        Tower(25, 0.5, 300, "ArrowTower", is_magic=False),  # 5 seconds = 250 damage, cost-effectiveness = 0.83

        # Cannon Tower: High damage, expensive, suitable for high HP
        Tower(120, 2.0, 800, "CannonTower", is_magic=False),  # 5 seconds = 300 damage, cost-effectiveness = 0.375

        # Magic Tower: Medium, suitable for high armor
        Tower(45, 1.0, 500, "MagicTower", is_magic=True)  # 5 seconds = 225 damage, cost-effectiveness = 0.45
    ]
    
    monsters = [
        # Small Monster 1: Low HP, low armor, high magic resist -> suitable for arrow tower
        Monster(120, 5, 60, "Quick Soldier"), 

        # Small Monster 2: Low HP, high armor, low magic resist -> suitable for magic tower
        Monster(120, 40, 10, "Armored Soldier"),

        # Elite: Medium HP, high resistances -> requires multiple towers
        Monster(250, 30, 30, "Elite Monster"),

        # BOSS: High HP, moderate resistance -> requires high damage
        Monster(400, 20, 20, "BOSS")
    ]
    
    return towers, monsters, position_times

def calculate_damage_over_path(placement, monster, position_times):
    """Calculate total damage monster receives from all towers"""
    total_damage = 0
    for pos, tower in placement:
        if tower.is_magic:
            damage = tower.damage * (1 - monster.magic_resist/100)
        else:
            damage = max(0, tower.damage - monster.armor)
            
        hits = math.floor(position_times[pos] / tower.attack_interval)
        total_damage += damage * hits
    
    return total_damage

def can_kill_monster(placement, monster, position_times):
    """Determine if the monster can be killed"""
    total_damage = calculate_damage_over_path(placement, monster, position_times)
    return total_damage >= monster.hp

def dp_placement(positions=5, initial_gold=3000):
    towers, monsters, position_times = init_game()
    dp = {}
    
    required_m1, required_m2, required_b1, required_b2 = 2, 2, 1, 1

    def update_requirements(current_placement, m1, m2, b1, b2):
        # If monster can be killed, set requirement to 0
        if m1 > 0 and can_kill_monster(current_placement, monsters[0], position_times):
            m1 = 0
        if m2 > 0 and can_kill_monster(current_placement, monsters[1], position_times):
            m2 = 0
        if b1 > 0 and can_kill_monster(current_placement, monsters[2], position_times):
            b1 = 0
        if b2 > 0 and can_kill_monster(current_placement, monsters[3], position_times):
            b2 = 0
        return m1, m2, b1, b2

    def solve(pos, m1, m2, b1, b2, gold_left, current_placement):
        # Update requirements
        m1, m2, b1, b2 = update_requirements(current_placement, m1, m2, b1, b2)
        
        # If all requirements are met, cost is 0 (no need to place more towers)
        if m1 == 0 and m2 == 0 and b1 == 0 and b2 == 0:
            return 0, current_placement

        if pos == 0:
            # No positions left and requirements not met
            return float('inf'), current_placement
            
        state = (pos, m1, m2, b1, b2, gold_left)
        if state in dp:
            return dp[state]
        
        min_cost = float('inf')
        best_placement = current_placement

        # Try not placing a tower
        cost, placement = solve(pos-1, m1, m2, b1, b2, gold_left, current_placement)
        if cost < min_cost:
            min_cost = cost
            best_placement = placement

        # Try placing each type of tower
        for tower in towers:
            if tower.cost <= gold_left:
                new_placement = [(pos-1, tower)] + current_placement
                new_m1, new_m2, new_b1, new_b2 = update_requirements(new_placement, m1, m2, b1, b2)
                
                # Continue trying other towers to find a cheaper solution
                new_cost, new_pl = solve(pos-1, new_m1, new_m2, new_b1, new_b2, gold_left - tower.cost, new_placement)
                total_cost = tower.cost + new_cost
                if total_cost < min_cost:
                    min_cost = total_cost
                    best_placement = new_pl

        dp[state] = (min_cost, best_placement)
        return dp[state]

    dp_cost, dp_result = solve(positions, required_m1, required_m2, required_b1, required_b2, initial_gold, [])

    # Extract tower positions and names
    tower_pos_output = [pos for pos, _ in dp_result]
    tower_name_output = [tower.name for _, tower in dp_result]

    return tower_pos_output, tower_name_output