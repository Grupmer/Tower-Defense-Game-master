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
    # Define attack durations for each position
    position_times = {
        0: 3.71,    # First position duration: 3.71 seconds
        1: 6.00,    # Second position duration: 6.00 seconds
        2: 6.12,    # Third position duration: 6.12 seconds
        3: 6.02,    # Fourth position duration: 6.02 seconds
        4: 5.92     # Fifth position duration: 5.92 seconds
    }
    
    towers = [
        Tower(25, 0.5, 300, "ArrowTower", is_magic=False),  # Fast attack speed, low cost, ideal for low armor
        Tower(120, 2.0, 800, "CannonTower", is_magic=False),  # High damage, expensive, good for high HP targets
        Tower(45, 1.0, 500, "MagicTower", is_magic=True)  # Moderate, effective against high armor
    ]
    
    monsters = [
        Monster(120, 5, 60, "Quick Minion"),  # Low HP, low armor, high magic resistance
        Monster(120, 40, 10, "Armored Minion"),  # Low HP, high armor, low magic resistance
        Monster(250, 30, 30, "Elite Monster"),  # Medium HP, high resistance, requires multiple towers
        Monster(400, 20, 20, "Boss")  # High HP, moderate resistance, needs high damage
    ]
    
    return towers, monsters, position_times

def calculate_damage_over_path(placement, monster, position_times):
    """Calculate total damage dealt to a monster by all towers"""
    total_damage = 0
    for pos, tower in placement:
        if tower.is_magic:
            damage = tower.damage * (1 - monster.magic_resist / 100)
        else:
            damage = max(0, tower.damage - monster.armor)
            
        hits = math.floor(position_times[pos] / tower.attack_interval)
        total_damage += damage * hits
    
    return total_damage

def can_kill_monster(placement, monster, position_times):
    """Determine whether a monster can be defeated"""
    total_damage = calculate_damage_over_path(placement, monster, position_times)
    return total_damage >= monster.hp

def improved_greedy_placement(positions=5, initial_gold=3000):
    """Optimized greedy algorithm: outputs tower positions and names"""
    towers, monsters, position_times = init_game()
    placement = []
    remaining_gold = initial_gold
    
    # Sort positions by attack duration in descending order
    sorted_positions = sorted(range(positions), key=lambda x: position_times[x], reverse=True)
    
    def calculate_tower_value(current_placement, tower, pos):
        """Calculate the comprehensive value of adding a tower"""
        value = 0
        new_placement = [(pos, tower)] + current_placement
        
        # Calculate change in the number of defeated monsters
        current_kills = sum(1 for monster in monsters 
                          if can_kill_monster(current_placement, monster, position_times) if current_placement)
        new_kills = sum(1 for monster in monsters 
                       if can_kill_monster(new_placement, monster, position_times))
        
        # Reward for additional kills
        if new_kills > current_kills:
            value += 10000 * (new_kills - current_kills)
        
        # Evaluate contribution to each monster's defeat
        for i, monster in enumerate(monsters):
            old_damage = calculate_damage_over_path(current_placement, monster, position_times) if current_placement else 0
            new_damage = calculate_damage_over_path(new_placement, monster, position_times)
            damage_increase = new_damage - old_damage
            
            # Calculate effective damage (exclude overflow)
            overflow = max(0, new_damage - monster.hp)
            effective_damage = damage_increase - overflow
            
            # Set base weight
            if old_damage < monster.hp:  # Monster not yet defeated
                weight = 5 if i >= 2 else 3  # Higher weight for Boss and Elite Monster
            else:  # Monster already defeated
                weight = 0.5  # Lower value for overkill
                
            # Position value adjustment
            position_weight = position_times[pos] / min(position_times.values())  # Relative to shortest time
            
            # Calculate contribution value for this monster
            monster_value = effective_damage * weight * position_weight
            
            # Bonus for near-optimal kills (90%-110% of HP)
            if 0.9 * monster.hp <= new_damage <= 1.1 * monster.hp:
                monster_value *= 1.5
                
            value += monster_value
        
        # Encourage balanced physical/magic towers
        magic_count = sum(1 for _, t in new_placement if t.is_magic)
        physical_count = len(new_placement) - magic_count
        
        if magic_count > 0 and physical_count > 0:
            value *= 1.2
        
        # Synergy between DPS and position duration
        dps_position_bonus = (tower.dps * position_times[pos]) / 10
        value *= (1 + dps_position_bonus)
        
        # Return cost-effectiveness ratio
        return value / tower.cost if tower.cost > 0 else 0
    
    # Iterate through positions sorted by attack duration
    for pos in sorted_positions:
        if remaining_gold < 300:  # Insufficient funds for cheapest tower
            break
            
        best_tower = None
        best_value = 0
        
        for tower in towers:
            if tower.cost <= remaining_gold:
                value = calculate_tower_value(placement, tower, pos)
                if value > best_value:
                    best_value = value
                    best_tower = tower
        
        if best_tower:
            placement.append((pos, best_tower))
            remaining_gold -= best_tower.cost
    
    # Sort placement by position for better readability
    placement.sort(key=lambda x: x[0])
    
    # Extract tower positions and names
    tower_pos_output = [pos for pos, _ in placement]
    tower_name_output = [tower.name for _, tower in placement]
    
    return tower_pos_output, tower_name_output