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
        Tower(25, 0.5, 300, "ArrowTower", is_magic=False),
        Tower(120, 2.0, 800, "CannonTower", is_magic=False),
        Tower(45, 1.0, 500, "MagicTower", is_magic=True)
    ]
    
    monsters = [
        Monster(120, 5, 60, "快速小兵"),
        Monster(120, 40, 10, "重甲小兵"),
        Monster(250, 30, 30, "精英怪"),
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

def improved_greedy_placement(positions=5, initial_gold=3000):
    """优化后的贪心算法，直接输出位置和塔名称"""
    towers, monsters, position_times = init_game()
    placement = []
    remaining_gold = initial_gold
    
    # 按攻击时间从长到短排序位置
    sorted_positions = sorted(range(positions), key=lambda x: position_times[x], reverse=True)
    
    def calculate_tower_value(current_placement, tower, pos):
        """计算增加这个塔的综合价值"""
        value = 0
        new_placement = [(pos, tower)] + current_placement
        
        # 计算击杀数量的变化
        current_kills = sum(1 for monster in monsters 
                          if can_kill_monster(current_placement, monster, position_times) if current_placement)
        new_kills = sum(1 for monster in monsters 
                       if can_kill_monster(new_placement, monster, position_times))
        
        # 如果能多杀死怪物，给予巨大奖励
        if new_kills > current_kills:
            value += 10000 * (new_kills - current_kills)
        
        # 对每个怪物分析价值
        for i, monster in enumerate(monsters):
            old_damage = calculate_damage_over_path(current_placement, monster, position_times) if current_placement else 0
            new_damage = calculate_damage_over_path(new_placement, monster, position_times)
            damage_increase = new_damage - old_damage
            
            # 计算有效伤害（去除过量部分）
            overflow = max(0, new_damage - monster.hp)
            effective_damage = damage_increase - overflow
            
            # 设置基础权重
            if old_damage < monster.hp:  # 还未能击杀
                weight = 5 if i >= 2 else 3  # BOSS和精英怪权重更高
            else:  # 已经能击杀
                weight = 0.5  # 已经能击杀的怪物价值大幅降低
                
            # 位置价值调整
            position_weight = position_times[pos] / min(position_times.values())  # 相对于最短时间的价值比
            
            # 计算这个怪物带来的价值
            monster_value = effective_damage * weight * position_weight
            
            # 如果即将击杀（伤害达到90%以上），给予额外奖励
            if 0.9 * monster.hp <= new_damage <= 1.1 * monster.hp:
                monster_value *= 1.5
                
            value += monster_value
        
        # 考虑塔的组合效应
        magic_count = sum(1 for _, t in new_placement if t.is_magic)
        physical_count = len(new_placement) - magic_count
        
        # 鼓励搭配使用物理和魔法塔
        if magic_count > 0 and physical_count > 0:
            value *= 1.2
        
        # DPS和位置时间的协同加成
        dps_position_bonus = (tower.dps * position_times[pos]) / 10
        value *= (1 + dps_position_bonus)
        
        # 最终返回性价比
        return value / tower.cost if tower.cost > 0 else 0
    
    # 按位置时间从长到短遍历位置
    for pos in sorted_positions:
        if remaining_gold < 300:  # 最便宜的塔都买不起了
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
    
    # 按位置顺序重新排序，方便显示
    placement.sort(key=lambda x: x[0])
    
    # 提取塔的位置和名称
    tower_pos_output = [pos for pos, _ in placement]
    tower_name_output = [tower.name for _, tower in placement]
    
    return tower_pos_output, tower_name_output
