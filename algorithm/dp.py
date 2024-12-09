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
    """初始化塔和怪物"""
    # 定义每个位置的攻击时间
    position_times = {
        0: 3.71,    # 第一个位置停留3.71秒
        1: 6.00,    # 第二个位置停留6.00秒
        2: 6.12,    # 第三个位置停留6.12秒
        3: 6.02,    # 第四个位置停留6.02秒
        4: 5.92     # 第五个位置停留5.92秒
    }
    
    towers = [
        # 箭塔：攻速快,便宜,适合打低护甲
        Tower(25, 0.5, 300, "ArrowTower", is_magic=False),  # 5秒=250伤害,性价比=0.83

        # 炮塔：高伤害,贵,适合打高血量
        Tower(120, 2.0, 800, "CannonTower", is_magic=False),  # 5秒=300伤害,性价比=0.375

        # 魔法塔：中等,适合打高护甲
        Tower(45, 1.0, 500, "MagicTower", is_magic=True)  # 5秒=225伤害,性价比=0.45
    ]
    
    monsters = [
        # 小怪1：低血量,低护甲,高魔抗 -> 适合箭塔
        Monster(120, 5, 60, "快速小兵"), 

        # 小怪2：低血量,高护甲,低魔抗 -> 适合魔法塔
        Monster(120, 40, 10, "重甲小兵"),

        # 精英：中等血量,双高抗 -> 需要多塔配合
        Monster(250, 30, 30, "精英怪"),

        # BOSS：高血量,抗性适中 -> 需要高伤害
        Monster(400, 20, 20, "BOSS")
    ]
    
    return towers, monsters, position_times

def calculate_damage_over_path(placement, monster, position_times):
    """计算怪物经过所有塔获得的总伤害"""
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
    """判断是否能击杀怪物"""
    total_damage = calculate_damage_over_path(placement, monster, position_times)
    return total_damage >= monster.hp

def dp_placement(positions=5, initial_gold=3000):
    towers, monsters, position_times = init_game()
    dp = {}
    
    required_m1, required_m2, required_b1, required_b2 = 2, 2, 1, 1

    def update_requirements(current_placement, m1, m2, b1, b2):
        # 若可以击杀对应怪物，则需求置0
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
        # 更新需求
        m1, m2, b1, b2 = update_requirements(current_placement, m1, m2, b1, b2)
        
        # 如果已经满足全部需求，则cost为0（不需要放更多塔）
        if m1 == 0 and m2 == 0 and b1 == 0 and b2 == 0:
            return 0, current_placement

        if pos == 0:
            # 没有位置可放且仍未满足需求
            return float('inf'), current_placement
            
        state = (pos, m1, m2, b1, b2, gold_left)
        if state in dp:
            return dp[state]
        
        min_cost = float('inf')
        best_placement = current_placement

        # 尝试不放塔
        cost, placement = solve(pos-1, m1, m2, b1, b2, gold_left, current_placement)
        if cost < min_cost:
            min_cost = cost
            best_placement = placement

        # 尝试在此位置放置每种塔
        for tower in towers:
            if tower.cost <= gold_left:
                new_placement = [(pos-1, tower)] + current_placement
                new_m1, new_m2, new_b1, new_b2 = update_requirements(new_placement, m1, m2, b1, b2)
                
                # 继续尝试其他塔，以寻找更便宜的方案
                new_cost, new_pl = solve(pos-1, new_m1, new_m2, new_b1, new_b2, gold_left - tower.cost, new_placement)
                total_cost = tower.cost + new_cost
                if total_cost < min_cost:
                    min_cost = total_cost
                    best_placement = new_pl

        dp[state] = (min_cost, best_placement)
        return dp[state]

    dp_cost, dp_result = solve(positions, required_m1, required_m2, required_b1, required_b2, initial_gold, [])

    # 提取塔的位置和名称
    tower_pos_output = [pos for pos, _ in dp_result]
    tower_name_output = [tower.name for _, tower in dp_result]

    return tower_pos_output, tower_name_output
