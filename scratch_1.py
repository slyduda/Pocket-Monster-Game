from typing import Dict, List
from operator import itemgetter
import discord
from discord.ext.commands import Bot
from discord.ext import commands
from PIL import Image
import asyncio
import time
import timeit
import sqlite3 as lite
import random
import math
import sys

# discord connection
Client = discord.Client()
client = commands.Bot(command_prefix="!")

conn = lite.connect('pokemon.db')
cursor = conn.cursor()

player_spawn_dict = {}
player_region_dict = {}
player_channel_dict = {}
player_experience_list = []
encounter_location_list = []
encounter_info_list = []
encounter_pokemon_list = []

pokemon_growth_dict = {}
pokemon_type_dict = {}
pokemon_capture_dict = {}
pokemon_gender_dict = {}
pokemon_gender_dif_dict = {}
pokemon_ev_dict = {}
experience_dict = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
pokemon_name_dict = {}
pokemon_ability_dict = {}
pokemon_base_stat_dict = {}
pokemon_height_dict = {}
pokemon_weight_dict = {}
pokemon_experience_dict = {}
pokemon_friendship_dict = {}
move_name_dict = {}
move_dict = {}
move_meta_dict = {}
move_meta_stat_dict = {}
move_pp_dict = {}
type_efficacy_dict = {}
evolves_from_list = []
evolution_level_dict = {}
item_dict = {}
item_pocket_dict = {}
nature_increased_dict = {}
nature_decreased_dict = {}

emoji_dict = {'grass': "\U0001F343", 'water': "\U0001F4A7", 'fire': "\U0001F525", 'yes': "\U0001F1F4", 'no': "\u2716",
              'fight': "\U0001F4A5", 'switch': "\u2194", "item": "\U0001F6CD", 'run': "\U0001F3C3", 'one': "\u0031\u20E3",
              'two': "\u0032\u20E3", 'three': "\u0033\u20E3", 'four': "\u0034\u20E3", 'five': "\u0035\u20E3",
              'six': "\u0036\u20E3", 'north': "\U0001F1F3", 'south': "\U0001F1F8", 'east': "\U0001F1EA", 'west': "\U0001F1FC",
              'left': "\u25C0", 'right': "\u25B6", 'down': "\u25BC" , 'up': "\u25B2", 'fleft': "\u23EA", 'fright': "\u23E9", 'fdown': "\u23EC", 'fup': "\u23EB"}

current_pokemon_id = 1
version_id = 15  # hard coded
height_percent = 60
weight_percent = 60
local_language = 9

store_dict = {}
global_pockets = ['poke balls', 'medicine']
global_bag_tabs = [['poke_ball', 'great_ball', 'ultra_ball', 'master_ball', 'safari_ball'],['potion', 'super_potion', 'hyper_potion', 'max_potion']]
global_store_tabs = []

def seed(species_id, level):
    seed = []
    base_stats = [0, 0, 0, 0, 0, 0]
    ev_stats = [0, 0, 0, 0, 0, 0]
    iv_stats = [0, 0, 0, 0, 0, 0]
    stats = [0, 0, 0, 0, 0, 0]
    effort_list = [0, 0, 0, 0, 0, 0]

    # ~~~~~~~~~~~~~~~||IDENTIFICATION||~~~~~~~~~~~~~~

    current_pokemon = 0
    id_list = [current_pokemon, species_id, level]
    seed.append(current_pokemon)
    seed.append(species_id)
    seed.append(level)

    # ~~~~~~~~~~~~~~~~~~||GROWTH||~~~~~~~~~~~~~~~~~~
    # dynamic

    growth_rate_id = pokemon_growth_dict[species_id]
    experience_temp = experience_dict[growth_rate_id]
    experience = experience_temp[level - 1]
    experience_to_next = experience_temp[level]
    friendship = pokemon_friendship_dict[species_id]

    growth_list = [experience, growth_rate_id, friendship]
    seed.append(experience)
    seed.append(experience_to_next)
    seed.append(growth_rate_id)
    seed.append(friendship)

    # ~~~~~~~~~~~~~~~~~||BASE STATS||~~~~~~~~~~~~~~~~~
    # static

    query = ('SELECT base_stat FROM pokemon_stats WHERE pokemon_id = %s' % species_id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    counter = 0
    for row in temp_tuple:
        base_stats[counter] = row[0]
        seed.append(row[0])
        counter = counter + 1

    # ~~~~~~~~~~~~~~~~~~||NATURE||~~~~~~~~~~~~~~~~~~~
    # static

    nature = random.randint(1, 25)
    seed.append(nature)
    nature_bonus_list = [1, 1, 1, 1, 1, 1]

    stat_increased = nature_increased_dict[nature]
    stat_decreased = nature_decreased_dict[nature]

    if stat_increased != stat_decreased:
        nature_bonus_list[stat_increased - 1] = 1.1
        nature_bonus_list[stat_decreased - 1] = .9

    n = 0
    for x in nature_bonus_list:
        seed.append(nature_bonus_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~||IV STATS||~~~~~~~~~~~~~~~~~~
    # static

    hp_iv = random.randint(0, 31)
    atk_iv = random.randint(0, 31)
    def_iv = random.randint(0, 31)
    spd_iv = random.randint(0, 31)
    spatk_iv = random.randint(0, 31)
    spdef_iv = random.randint(0, 31)

    iv_stats = [hp_iv, atk_iv, def_iv, spd_iv, spatk_iv, spdef_iv]

    n = 0
    for x in iv_stats:
        seed.append(iv_stats[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~||EV STATS||~~~~~~~~~~~~~~~~~
    # dynamic

    n = 0
    for x in ev_stats:
        seed.append(ev_stats[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~||CUM STATS||~~~~~~~~~~~~~~~~~

    counter = 0
    for x in stats:
        if counter == 0:
            stats[counter] = int(
                (2 * base_stats[counter] + iv_stats[counter] + int(ev_stats[counter] / 4)) * level / 100) + level + 10
            temp = stats[counter]
            counter = counter + 1
        else:
            stats[counter] = int(
                (int((2 * base_stats[counter] + iv_stats[counter] + int(ev_stats[counter] / 4)) * level / 100) + 5) *
                nature_bonus_list[counter])
            temp = stats[counter]
            counter = counter + 1

    n = 0
    for x in stats:
        seed.append(stats[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~||ITEMS AND STATUS||~~~~~~~~~~~~~~~~~

    current_hp = stats[0]

    # PLACHEOLDER
    ailment = 0

    # PLACHEOLDER
    held_item = 0

    status_list = [current_hp, ailment, held_item]

    n = 0
    for x in status_list:
        seed.append(status_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~~||ABILITY||~~~~~~~~~~~~~~~~~~~
    # static

    ability_ratio = random.randint(1, 2)
    ability = 0
    query = ('SELECT slot,ability_id FROM pokemon_abilities WHERE pokemon_id = %s' % species_id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    if len(temp_tuple) == 2:
        ability_ratio = 1

    for row in temp_tuple:
        if row[0] == ability_ratio:
            ability = row[1]

    seed.append(ability)

    # ~~~~~~~~~~~~~~~~~~~||TYPE||~~~~~~~~~~~~~~~~~~

    query = ('SELECT slot, type_id FROM pokemon_types WHERE pokemon_id = %s' % species_id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    type1 = 0
    type2 = 0

    counter = 0
    for row in temp_tuple:
        if counter == 0:
            type1 = row[1]
        if counter == 1:
            type2 = row[1]
        counter = counter + 1

    type_list = [type1, type2]

    n = 0
    for x in type_list:
        seed.append(type_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~||MOVES||~~~~~~~~~~~~~~~~~~
    # dynamic

    query = ('SELECT level, move_id FROM pokemon_moves WHERE pokemon_method_id = 1 AND version_id = %s AND pokemon_id = %s' % (version_id, species_id))
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    move1 = 0
    move2 = 0
    move3 = 0
    move4 = 0
    move1_pp = 0
    move2_pp = 0
    move3_pp = 0
    move4_pp = 0

    for row in temp_tuple:
        if row[0] <= level:
            move4 = move3
            move3 = move2
            move2 = move1
            move1 = row[1]

    try:
        move1_pp = move_pp_dict[move1]
    except:
        move1_pp = 0
    try:
        move2_pp = move_pp_dict[move2]
    except:
        move2_pp = 0
    try:
        move3_pp = move_pp_dict[move3]
    except:
        move3_pp = 0
    try:
        move4_pp = move_pp_dict[move4]
    except:
        move4_pp = 0

    move_list = [move1, move2, move3, move4]
    pp_list = [move1_pp, move2_pp, move3_pp, move4_pp]
    pp_up_list = [0, 0, 0, 0]

    n = 0
    for x in move_list:
        seed.append(move_list[n])
        n = n + 1

    n = 0
    for x in pp_list:
        seed.append(pp_list[n])
        n = n + 1

    n = 0
    for x in pp_up_list:
        seed.append(pp_up_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~~||GENDER||~~~~~~~~~~~~~~~~~~~~
    # static

    gender_rate = pokemon_gender_dict[species_id]
    is_genderless = 0
    if gender_rate == -1:
        is_genderless = 1
    else:
        is_genderless = 0

    is_female = 0
    if gender_rate == -1 or gender_rate == 0:
        is_female = 0
    elif gender_rate == 8:
        is_female = 1
    else:
        male_weight = 8 - gender_rate
        female_weight = 8 - male_weight
        ratios = [(0, male_weight), (1, female_weight)]
        gender = [val for val, cnt in ratios for i in range(cnt)]
        is_female = random.choice(gender)

    gender_dif = pokemon_gender_dif_dict[species_id]

    # ~~~~~~~~~~~~~~~~~~||SHINY & EGG||~~~~~~~~~~~~~~~~~~
    # static

    p_shiny = 1
    p_non_shiny = 8192
    ratios = [(0, p_non_shiny), (1, p_shiny)]
    shiny = [val for val, cnt in ratios for i in range(cnt)]
    is_shiny = random.choice(shiny)
    is_egg = 0

    gene_list = [is_genderless, is_female, gender_dif, is_shiny, is_egg]

    n = 0
    for x in gene_list:
        seed.append(gene_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~||MISC||~~~~~~~~~~~~~~~~~~~
    # static
    # placeholder
    markings = 0

    # placeholder
    unknown = 0

    species_height = pokemon_height_dict[species_id]
    height_bonus = round(calc_size(1), 4)
    height = round(species_height * height_bonus, 2)
    height_list = [markings, unknown, species_height, height_bonus, height]

    n = 0
    for x in height_list:
        seed.append(height_list[n])
        n = n + 1

    species_weight = pokemon_weight_dict[species_id]
    weight_bonus = round(calc_size(0), 4)
    weight = round(species_weight * math.sqrt(height_bonus) * weight_bonus, 2)
    weight_list = [species_weight, weight_bonus, weight]

    n = 0
    for x in weight_list:
        seed.append(weight_list[n])
        n = n + 1

    # ~~~~~~~~~~~~~~~~~||BATTLE INFO||~~~~~~~~~~~~~~~~~

    query = ('SELECT stat_id, effort FROM pokemon_stats WHERE pokemon_id = %s' % (species_id))
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    counter = 0
    for row in temp_tuple:
        effort_list[counter] = row[1]
        counter = counter + 1

    capture_rate = pokemon_capture_dict[species_id]

    n = 0
    for x in effort_list:
        seed.append(effort_list[n])
        n = n + 1

    seed.append(capture_rate)
    seed.append(ability_ratio)
    return (seed)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@client.event
async def on_ready():
    global version_id, current_pokemon_id, local_language

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    print("Hello world!")
    print("My name is:", client.user.name)
    print("My ID is:", client.user.id)

# PLAYER~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PLAYER_CHANNEL_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#changes

    query = 'SELECT * FROM player_discord'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        player_channel_dict[str(row[0])] = str(row[3])

#PLAYER_SPAWN_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#changes

    query = 'SELECT * FROM player_game'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        player_spawn_dict[str(row[0])] = 0

#PLAYER_EXPERIENCE_LIST~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT experience FROM player_experience'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        player_experience_list.append(row[0])

# ENCOUNTERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ENCOUNTER_LISTS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT location_id,location_x,location_y,location_z,location_difficulty,minimum_battles,minimum_trainer_level,pokecenter, store FROM encounter_locations'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 0
    for row in temp_list:
        encounter_location_list.append([row[1],row[2],row[3]])
        encounter_info_list.append([row[4],row[5],row[6],row[7],row[8]])
        counter = counter + 1

# ENCOUNTER_LISTS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT location_id,pokemon_id,encounter_chance,min_level,max_level FROM encounter_pokemon'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 1
    temp_ = []
    for row in temp_list:
        if int(row[0]) == counter:
            temp_.append([row[1],row[2],row[3],row[4]])
        else:
            encounter_pokemon_list.append(list(temp_))
            temp_.clear()
            temp_.append([row[1],row[2],row[3],row[4]])
            counter = counter + 1

    encounter_pokemon_list.append(list(temp_))

    # POKEMON~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # POKEMON_ABILITY_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM pokemon_abilities WHERE is_hidden = 0'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 1
    temp_ = []
    for row in temp_list:
        if row[0] != counter:
            temp_.append(row[1])
            pokemon_ability_dict[row[0]] = list(temp_)
        else:
            temp_.clear()
            temp_.append(row[1])
            pokemon_ability_dict[row[0]] = list(temp_)
            counter = counter + 1

    # POKEMON_TYPE_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT pokemon_id, type_id FROM pokemon_types'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 1
    temp_ = []
    new_entry = 0
    for row in temp_list:
        if row[0] != counter:
            new_entry = row[0]
            temp_.append(row[1])
            pokemon_type_dict[new_entry] = list(temp_)
        else:
            if len(temp_) == 1:
                temp_.append(0)
                pokemon_type_dict[new_entry] = list(temp_)
            new_entry = row[0]
            temp_.clear()
            temp_.append(row[1])
            pokemon_type_dict[row[0]] = list(temp_)
            counter = counter + 1

    # POKEMON_EV_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT pokemon_id, effort FROM pokemon_stats'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 1
    temp_ = []
    for row in temp_list:
        if row[0] != counter:
            temp_.append(row[1])
            pokemon_ev_dict[row[0]] = list(temp_)
        else:
            temp_.clear()
            temp_.append(row[1])
            pokemon_ev_dict[row[0]] = list(temp_)
            counter = counter + 1

    # POKEMON_BASE_STAT_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT pokemon_id, base_stat FROM pokemon_stats'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    counter = 1
    temp_ = []
    for row in temp_list:
        if row[0] != counter:
            temp_.append(row[1])
            pokemon_base_stat_dict[row[0]] = list(temp_)
        else:
            temp_.clear()
            temp_.append(row[1])
            pokemon_base_stat_dict[row[0]]= list(temp_)
            counter = counter + 1

# POKEMON_NAME_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = ('SELECT id,name FROM pokemon_species_names WHERE local_language = %s' % local_language)
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        pokemon_name_dict[int(row[0])] = str(row[1])

# POKEMON_FRIENDSHIP_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id, base_happiness FROM pokemon_species'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        pokemon_friendship_dict[int(row[0])] = int(row[1])

# POKEMON_HEIGHT,POKEMON_WEIGHT,POKEMON_EXP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id,height,weight,base_experience FROM pokemon'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        pokemon_height_dict[int(row[0])] = int(row[1])
        pokemon_weight_dict[int(row[0])] = int(row[2])
        pokemon_experience_dict[int(row[0])] = int(row[3])


# POKEMON_SPECIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id,gender_rate,capture_rate,growth_rate_id,has_gender_differences FROM pokemon_species'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        pokemon_gender_dict[row[0]] = row[1]
        pokemon_capture_dict[row[0]] = row[2]
        pokemon_growth_dict[row[0]] = row[3]
        pokemon_gender_dif_dict[row[0]] = row[4]

# MOVES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MOVE_NAME_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = ('SELECT move_id,name FROM move_names WHERE local_language = %s' % local_language)
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        move_name_dict[int(row[0])] = str(row[1])

# MOVE_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM moves'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        move_dict[row[0]] = [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]]

# MOVE_META_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM move_meta'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        move_meta_dict[row[0]] = [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]]

# MOVE_PP_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id,pp FROM moves'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        move_pp_dict[row[0]] = row[1]

    # MOVE_META_STAT_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM move_meta_stat_changes'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()
    #hp,atk,def,spd,spatk,spdef,acc,eva
    temp_ = [0,0,0,0,0,0,0,0]
    temp_tracker = 0

    for row in temp_tuple:
        if row[0] == temp_tracker:
            move_meta_stat_dict[row[0]][row[1] - 1] = row[2]
        else:
            move_meta_stat_dict[row[0]] = list(temp_)
            move_meta_stat_dict[row[0]][row[1] - 1] = row[2]
            temp_tracker = row[0]

# TYPE_EFFICACY_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM type_efficacy'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    temp_ = []
    for row in temp_tuple:
        if row[1] == 18:
            temp_.append(row[2])
            type_efficacy_dict[row[0]] = list(temp_)
            temp_.clear()
        else:
            temp_.append(row[2])

    # EVOLUTION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EVOLUTION_LEVEL_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = (
        'SELECT evolution_species_id,minimum_level,gender_id,location_id,held_item_id,time_of_day,known_move_id,known_move_type_id,minimum_happiness,minimum_beauty,minimum_affection FROM pokemon_evolution WHERE evolution_trigger_id = 1')
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        evolution_level_dict[row[0]] = [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]]

# EVOLUTION_ITEM_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# EVOLVES_FROM_LIST~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id,evolves_from_species_id FROM pokemon_species'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        evolves_from_list.append([row[0], row[1]])

# ITEMS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ITEM_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT identifier, category_id, pocket_id, cost, fling_power, fling_effect_id FROM items'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        item_dict[row[0]] = [row[1],row[2],row[3],row[4],row[5]]

# ITEM_POCKET_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id, identifier FROM item_pockets'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        item_pocket_dict[row[0]] = row[1]

# MISC~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NATURE_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT id,decreased_stat_id,increased_stat_id FROM natures'
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        nature_decreased_dict[row[0]] = row[1]
        nature_increased_dict[row[0]] = row[2]

# EXPERIENCE_DICT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT * FROM experience'
    cursor.execute(query)
    experience_tuple = cursor.fetchall()
    temp_growth_id = 1
    temp_exp_list = []
    for row in experience_tuple:
        if row[1] == 100:
            temp_exp_list.append(row[2])
            experience_dict[temp_growth_id] = list(temp_exp_list)
            temp_exp_list.clear()
            temp_growth_id = temp_growth_id + 1
        else:
            temp_exp_list.append(row[2])

#CURRENT_POKEMON_ID~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT pokemon_id FROM player_pokemon'
    cursor.execute(query)
    pokemon_id_tuple = cursor.fetchall()

    current_pokemon_id = 1
    pokemon_id_list = []
    if not pokemon_id_tuple:
        current_pokemon_id = 1
        print("Current Pokemon ID is", current_pokemon_id)
    else:
        for row in pokemon_id_tuple:
            pokemon_id_list.append(row[0])

    if not pokemon_id_list:
        current_pokemon_id = 1
    else:
        current_pokemon_id = pokemon_id_list[-1] + 1

# STORE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = 'SELECT identifier, amount FROM store'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        store_dict[str(row[0])] = row[1]


@client.event
async def on_message(message):

#COMMANDS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#$INFO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$INFO'):
        main_player = message.author
        try:
            await client.delete_message(message)
        except:
            pass
        bot_message = await client.send_message(message.author, "Listed below are available commands and descriptions of features in this bot.\n"
                                                                "**1: $SETUP** - Admin Only - Initializes player setup.\n"
                                                                "**2: $STARTER** - All Players - Choose your starter Pokemon to begin your journey.\n"
                                                                "**3: $HEAL** - All Players - Heal up your current party.\n"
                                                                "**4: $TRAVEL** - All Players - Travel to a different location in your region.\n"
                                                                "**5: $SWITCH** - All Players - Switch any Pokemon in your current party.\n"
                                                                "**6: $PARTY** - All Players - (Coming Soon)\n"
                                                                "**7: $BUY** - All Players - Purchase in game items that will help you on your journey.\n"
                                                                "Click any number to learn more about the corresponding command.")
        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
        await client.delete_message(bot_message)

#$SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$SETUP') and message.author.id == str(341429638775701515):
        main_user = message.author
        setup_channel = message.channel
        await client.send_message(message.channel, 'Please type "$PLAYER" to participate.')

        def check(msg):
            return msg.content.upper().startswith('$PLAYER')

        message = await client.wait_for_message(channel=setup_channel, check=check)
        temp_message = message
        userDuplicate = True

        query = ("""SELECT * FROM player_discord WHERE player_id = '%s' """ % (temp_message.author.id))
        cursor.execute(query)
        temp_list = list(cursor.fetchall())

        if not temp_list:
            userDuplicate = False

        if userDuplicate == False:
            print("A new user would like to begin their journey")
            await client.send_message(message.channel, '%s, please confirm %s membership by typing "ADD"' % (
            str(main_user), str(temp_message.author)))
            message = await client.wait_for_message(author=main_user, channel=setup_channel)

            if message.content.upper().startswith("ADD"):

                temp = [str(temp_message.author.id), str(temp_message.author), str(temp_message.server.id),
                        str(temp_message.channel.id), 0]
                cursor.execute(
                    'INSERT INTO player_discord (player_id, player_name, server_id, channel_id, is_tutorial) VALUES (?,?,?,?,?)',
                    temp)
                conn.commit()
                await client.send_message(message.channel,
                                          '%s has been added to the list of players.' % str(temp_message.author))
                bot_message = await client.send_message(temp_message.author,
                                                        """**Thank you for taking your time to participate in the alpha stages of this bot! This version of a Pokemon bot includes many of the mechanics that you would find in the core games. Currently, this bot supported generating Pokemon with IV's, EV's, Natures, Abilities, etc. Spawning and a battle system are under development at this time. Public events, P2P battles along with trading will be implemented after those features are complete.\nThis bot must store the user's ID, server, and channel in order to function properly. If at any point you would like to erase your information, please message a moderator (this will permanently delete all of your game progress).**\nIn order to get starter with your journey, please message the professor with the "$STARTER" in the server you had set up your account.""")
                return
            else:
                await client.send_message(message.channel, 'Incorrect response. Please try again!')
                return
        elif userDuplicate == True:
            await client.send_message(message.channel, """Your username has already been stored""")
            return

#$STARTER~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$STARTER'):
        query = ('SELECT is_tutorial FROM player_discord WHERE player_id = %s' % message.author.id)
        cursor.execute(query)
        newresults = cursor.fetchall()

        if not newresults:
            await client.send_message(message.channel,
                                      """You have not set up your account! To set up your account please ask an administrator.""")

        else:
            for row in newresults:
                is_tutorial = row[0]

            if is_tutorial == 0:
                main_player = message.author
                bot_message = await client.send_message(main_player,
                                                        "Hello %s, my name is Professor Maple. Click on a reaction to choose your starter type pokemon or click X to try again later. Choose wisely as you will only be able to choose your starter pokemon once.\n**Grass = Bulbasaur **|-|** Water = Squirtle **|-|** Fire = Charmander **|-|** X = Quit Tutorial**" % main_player)
                bot_reaction_grass = await client.add_reaction(bot_message, emoji=emoji_dict['grass'])
                bot_reaction_fire = await client.add_reaction(bot_message, emoji=emoji_dict['fire'])
                bot_reaction_water = await client.add_reaction(bot_message, emoji=emoji_dict['water'])
                bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                player_choice = 0
                starter_level = 5
                if player_response.reaction.emoji == emoji_dict['grass']:
                    player_choice = 1
                elif player_response.reaction.emoji == emoji_dict['fire']:
                    player_choice = 4
                elif player_response.reaction.emoji == emoji_dict['water']:
                    player_choice = 7
                elif player_response.reaction.emoji == emoji_dict['no']:
                    player_choice = 0
                    await client.delete_message(bot_message)
                    bot_message = await client.send_message(main_player,
                                                            "Selection canceled. Enter $STARTER to try again.")
                    return
                else:
                    player_choice = 0
                    await client.delete_message(bot_message)
                    await client.send_message(message.author,
                                              "Invalid response. Selection canceled. Enter $STARTER to try again.")
                    return

                player_pokemon_name = pokemon_name_dict[player_choice].capitalize()
                current_pokemon = seed(player_choice, starter_level)
                current_pokemon = catch(current_pokemon, 4, str(message.author), message.author.id)
                player_region = 1
                setup(message.author.id, player_region, current_pokemon)

                await client.delete_message(bot_message)
                await client.send_file(main_player,
                                       'C:/Users/Sylvester/Documents/PokemonSprites/%s.png' % player_choice)
                bot_message = await client.send_message(main_player,
                                                        "Congratulations! You have selected %s as your starter Pokemon! Would you like to post your choice on the your Pokebot channel?\n\n**Circle: Yes **|-|** X: No**" % player_pokemon_name)
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])

                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                if player_response.reaction.emoji == emoji_dict['yes']:
                    await client.send_file(message.channel,
                                           'C:/Users/Sylvester/Documents/PokemonSprites/%s.png' % player_choice)
                    await client.send_message(message.channel, """%s has chosen %s as their starter Pokemon!""" % (
                    main_player, player_pokemon_name))
                    bot_message = await client.send_message(main_player,
                                                            "Message sent! Updates on battles and leveling coming soon!\n\n**Circle: Complete Tutorial**")
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])

                    if player_response.reaction.emoji == emoji_dict['yes']:
                        await client.delete_message(bot_message)

                elif player_response.reaction.emoji == emoji_dict['no']:
                    bot_message = await client.send_message(main_player,
                                                            "Updates on battles and leveling coming soon!\n\n**Circle: Complete Tutorial**")
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])

                    if player_response.reaction.emoji == emoji_dict['yes']:
                        await client.delete_message(bot_message)
            else:
                await client.send_message(message.channel, """You have already completed the tutorial!""")
                return

#$BUY~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$BUY'):
        main_player = message.author
        try:
            await client.delete_message(message)
        except:
            pass
        if player_spawn_dict[main_player.id] == 0:

            player_spawn_dict[main_player.id] = 1


            query = (
                        'SELECT player_location,player_money FROM player_game WHERE player_id = %s' % main_player.id)
            cursor.execute(query)
            temp_list = list(cursor.fetchall())
            temp_ = []

            for row in temp_list:
                temp_ = [row[0]]

            user_location = encounter_info_list[temp_[0]-1][4]

            if user_location == 1:
                isselect = True
                while bool(isselect):
                    query = 'SELECT identifier,amount FROM store WHERE on_sale = 1'
                    cursor.execute(query)
                    temp_list = list(cursor.fetchall())
                    display_list = []
                    in_stock = []

                    for row in temp_list:
                        display_list.append(row[0])
                        in_stock.append(row[1])

                    bot_message = await client.send_message(main_player,
                                                            "What would you like to buy?\n\n"
                                                            "1) **%s** @ $%s - *(%s in stock)*\n"
                                                            "2) **%s** @ $%s - *(%s in stock)*\n"
                                                            "3) **%s** @ $%s - *(%s in stock)*\n"
                                                            "4) **%s** @ $%s - *(%s in stock)*\n"
                                                            "5) **%s** @ $%s - *(%s in stock)*" %
                                                            (display_list[0], int(item_dict[display_list[0]][2] / 10),in_stock[0],
                                                            display_list[1] , int(item_dict[display_list[1]][2] / 10),in_stock[1],
                                                            display_list[2] , int(item_dict[display_list[2]][2] / 10),in_stock[2],
                                                            display_list[3] , int(item_dict[display_list[3]][2] / 10),in_stock[3],
                                                            display_list[4] , int(item_dict[display_list[4]][2] / 10),in_stock[4]))

                    temp_list = ['one', 'two', 'three', 'four', 'five', 'six']
                    n = 0
                    for i in display_list:
                        if in_stock[n] > 0:
                            bot_reaction = await client.add_reaction(bot_message,
                                                                     emoji=emoji_dict[temp_list[n]])
                        n = n + 1

                    bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                    await client.delete_message(bot_message)

                    in_cart = 0
                    position = 0
                    if player_response.reaction.emoji == emoji_dict['one'] and store_dict[display_list[0]] > 0:
                        position = 0
                    elif player_response.reaction.emoji == emoji_dict['two'] and store_dict[display_list[1]] > 0:
                        position = 1
                    elif player_response.reaction.emoji == emoji_dict['three'] and store_dict[display_list[2]] > 0:
                        position = 2
                    elif player_response.reaction.emoji == emoji_dict['four'] and store_dict[display_list[3]] > 0:
                        position = 3
                    elif player_response.reaction.emoji == emoji_dict['five'] and store_dict[display_list[4]] > 0:
                        position = 4
                    elif player_response.reaction.emoji == emoji_dict['six'] and store_dict[display_list[5]] > 0:
                        position = 5
                    else:
                        player_spawn_dict[main_player.id] = 0
                        isselect = False
                        break

                    query = ('SELECT player_money FROM player_game WHERE player_id = %s' % main_player.id)
                    cursor.execute(query)
                    temp_list = list(cursor.fetchall())
                    temp_ = 0

                    for row in temp_list:
                        temp_ = row[0]

                    player_cash = temp_
                    in_cart = 0
                    in_cart_total = 0

                    bot_message = await client.send_message(main_player,
                                                            "How many %s's would you like to buy?\n"
                                                            "(Click Emoji to Add and Circle to Accept)\n\n"
                                                            "Cash on Hand: **$%s**\n"
                                                            "Amount in Cart: %s\n"
                                                            "Total Price: **$%s**" %(display_list[position], player_cash,in_cart, in_cart_total))
                    bot_reaction_one = await client.add_reaction(bot_message, emoji=emoji_dict['one'])
                    bot_reaction_five = await client.add_reaction(bot_message, emoji=emoji_dict['five'])
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])

                    iscart = True
                    while bool(iscart):
                        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                        if player_response.reaction.emoji == emoji_dict['one']:
                            in_cart = in_cart + 1
                        elif player_response.reaction.emoji == emoji_dict['five']:
                            in_cart = in_cart + 5
                        elif player_response.reaction.emoji == emoji_dict['yes']:
                            query = ('SELECT player_money FROM player_game WHERE player_id = %s' % main_player.id)
                            cursor.execute(query)
                            temp_list = list(cursor.fetchall())
                            temp_ = 0

                            for row in temp_list:
                                temp_ = row[0]

                            player_cash = temp_

                            if player_cash >= in_cart_total:

                                query = 'SELECT identifier,amount FROM store WHERE on_sale = 1'
                                cursor.execute(query)
                                temp_list = list(cursor.fetchall())
                                display_list = []
                                in_stock = []



                                for row in temp_list:
                                    display_list.append(row[0])
                                    in_stock.append(row[1])

                                print(in_stock)

                                if in_cart > in_stock[position]:
                                    bot_message_new = await client.send_message(main_player,
                                                                                "Oops! Looks like you missed the last few. Try entering a smaller amount.")
                                    bot_reaction_yes = await client.add_reaction(bot_message_new, emoji=emoji_dict['yes'])
                                    player_response = await client.wait_for_reaction(message=bot_message_new,
                                                                                     user=main_player)
                                    await client.delete_message(bot_message_new)
                                    break

                                query = ('UPDATE player_game SET player_money = player_money - %s WHERE player_id = %s' % (
                                in_cart_total, main_player.id))
                                cursor.execute(query)

                                query = ('SELECT player_money FROM player_game WHERE player_id = %s' % main_player.id)
                                cursor.execute(query)
                                temp_list = list(cursor.fetchall())
                                temp_ = 0

                                for row in temp_list:
                                    temp_ = row[0]

                                player_cash = temp_

                                if player_cash < 0:
                                    query = ('UPDATE player_game SET player_money = player_money + %s WHERE player_id = %s' % (
                                            in_cart_total, main_player.id))
                                    cursor.execute(query)
                                    bot_message_new = await client.send_message(main_player,
                                        "Oops! Looks like you almost got away with buying something with money you didn't have. Your money has been returned.")
                                    bot_reaction_yes = await client.add_reaction(bot_message_new, emoji=emoji_dict['yes'])
                                    player_response = await client.wait_for_reaction(message=bot_message_new,
                                                                                     user=main_player)
                                    await client.delete_message(bot_message_new)
                                    conn.commit()
                                    break

                                query = ("""UPDATE store SET cash = cash + %s, amount = amount - %s WHERE identifier = '%s' """ % (
                                    in_cart_total, in_cart, display_list[position]))
                                cursor.execute(query)

                                print(item_dict[display_list[position]][1])

                                print(main_player.id)
                                if item_dict[display_list[position]][1] == 1:
                                    query = ('UPDATE player_item_balls SET %s = %s + %s WHERE player_id = %s' % (display_list[position], display_list[position], in_cart, main_player.id))
                                if item_dict[display_list[position]][1] == 2:
                                    query = ('UPDATE player_item_medicine SET %s = %s + %s WHERE player_id = %s' % (display_list[position], display_list[position], in_cart, main_player.id))

                                try:
                                    cursor.execute(query)
                                except:
                                    print(main_player, in_cart, display_list[position], "ERROR SAVING ITEMS BOUGHT")

                                await client.delete_message(bot_message)
                                conn.commit()
                                break
                            else:
                                bot_message_new = await client.send_message(main_player,
                                                                        "You do not have enough cash!")
                                bot_reaction_yes = await client.add_reaction(bot_message_new, emoji=emoji_dict['yes'])
                                player_response = await client.wait_for_reaction(message=bot_message_new, user=main_player)
                                await client.delete_message(bot_message_new)
                        else:
                            await client.delete_message(bot_message)
                            iscart = False
                            break

                        in_cart_total = int(item_dict[display_list[position]][2] / 10) * in_cart
                        bot_message = await client.edit_message(bot_message,
                                                                "How many %s's would you like to buy?\n"
                                                                "(Click Emoji to Add and Circle to Accept)\n\n"
                                                                "Cash on Hand: **$%s**\n"
                                                                "Amount in Cart: %s\n"
                                                                "Total Price: **$%s**" % (display_list[position], player_cash, in_cart,
                                                                               in_cart_total))

            else:
                bot_message = await client.send_message(main_player, "Not a store in sight.")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                player_spawn_dict[main_player.id] = 0
                await client.delete_message(bot_message)

        else:
            bot_message = await client.send_message(main_player, "You have to complete your active spawn before doing an action.")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)

#$HEAL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$HEAL'):
        main_player = message.author
        try:
            await client.delete_message(message)
        except:
            pass
        if player_spawn_dict[message.author.id] == 0:
            player_spawn_dict[main_player.id] = 1

            query = (
                        'SELECT player_location FROM player_game WHERE player_id = %s' % main_player.id)
            cursor.execute(query)
            temp_list = list(cursor.fetchall())
            temp_ = []

            for row in temp_list:
                temp_ = [row[0]]

            user_location = temp_[0]

            if encounter_info_list[user_location-1][3] == 1:
                bot_message = await client.send_message(main_player,
                                                        "Updating...\nThis may take a while.")
                in_party = get_pokemon(main_player.id)
                counter = 0
                print(in_party)
                for i in in_party:
                    current_pokemon = in_party[counter]
                    if current_pokemon != 0:
                        query = ('SELECT * FROM player_pokemon WHERE pokemon_id = %s' % current_pokemon)
                        cursor.execute(query)
                        temp_tuple = cursor.fetchall()

                        for row in temp_tuple:
                            temp_dict = {'pokemon_id': row[0],'hp_battle': row[32], 'hp_current': row[38], 'ailment': row[39]}
                            current_pokemon = dict(temp_dict)
                            current_pokemon['hp_current'] = current_pokemon['hp_battle']
                            current_pokemon['ailment'] = 0
                            cursor.execute('UPDATE player_pokemon SET hp_current = %s, ailment = %s WHERE pokemon_id = %s' % (current_pokemon['hp_current'],current_pokemon['ailment'],current_pokemon['pokemon_id']))
                            time.sleep(1)
                            conn.commit()

                    counter += 1


                await client.delete_message(bot_message)
                bot_message = await client.send_message(main_player,
                                                        "Your party's health and status has been restored.\n\nCircle: Continue")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
                player_spawn_dict[main_player.id] = 0

            else:
                bot_message = await client.send_message(main_player,
                                                        "There is no Pokecenter in this area.\n\nCircle: Continue")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
                player_spawn_dict[main_player.id] = 0
        else:
            bot_message = await client.send_message(main_player, "You have to complete your active action before doing an action.")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)

#$SWITCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if message.content.upper().startswith('$OVER'):
        new_role = discord.utils.get(message.server.roles, name="over-watchers")
        if new_role.id in [role.id for role in message.author.roles]:
            await client.remove_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are no longer an over-watcher.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)
        else:
            await client.add_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are an over-watcher.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)

    if message.content.upper().startswith('$POKE'):
        new_role = discord.utils.get(message.server.roles, name="poke-botters")
        if new_role.id in [role.id for role in message.author.roles]:
            await client.remove_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are no longer a poke-botter.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)
        else:
            await client.add_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are a poke-botter.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)

    if message.content.upper().startswith('$FORT'):
        new_role = discord.utils.get(message.server.roles, name="fort-niters")
        if new_role.id in [role.id for role in message.author.roles]:
            await client.remove_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are no longer a fort-niter.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)
        else:
            await client.add_roles(message.author, new_role)
            await client.delete_message(message)
            bot_message = await client.send_message(message.author,
                                                    "You are a fort-niter.\n\nCircle: Continue")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=message.author)
            await client.delete_message(bot_message)

    if message.content.upper().startswith('$SWITCH'):
        main_player = message.author
        try:
            await client.delete_message(message)
        except:
            pass
        if player_spawn_dict[message.author.id] == 0:
            player_spawn_dict[main_player.id] = 1

            query = (
                        'SELECT player_location FROM player_game WHERE player_id = %s' % main_player.id)
            cursor.execute(query)
            temp_list = list(cursor.fetchall())
            temp_ = []

            for row in temp_list:
                temp_ = [row[0]]

            user_location = temp_[0]

            if encounter_info_list[user_location-1][3] == 1:
                in_party = get_pokemon(main_player.id)
                isconfirm = False
                counter = 0
                print(in_party)
                for i in in_party:
                    current_pokemon = in_party[counter]
                    if current_pokemon != 0:
                        query = ('SELECT pokemon_id, species_id FROM player_pokemon WHERE pokemon_id = %s' % current_pokemon)
                        cursor.execute(query)
                        temp_tuple = cursor.fetchall()

                        for row in temp_tuple:
                            temp_dict = {'pokemon_id':row[0],'species_id': row[1]}
                            in_party[counter] = dict(temp_dict)
                    else:
                        in_party[counter] = {'pokemon_id': 0,'species_id': 0}

                    counter += 1

                bot_message = await client.send_message(main_player,
                                                        "Which Pokemon would you like to move?\n"
                                                         "1: %s ID: %s\n"
                                                         "2: %s ID: %s\n"
                                                         "3: %s ID: %s\n"
                                                         "4: %s ID: %s\n"
                                                         "5: %s ID: %s\n"
                                                         "6: %s ID: %s"  % (pokemon_name_dict[in_party[0]['species_id']],in_party[0]['pokemon_id'],
                                                                            pokemon_name_dict[in_party[1]['species_id']],in_party[1]['pokemon_id'],
                                                                            pokemon_name_dict[in_party[2]['species_id']],in_party[2]['pokemon_id'],
                                                                            pokemon_name_dict[in_party[3]['species_id']],in_party[3]['pokemon_id'],
                                                                            pokemon_name_dict[in_party[4]['species_id']],in_party[4]['pokemon_id'],
                                                                            pokemon_name_dict[in_party[5]['species_id']],in_party[5]['pokemon_id'],))

                emoji_list = ['one', 'two', 'three', 'four', 'five', 'six']

                counter = 0
                for i in in_party:
                    if in_party[counter]['pokemon_id'] != 0:
                        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict[emoji_list[counter]])
                    counter += 1


                bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                player_switch = 0

                if player_response.reaction.emoji == emoji_dict['one'] and in_party[0]['pokemon_id'] != 0:
                    player_switch = 0
                    isconfirm = True
                elif player_response.reaction.emoji == emoji_dict['two'] and in_party[1]['pokemon_id'] != 0:
                    player_switch = 1
                    isconfirm = True
                elif player_response.reaction.emoji == emoji_dict['three'] and in_party[2]['pokemon_id'] != 0:
                    player_switch = 2
                    isconfirm = True
                elif player_response.reaction.emoji == emoji_dict['four'] and in_party[3]['pokemon_id'] != 0:
                    player_switch = 3
                    isconfirm = True
                elif player_response.reaction.emoji == emoji_dict['five'] and in_party[4]['pokemon_id'] != 0:
                    player_switch = 4
                    isconfirm = True
                elif player_response.reaction.emoji == emoji_dict['six'] and in_party[5]['pokemon_id'] != 0:
                    player_switch = 5
                    isconfirm = True
                else:
                    pass

                await client.delete_message(bot_message)

                while bool(isconfirm):
                    bot_message = await client.send_message(main_player,
                                                            "Which Pokemon would you like to switch it with?\n"
                                                            "1: %s ID: %s \n"
                                                            "2: %s ID: %s\n"
                                                            "3: %s ID: %s\n"
                                                            "4: %s ID: %s\n"
                                                            "5: %s ID: %s\n"
                                                            "6: %s ID: %s" % (
                                                            pokemon_name_dict[in_party[0]['species_id']],
                                                            in_party[0]['pokemon_id'],
                                                            pokemon_name_dict[in_party[1]['species_id']],
                                                            in_party[1]['pokemon_id'],
                                                            pokemon_name_dict[in_party[2]['species_id']],
                                                            in_party[2]['pokemon_id'],
                                                            pokemon_name_dict[in_party[3]['species_id']],
                                                            in_party[3]['pokemon_id'],
                                                            pokemon_name_dict[in_party[4]['species_id']],
                                                            in_party[4]['pokemon_id'],
                                                            pokemon_name_dict[in_party[5]['species_id']],
                                                            in_party[5]['pokemon_id'],))

                    emoji_list = ['one', 'two', 'three', 'four', 'five', 'six']

                    counter = 0
                    for i in in_party:
                        if in_party[counter]['pokemon_id'] != 0:
                            bot_reaction_yes = await client.add_reaction(bot_message,
                                                                         emoji=emoji_dict[emoji_list[counter]])
                        counter += 1

                    bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                    switch = 0

                    if player_response.reaction.emoji == emoji_dict['one'] and in_party[0]['pokemon_id'] != 0:
                        switch = 0
                    elif player_response.reaction.emoji == emoji_dict['two'] and in_party[1]['pokemon_id'] != 0:
                        switch = 1
                    elif player_response.reaction.emoji == emoji_dict['three'] and in_party[2]['pokemon_id'] != 0:
                        switch = 2
                    elif player_response.reaction.emoji == emoji_dict['four'] and in_party[3]['pokemon_id'] != 0:
                        switch = 3
                    elif player_response.reaction.emoji == emoji_dict['five'] and in_party[4]['pokemon_id'] != 0:
                        switch = 4
                    elif player_response.reaction.emoji == emoji_dict['six'] and in_party[5]['pokemon_id'] != 0:
                        switch = 5
                    else:
                        await client.delete_message(bot_message)
                        isconfirm = False
                        break

                    counter = 0
                    new_list = [0,0,0,0,0,0]
                    for i in in_party:
                        if counter == player_switch:
                            new_list[counter] = int(in_party[switch]['pokemon_id'])
                        elif counter == switch:
                            new_list[counter] = int(in_party[player_switch]['pokemon_id'])
                        else:
                            new_list[counter] = int(in_party[counter]['pokemon_id'])
                        counter += 1

                    in_party = list(new_list)
                    print(in_party)
                    await client.delete_message(bot_message)
                    cursor.execute('UPDATE player_game SET pokemon1 = %s, pokemon2 = %s, pokemon3 = %s, pokemon4 = %s, pokemon5 = %s, pokemon6 = %s WHERE player_id = %s' % (
                    in_party[0],in_party[1],in_party[2],in_party[3],in_party[4],in_party[5], main_player.id))
                    time.sleep(1)
                    conn.commit()
                    isconfirm = False
                    break


                player_spawn_dict[main_player.id] = 0
                bot_message = await client.send_message(main_player,
                                                        "Pokemon switched!")

            else:
                bot_message = await client.send_message(main_player,
                                                        "There is no Pokecenter in this area.\n\nCircle: Continue")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
                player_spawn_dict[main_player.id] = 0
        else:
            bot_message = await client.send_message(main_player, "You have to complete your active action before doing an action.")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$TRAVEL'):
        main_player = message.author
        try:
            await client.delete_message(message)
        except:
            pass
        if player_spawn_dict[message.author.id] == 0:
            player_spawn_dict[main_player.id] = 1
            query = ('SELECT player_location, player_level, battle_count FROM player_game WHERE player_id = %s' % main_player.id)
            cursor.execute(query)
            temp_list = list(cursor.fetchall())
            temp_ = []

            for row in temp_list:
                temp_ = [row[0],row[1],row[2]]

            user_location = temp_[0]
            user_level = temp_[1]
            user_battle_count = temp_[2]


            istravel = True
            while bool(istravel):
                user_coord = encounter_location_list[user_location - 1]
                bot_message = await client.send_message(main_player, "Which direction would you like to go? X: Stay")
                bot_reaction_west= await client.add_reaction(bot_message, emoji=emoji_dict['west'])
                bot_reaction_north = await client.add_reaction(bot_message, emoji=emoji_dict['north'])
                bot_reaction_south = await client.add_reaction(bot_message, emoji=emoji_dict['south'])
                bot_reaction_east = await client.add_reaction(bot_message, emoji=emoji_dict['east'])
                bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                if player_response.reaction.emoji == emoji_dict['north']:
                    offset = [0, 1, 0]
                    new_location = [x + y for x, y in zip(user_coord, offset)]
                elif player_response.reaction.emoji == emoji_dict['south']:
                    offset = [0, -1, 0]
                    new_location = [x + y for x, y in zip(user_coord, offset)]
                elif player_response.reaction.emoji == emoji_dict['west']:
                    offset = [-1, 0, 0]
                    new_location = [x + y for x, y in zip(user_coord, offset)]
                elif player_response.reaction.emoji == emoji_dict['east']:
                    offset = [1, 0, 0]
                    new_location = [x + y for x, y in zip(user_coord, offset)]
                else:
                    istravel = False
                    await client.delete_message(bot_message)
                    player_spawn_dict[main_player.id] = 0
                    break

                print(new_location)
                if new_location in encounter_location_list:
                    user_pos = encounter_location_list.index(new_location) + 1
                    required_battles = encounter_info_list[user_pos - 1][1]

                    await client.delete_message(bot_message)
                    bot_message = await client.send_message(main_player,
                                                            "Are you sure you would like to move to this area?\n"
                                                            "Difficulty: %s\n"
                                                            "Required Battle Count: %s\n"
                                                            "Recommended Trainer Level: %s\n"
                                                            "Pockecenter(s): %s\n"
                                                            "Shop(s): %s" % (encounter_info_list[user_pos - 1][0],encounter_info_list[user_pos - 1][1],encounter_info_list[user_pos - 1][2],encounter_info_list[user_pos - 1][3],encounter_info_list[user_pos - 1][4]))
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                    await client.delete_message(bot_message)

                    if player_response.reaction.emoji == emoji_dict['yes']:
                        if user_battle_count >= required_battles:
                            cursor.execute('UPDATE player_game SET player_location = %s, battle_count = 0 WHERE player_id = %s' % (user_pos,main_player.id))
                            conn.commit()

                            bot_message = await client.send_message(main_player,
                                                                "New location saved.\n\nCircle: Continue.")
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                            await client.delete_message(bot_message)
                            player_spawn_dict[main_player.id] = 0
                            istravel = False
                        else:
                            battle_dif = required_battles - user_battle_count
                            bot_message = await client.send_message(main_player,
                                                                    "You need %s more battle(s) to enter this location.\n\nCircle: Continue." % battle_dif)
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                            await client.delete_message(bot_message)
                    else:
                        pass
                else:
                    await client.delete_message(bot_message)
                    bot_message = await client.send_message(main_player, "You stumble upon a newly built steel chain link fence that nearly doubles your height. It is too tall to climb over. You turn back empty handed and disappointed.\n\nCircle: Continue.")
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                    await client.delete_message(bot_message)
        else:
            bot_message = await client.send_message(main_player, "You have to complete your active action before doing an action.")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)

#$MEMBERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$MEMBERS') and message.author.id == str(341429638775701515):
        x = message.server.members
        await client.delete_message(message)
        print(x)

#$DEBUG~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$DEBUG') and message.author.id == str(341429638775701515):
        await client.send_message(message.channel, 'Debug info sent to shell.')
        print(message.server.id)
        print(message.channel.id)
        print(message.author.id)
        await client.delete_message(message)

#$REFRESH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if message.content.upper().startswith('$REFRESH') and message.author.id == str(341429638775701515):
        active_refresh()
        await client.delete_message(message)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    for x, y in player_spawn_dict.items():
        if x == message.author.id and y == 0:
            chance = 4
            if message.author.id == str(341429638775701515):
                chance = 3
            main_player = message.author
            test1 = random.randint(1,chance)
            test2 = random.randint(1,chance)
            test = test1 + test2
            if test == chance:
                game_channel = client.get_channel(player_channel_dict[main_player.id])

                query = ('SELECT player_location FROM player_game WHERE player_id = %s' % main_player.id)
                cursor.execute(query)
                temp_list = list(cursor.fetchall())
                temp_ = []

                for row in temp_list:
                    temp_ = [row[0]]

                user_location = temp_[0]

                pokemon_id, pokemon_level = encounters(user_location)
                player_spawn_dict[main_player.id] = 1
                bot_message = await client.send_message(game_channel,
                                                        '<@%s>, a wild Pokemon appeared!\n\n**Boom: Fight **|-|** Run: Flee**' % main_player.id)
                bot_reaction_fight = await client.add_reaction(bot_message, emoji=emoji_dict['fight'])
                bot_reaction_run = await client.add_reaction(bot_message, emoji=emoji_dict['run'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                if player_response.reaction.emoji == emoji_dict['fight']:
                    await client.delete_message(bot_message)
                    seed_list = seed(pokemon_id, pokemon_level)
                    player_pokemon = get_pokemon(main_player.id)
                    await battle(main_player, player_pokemon, seed_list, 1)
                elif player_response.reaction.emoji == emoji_dict['run']:
                    await client.delete_message(bot_message)
                    player_spawn_dict[main_player.id] = 0
                    return

#FUNCTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def setup(player_id, player_region, pokemon_id):
    start_location = 1
    start_level = 0
    start_money = 0
    temp1 = [player_id, player_region, start_location, start_level, player_experience_list[0], player_experience_list[1], start_money, pokemon_id, 0, 0, 0, 0, 0, 0, 0, 0]
    temp2 = [player_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    temp3 = [player_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    try:
        cursor.execute('UPDATE player_discord SET is_tutorial = 1 WHERE player_id = %s' % player_id)
        cursor.execute('INSERT INTO player_game VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', temp1)
        cursor.execute('INSERT INTO player_item_balls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', temp2)
        cursor.execute('INSERT INTO player_item_medicine VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', temp3)
        conn.commit()
        player_spawn_dict[player_id] = 0
    except:
        print("Error setting up player profile")

#GET_POKEMON~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_pokemon(author_id):
    query = ('SELECT pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6 FROM player_game WHERE player_id = %s' % author_id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    pokemon_list = []
    for row in temp_tuple:
        temp_list = [row[0], row[1], row[2], row[3], row[4], row[5]]
        pokemon_list = temp_list

    return pokemon_list

#ACTIVE_REFRESH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def active_refresh():
    query = 'SELECT * FROM player_game'
    cursor.execute(query)
    temp_list = list(cursor.fetchall())

    for row in temp_list:
        player_spawn_dict[str(row[0])] = 0

#ENCOUNTERS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def encounters(user_location):
    temp_pokemon = []
    temp_chance = []

    for row in encounter_pokemon_list[user_location-1]:
        temp_pokemon.append(row[0])
        temp_chance.append(row[1])

    pokemon_id = random.choices(temp_pokemon,temp_chance,k=1)
    pokemon_id = pokemon_id[0]

    min_level = 80
    max_level = 100
    for row in encounter_pokemon_list[user_location-1]:
        if row[0] == pokemon_id:
            min_level = row[2]
            max_level = row[3]
            break

    pokemon_level = random.randint(min_level,max_level)
    return pokemon_id, pokemon_level

#CALC_SIZE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def calc_size(is_height):
    global height_percent, weight_percent

    percent = 50  # placeholder if error
    if is_height == 1:
        percent = height_percent
    if is_height == 0:
        percent = weight_percent

    total_spread = 600
    z_score = 6
    offset = total_spread / percent
    roll_spread = total_spread / z_score

    probability = 0
    for i in range(z_score):
        roll = random.randint(0, roll_spread)
        probability = probability + roll

    difference = (probability - roll_spread * z_score / 2) / offset / 100
    ratio = 1 + difference
    return ratio

#CATCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def catch(seed_list, pokeball_id, player_name, player_id):
    global current_pokemon_id
    seed_list[0] = current_pokemon_id
    current_pokemon_id = current_pokemon_id + 1
    pokeball = pokeball_id
    user_name = player_name
    user_id = player_id
    original_player = player_name
    date_met = time.strftime("%m/%d/%Y")
    is_nicknamed = 0
    nickname = ""

    catch_data = [pokeball, user_name, user_id, original_player, date_met, is_nicknamed, nickname]

    n = 0
    for x in catch_data:
        seed_list.append(catch_data[n])
        n = n + 1

    #catch rate = 0
    seed_list[75] = 0

    try:
        cursor.execute(
            'INSERT INTO player_pokemon VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            seed_list)
        conn.commit()
        return (seed_list[0])
    except:
        print("Error saving Pokemon occurred")

#CALC_STATS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def calc_stats(current_pokemon):
    current_pokemon['hp_battle'] = int(
        (2 * current_pokemon['hp'] + current_pokemon['hp_iv'] + int(current_pokemon['hp_ev'] / 4)) * current_pokemon[
            'level'] / 100) + current_pokemon['level'] + 10
    current_pokemon['atk_battle'] = int((int(
        (2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['atk_nature'])
    current_pokemon['def_battle'] = int((int(
        (2 * current_pokemon['def_'] + current_pokemon['def_iv'] + int(current_pokemon['def_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['def_nature'])
    current_pokemon['spd_battle'] = int((int(
        (2 * current_pokemon['spd'] + current_pokemon['spd_iv'] + int(current_pokemon['spd_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spd_nature'])
    current_pokemon['spatk_battle'] = int((int(
        (2 * current_pokemon['spatk'] + current_pokemon['spatk_iv'] + int(current_pokemon['spatk_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spatk_nature'])
    current_pokemon['spdef_battle'] = int((int(
        (2 * current_pokemon['spdef'] + current_pokemon['spdef_iv'] + int(current_pokemon['spdef_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spdef_nature'])

    return(current_pokemon)

#CALC_BUFF~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def calc_buff(value,reg):
    percent = 1
    if value < 0:
        percent =  (2 + reg) / (2 + abs(value))
    elif value > 0:
        percent = (2 + value) / (2 + reg)
    else:
        percent = 1

    return(percent)

#AI_BATTLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ai_battle(ai_pokemon, players_pokemon):
    move_list = []
    if ai_pokemon['move1'] != 0:
        move_list.append(ai_pokemon['move1'])
    if ai_pokemon['move2'] != 0:
        move_list.append(ai_pokemon['move2'])
    if ai_pokemon['move3'] != 0:
        move_list.append(ai_pokemon['move3'])
    if ai_pokemon['move4'] != 0:
        move_list.append(ai_pokemon['move4'])

    move_choice = random.choice(move_list)
    return (move_choice)

#PRIORITY~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def priority(on_field_friendly, on_field_hostile):
    battle_list: List[Dict[str, int]] = []

    n = 0
    for i in on_field_friendly:
        if on_field_friendly[n] != 0:
            battle_list.append(on_field_friendly[n])
            n = n + 1

    n = 0
    for i in on_field_hostile:
        if on_field_hostile[n] != 0:
            battle_list.append(on_field_hostile[n])
            n = n + 1

    n = 0
    for i in battle_list:
        current_pokemon = battle_list[n]
        if current_pokemon['choice'] == 1:
            current_pokemon['priority'] = move_dict[current_pokemon['value']][6]
        if current_pokemon['choice'] == 2:
            current_pokemon['priority'] = 10
        if current_pokemon['choice'] == 3:
            current_pokemon['priority'] = 9
        n = n + 1

    battle_list = sorted(battle_list, key=itemgetter('priority', 'spd_battle'), reverse=True)
    return battle_list

#DAMAGE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def damage(pokemon_giving, move, pokemon_receiving, weather, main_player):
    stat_buff = ['hp_buff', 'atk_buff', 'def_buff', 'spatk_buff', 'spdef_buff', 'spd_buff', 'acc_buff', 'eva_buff']
    stats = ['health', 'attack', 'defense', 'special attack', 'special defense', 'speed', 'accuracy', 'evasion']
    ailment_list = ['none', 'paralysis', 'sleep', 'freeze', 'burn', 'poison', 'confusion', 'infatuation', 'trap', 'nightmare', 'torment', 'disable', 'yawn', 'heal_block', 'no_type_immunity', 'leech_seed', 'embargo', 'perish_song', 'ingrain', 'silence']
    target_type1 = pokemon_type_dict[pokemon_receiving['species_id']][0]
    target_type2 = pokemon_type_dict[pokemon_receiving['species_id']][1]

    user_accuracy = pokemon_giving['acc_buff']
    target_evasion = pokemon_receiving['eva_buff']

    type = move_dict[move][2]
    power = move_dict[move][3]
    accuracy = move_dict[move][5]
    target = move_dict[move][7]
    damage_class = move_dict[move][8]
    effect = move_dict[move][9]
    effect_chance = move_dict[move][10]

    category = move_meta_dict[move][0]
    ailment = move_meta_dict[move][1]
    min_hits = move_meta_dict[move][2]
    max_hits = move_meta_dict[move][3]
    min_turns = move_meta_dict[move][4]
    max_turns = move_meta_dict[move][5]
    drain = move_meta_dict[move][6]
    healing = move_meta_dict[move][7]
    crit_rate = move_meta_dict[move][8]
    ailment_chance = move_meta_dict[move][9]
    flinch_chance = move_meta_dict[move][10]
    stat_chance = move_meta_dict[move][11]

    damage = 0
    attack = 'atk_battle'
    defense = 'def_battle'
    attack_buff = 'atk_buff'
    defense_buff = 'def_buff'
    accuracy_result = 0
    effect_result = 0

    bot_message = await client.send_message(main_player, "%s used %s." % (pokemon_name_dict[pokemon_giving['species_id']], move_name_dict[move]))
    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
    await client.delete_message(bot_message)

    #accuracy check
    if not accuracy:
        print("this move skips accuracy check")
        accuracy_result = 1
    else:
        random_var = random.uniform(0,100)
        acc_limit = accuracy * calc_buff(user_accuracy,1)/calc_buff(target_evasion,1)
        print("Random Var:", random_var)
        print("Accuracy:", acc_limit)
        if acc_limit > random_var:
            accuracy_result = 1
            print('accuracy success')
        else:
            accuracy_result = 0
            print('accuracy failure')

    if not effect_chance:
        #print("this move skips effect chance check")
        effect_result = 0
    else:
        random_var = random.uniform(0, 100)
        if effect > random_var:
            effect_result = random_var
            #print('effect success')
        else:
            effect_result = 200
            #print('effect failure')

    if accuracy_result == 1:
        #status

        try:
            if damage_class == 1:
                recipient = {}
                if target == 7:
                    recipient = pokemon_giving
                else:
                    recipient = pokemon_receiving

                if not stat_chance:
                    stat_chance = 100

                if not effect_chance:
                    effect_chance = 100

                if effect_result < stat_chance:
                    counter = 0
                    for i in stat_buff:
                        if move_meta_stat_dict[move][counter] != 0:
                            recipient[stat_buff[counter]] = recipient[stat_buff[counter]] + move_meta_stat_dict[move][counter]
                            print(recipient[stat_buff[counter]])
                            prose = ""

                            if move_meta_stat_dict[move][counter] > 0:
                                if move_meta_stat_dict[move][counter] > 1:
                                    prose = "sharply rose"
                                else:
                                    prose = "rose"
                            if move_meta_stat_dict[move][counter] < 0:
                                if move_meta_stat_dict[move][counter] < -1:
                                    prose = "sharply decreased"
                                else:
                                    prose = "decreased"

                            bot_message = await client.send_message(main_player, "%s's %s **%s**." % (pokemon_name_dict[recipient['species_id']],stats[counter],prose))
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                            await client.delete_message(bot_message)

                        else:
                            pass
                        counter = counter + 1
                else:
                    bot_message = await client.send_message(main_player, "%s failed." (move_name_dict[move]))
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                    await client.delete_message(bot_message)

                if effect_result < ailment_chance:
                    if ailment <= 6:
                        recipient['ailment'] = ailment
                        bot_message = await client.send_message(main_player, "%s has been inflicted with %s."(pokemon_name_dict[recipient['species_id']],ailment_list[ailment]))
                        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                        await client.delete_message(bot_message)
                    else:
                        bot_message = await client.send_message(main_player, "%s would have been inflicted with %s, but the professor is a lazy piece of trash who hasn't gotten to programming this yet."(pokemon_name_dict[recipient['species_id']],ailment_list[ailment]))
                        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                        await client.delete_message(bot_message)
        except:
            print("ERROR")

        #non-status
        else:
            # physical
            if damage_class == 2:
                attack = 'atk_battle'
                defense = 'def_battle'
                attack_buff = 'atk_buff'
                defense_buff = 'def_buff'

            #special
            if damage_class == 3:
                attack = 'spatk_battle'
                defense = 'spatk_battle'
                attack_buff = 'spatk_buff'
                defense_buff = 'spdef_buff'

            critical = 1
            A = pokemon_giving['level']*critical
            B = calc_buff(pokemon_giving[attack_buff], 0) * pokemon_giving[attack]
            C = power
            D = calc_buff(pokemon_receiving[defense_buff], 0) * pokemon_receiving[defense]

            STAB = 1
            if type in pokemon_type_dict[pokemon_giving['species_id']]:
                STAB = 1.5
                #print("STAB Mod:", STAB)

            type_modifier1 = (type_efficacy_dict[type][target_type1 - 1])/100
            type_modifier2 = 1
            if target_type2 != 0:
                type_modifier2 = (type_efficacy_dict[type][target_type2 - 1])/100


            type_modifier = type_modifier1 * type_modifier2

            if type_modifier < 1 and type_modifier > 0:
                bot_message = await client.send_message(main_player, "It's not very effective.")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
            elif type_modifier > 1:
                bot_message = await client.send_message(main_player, "It's super effective!")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
            elif type_modifier == 0:
                bot_message = await client.send_message(main_player, "That move had no effect!")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            #print("Type Mod:", type_modifier)
            X = STAB
            Y = type_modifier
            Z = random.uniform(.85,1.0)

            if bool(power) == False:
                damage = 0
            else:
                damage = int((((2 * A / 5 + 2) * C * B / D) / 50 + 2) * X * Y * Z)

            pokemon_receiving['hp_current'] = pokemon_receiving['hp_current'] - damage
    else:
        bot_message = await client.send_message(main_player,
                                                "The enemy %s avoided the attack." % pokemon_name_dict[pokemon_receiving['species_id']])
        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
        await client.delete_message(bot_message)

    return (pokemon_giving, pokemon_receiving)

#EXPERIENCE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def experience(pokemon_list, opposing_pokemon):
    counter = 0
    exp_portion = 0
    for n in pokemon_list:
        current_pokemon = pokemon_list[counter]
        if bool(current_pokemon) == False:
            counter = counter + 1
        elif current_pokemon['participant'] == 1 and current_pokemon['hp_current'] > 0:
            exp_portion = exp_portion + 1
            counter = counter + 1
        else:
            counter = counter + 1

    counter = 0
    experience_list = [0, 0, 0, 0, 0, 0]
    for n in pokemon_list:
        current_pokemon = pokemon_list[counter]
        if bool(current_pokemon) == False:
            counter = counter + 1
        elif current_pokemon['participant'] == 1 and current_pokemon['hp_current'] > 0:
            a = 1
            t = 1
            b = pokemon_experience_dict[opposing_pokemon['species_id']]
            e = 1
            L = opposing_pokemon['level']
            p = 1
            f = 1
            v = 1
            s = 1

            experience = int((a * t * b * e * L * p * f * v) / (7 * s * exp_portion))
            if experience > 2000:
                experience = 2000

            experience_list[counter] = int(experience)
            counter = counter + 1
        else:
            counter = counter + 1

    return (experience_list)

#LEVEL_UP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def level_up(current_pokemon):
    current_pokemon['level'] = current_pokemon['level'] + 1
    experience_temp = experience_dict[current_pokemon['growth_rate_id']]
    current_pokemon['experience_to_next'] = experience_temp[current_pokemon['level']]
    current_pokemon['hp_battle'] = int(
        (2 * current_pokemon['hp'] + current_pokemon['hp_iv'] + int(current_pokemon['hp_ev'] / 4)) * current_pokemon[
            'level'] / 100) + current_pokemon['level'] + 10
    current_pokemon['atk_battle'] = int((int(
        (2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['atk_nature'])
    current_pokemon['def_battle'] = int((int(
        (2 * current_pokemon['def_'] + current_pokemon['def_iv'] + int(current_pokemon['def_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['def_nature'])
    current_pokemon['spd_battle'] = int((int(
        (2 * current_pokemon['spd'] + current_pokemon['spd_iv'] + int(current_pokemon['spd_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spd_nature'])
    current_pokemon['spatk_battle'] = int((int(
        (2 * current_pokemon['spatk'] + current_pokemon['spatk_iv'] + int(current_pokemon['spatk_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spatk_nature'])
    current_pokemon['spdef_battle'] = int((int(
        (2 * current_pokemon['spdef'] + current_pokemon['spdef_iv'] + int(current_pokemon['spdef_ev'] / 4)) * current_pokemon[
            'level'] / 100) + 5) * current_pokemon['spdef_nature'])

    query = (
                'SELECT move_id FROM pokemon_moves WHERE pokemon_method_id = 1 AND version_id = %s AND pokemon_id = %s AND level = %s' % (
        version_id, current_pokemon['species_id'], current_pokemon['level']))
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    move = 0
    for row in temp_tuple:
        if not temp_tuple:
            move = 0
        else:
            move = row[0]

    return (current_pokemon, move)

#SAVE_OUTCOME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_outcome(outcome, level, experience_total, experience_to_next, main_player):
    query = ('SELECT total_wins, total_losses, battle_count FROM player_game WHERE player_id = %s' % main_player.id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()
    temp_ = []

    counter = 0
    for row in temp_tuple:
        temp_ = [row[0],row[1],row[2]]

    total_wins = temp_[0]
    total_losses = temp_[1]
    battle_count = temp_[2]

    if outcome == 1:
        total_wins = total_wins + 1
        battle_count = battle_count + 1
        cursor.execute('UPDATE player_game SET player_level = %s, player_experience = %s, player_experience_to_next = %s, total_wins = %s, battle_count = %s WHERE player_id = %s' % (
        level, experience_total, experience_to_next, total_wins, battle_count, main_player.id))
        conn.commit()
    if outcome == 2:
        total_losses = total_losses + 1
        battle_count = 0
        default_location = 1
        cursor.execute('UPDATE player_game SET player_location = %s, total_losses = %s, battle_count = %s WHERE player_id = %s' % (
        default_location, total_losses, battle_count, main_player.id))
        conn.commit()

#SAVE_PROGRESS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def save_progress(pokemon_party):
    counter = 0
    current_pokemon = {}
    for i in pokemon_party:
        if pokemon_party[counter] != 0:
            current_pokemon = pokemon_party[counter]
            execute_list = (current_pokemon['species_id'],current_pokemon['level'],current_pokemon['experience'],current_pokemon['experience_to_next'],current_pokemon['hp'],current_pokemon['atk'],current_pokemon['def_'],current_pokemon['spd'],current_pokemon['spatk'],current_pokemon['spdef'],current_pokemon['hp_battle'],current_pokemon['atk_battle'],current_pokemon['def_battle'],current_pokemon['spd_battle'],current_pokemon['spatk_battle'],current_pokemon['spdef_battle'],current_pokemon['hp_current'],current_pokemon['ailment'],current_pokemon['held_item'],current_pokemon['ability'],current_pokemon['type1'],current_pokemon['type2'],current_pokemon['move1'],current_pokemon['move2'],current_pokemon['move3'],current_pokemon['move4'],current_pokemon['move1_pp'],current_pokemon['move2_pp'],current_pokemon['move3_pp'],current_pokemon['move4_pp'],current_pokemon['height'],current_pokemon['height_total'],current_pokemon['weight'],current_pokemon['weight_total'],current_pokemon['battle_ev1'],current_pokemon['battle_ev2'],current_pokemon['battle_ev3'],current_pokemon['battle_ev4'],current_pokemon['battle_ev5'],current_pokemon['battle_ev6'],current_pokemon['pokemon_id'])
            cursor.execute('UPDATE player_pokemon SET species_id = %s, level = %s, experience_points = %s,experience_to_next = %s,hp = %s,atk = %s,def = %s, spd = %s, spatk = %s, spdef = %s, hp_battle = %s, atk_battle = %s, def_battle = %s, spd_battle = %s, spatk_battle = %s, spdef_battle = %s, hp_current = %s,ailment = %s, held_item = %s, ability = %s, type1 = %s, type2 = %s, move1 = %s, move2 = %s, move3 = %s, move4 = %s, move1_pp = %s, move2_pp = %s, move3_pp = %s, move4_pp = %s, height = %s, height_total = %s, weight = %s, weight_total = %s, battle_ev1 = %s, battle_ev2 = %s, battle_ev3 = %s, battle_ev4 = %s, battle_ev5 = %s, battle_ev6 = %s WHERE pokemon_id = %s' % (execute_list))
            conn.commit()
        counter = counter + 1

#ASYNC_FUNCTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#BATTLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def battle(main_player, player_party, seed_list, battle_size):

    query = (
                'SELECT player_level, player_experience,player_experience_to_next FROM player_game WHERE player_id = %s' % main_player.id)
    cursor.execute(query)
    temp_tuple = cursor.fetchall()
    temp_ = []

    for row in temp_tuple:
        temp_ = [row[0], row[1], row[2]]

    weather = 1
    isexit = False
    player_level = temp_[0]
    player_experience = temp_[1]
    player_experience_to_next = temp_[2]
    trainer_experience = 0
    max_on_side = battle_size
    on_field_friendly: List[Dict[str, int]] = []
    on_field_hostile: List[Dict[str, int]] = []
    in_party_friendly = player_party
    in_party_hostile = [seed_list, 0, 0, 0, 0, 0]
    in_bag_friendly = []
    in_bag_hostile = []

    temp_dict = {'pokemon_id': 0, 'species_id': 0, 'level': 0, 'experience': 0,
                 'experience_to_next': 0, 'growth_rate_id': 0, 'friendship': 0, 'hp': 0,
                 'atk': 0, 'def_': 0, 'spd': 0, 'spatk': 0, 'spdef': 0,
                 'nature': 0, 'hp_nature': 0, 'atk_nature': 0, 'def_nature': 0,
                 'spd_nature': 0, 'spatk_nature': 0, 'spdef_nature': 0, 'hp_iv': 0,
                 'atk_iv': 0, 'def_iv': 0, 'spd_iv': 0, 'spatk_iv': 0,
                 'spdef_iv': 0, 'hp_ev': 0, 'atk_ev': 0, 'def_ev': 0,
                 'spd_ev': 0, 'spatk_ev': 0, 'spdef_ev': 0, 'hp_battle': 0,
                 'atk_battle': 0, 'def_battle': 0, 'spd_battle': 0,
                 'spatk_battle': 0, 'spdef_battle': 0, 'hp_current': 0,
                 'ailment': 0, 'held_item': 0, 'ability': 0, 'type1': 0, 'type2': 0,
                 'move1': 0, 'move2': 0, 'move3': 0, 'move4': 0,
                 'move1_pp': 0, 'move2_pp': 0, 'move3_pp': 0, 'move4_pp': 0,
                 'height': 0, 'height_bonus': 0, 'height_total': 0, 'weight': 0, 'weight_bonus': 0, 'weight_total': 0,
                 'ability_seed': 0, 'shiny': 0,
                 'hp_buff': 0, 'atk_buff': 0, 'def_buff': 0, 'spd_buff': 0, 'spatk_buff': 0, 'spdef_buff': 0,
                 'acc_buff': 0, 'eva_buff': 0,
                 'leveled': 0, 'participant': 0, 'choice': 0, 'value': 0, 'target_team': 0, 'target_pos': 0,
                 'switching': 0, 'priority': 0, 'team': 0, 'battle_id': 0,
                 'bound': 0, 'escape_block': 0, 'confusion': 0, 'curse': 0, 'embargo': 0, 'encore': 0, 'flinch': 0,
                 'heal_block': 0, 'identified': 0, 'infatuation': 0, 'leech_seed': 0, 'nightmare': 0, 'perish_song': 0,
                 'spooked': 0, 'taunt': 0, 'telekinesis': 0, 'torment': 0,
                 'aqua_ring': 0, 'bracing': 0, 'charging_turn': 0, 'center_of_attention': 0, 'defense_curl': 0,
                 'rooting': 0, 'magic_coat': 0, 'magnetic_levitation': 0, 'minimize': 0, 'protection': 0,
                 'team_protection': 0, 'recharging': 0, 'semi_invulnerable': 0, 'substitute': 0, 'taking_aim': 0,
                 'withdraw': 0}

    for x in range(0, max_on_side):
        on_field_friendly.append(dict(temp_dict))
        on_field_hostile.append(dict(temp_dict))

    on_field = [on_field_friendly, on_field_hostile]
    in_party = [in_party_friendly, in_party_hostile]

    counter = 0
    for i in in_party_friendly:
        current_pokemon = in_party_friendly[counter]
        if current_pokemon != 0:
            query = ('SELECT * FROM player_pokemon WHERE pokemon_id = %s' % current_pokemon)
            cursor.execute(query)
            temp_tuple = cursor.fetchall()

            n = 0
            for row in temp_tuple:
                temp_dict = {'pokemon_id': row[0], 'species_id': row[1], 'level': row[2], 'experience': row[3],
                             'experience_to_next': row[4], 'growth_rate_id': row[5], 'friendship': row[6], 'hp': row[7],
                             'atk': row[8], 'def_': row[9], 'spd': row[10], 'spatk': row[11], 'spdef': row[12],
                             'nature': row[13], 'hp_nature': row[14], 'atk_nature': row[15], 'def_nature': row[16],
                             'spd_nature': row[17], 'spatk_nature': row[18], 'spdef_nature': row[19], 'hp_iv': row[20],
                             'atk_iv': row[21], 'def_iv': row[22], 'spd_iv': row[23], 'spatk_iv': row[24],
                             'spdef_iv': row[25], 'hp_ev': row[26], 'atk_ev': row[27], 'def_ev': row[28],
                             'spd_ev': row[29], 'spatk_ev': row[30], 'spdef_ev': row[31], 'hp_battle': row[32],
                             'atk_battle': row[33],'def_battle': row[34], 'spd_battle': row[35],
                             'spatk_battle': row[36], 'spdef_battle': row[37], 'hp_current': row[38],
                             'ailment': row[39], 'held_item': row[40], 'ability': row[41], 'type1': row[42],
                             'type2': row[43], 'move1': row[44], 'move2': row[45], 'move3': row[46],
                             'move4': row[47], 'move1_pp': row[48], 'move2_pp': row[49], 'move3_pp': row[50],
                             'move4_pp': row[51], 'shiny': row[59],
                             'height': row[63], 'height_bonus': row[64], 'height_total': row[65], 'weight': row[66],
                             'weight_bonus': row[67], 'weight_total': row[68],
                             'battle_ev1': row[69], 'battle_ev2': row[70], 'battle_ev3': row[71], 'battle_ev4': row[72],
                             'battle_ev5': row[73], 'battle_ev6': row[74], 'catch_rate': row[75], 'ability_seed': row[76],
                             'hp_buff': 0, 'atk_buff': 0, 'def_buff': 0, 'spd_buff': 0, 'spatk_buff': 0, 'spdef_buff': 0, 'acc_buff': 0, 'eva_buff': 0,
                             'leveled': 0, 'participant': 0, 'choice': 0, 'value': 0,
                             'target_team': 0, 'target_pos': 0, 'switching': 0, 'priority': 0, 'team': 0,
                             'battle_id': int(counter),
                             'bound': 0, 'escape_block': 0, 'confusion': 0, 'curse': 0, 'embargo': 0, 'encore': 0,
                             'flinch': 0, 'heal_block': 0, 'identified': 0, 'infatuation': 0, 'leech_seed': 0,
                             'nightmare': 0, 'perish_song': 0, 'spooked': 0, 'taunt': 0, 'telekinesis': 0, 'torment': 0,
                             'aqua_ring': 0, 'bracing': 0, 'charging_turn': 0, 'center_of_attention': 0,
                             'defense_curl': 0, 'rooting': 0, 'magic_coat': 0, 'magnetic_levitation': 0, 'minimize': 0,
                             'protection': 0, 'team_protection': 0, 'recharging': 0, 'semi_invulnerable': 0,
                             'substitute': 0, 'taking_aim': 0, 'withdraw': 0}

                current_pokemon = dict(temp_dict)
                current_pokemon = calc_stats(current_pokemon)
                in_party_friendly[counter] = current_pokemon
                if current_pokemon['hp_current'] > 0:
                    if on_field_friendly[n]['pokemon_id'] == 0 and n < max_on_side:
                        on_field_friendly[n] = current_pokemon
                        n = n + 1

        counter = counter + 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    query = ('SELECT * FROM player_item_balls WHERE player_id = %s' % (main_player.id))
    cursor.execute(query)
    temp_tuple = cursor.fetchall()
    temp_dict1 = {}
    temp_dict2 = {}

    for row in temp_tuple:
        temp_dict1 = {'master_ball': row[1], 'ultra_ball': row[2], 'great_ball': row[3], 'poke_ball': row[4], 'safari_ball': row[5], 'net_ball': row[6], 'dive_ball': row[7]}

    in_bag_hostile.append(dict(temp_dict))

    query = ('SELECT * FROM player_item_medicine WHERE player_id = %s' % (main_player.id))
    cursor.execute(query)
    temp_tuple = cursor.fetchall()

    for row in temp_tuple:
        temp_dict2 = {'potion': row[1], 'antidote': row[2], 'burn_heal': row[3], 'ice_heal': row[4], 'awakening': row[5], 'paralyze_heal': row[6],
                     'full_restore': row[7], 'max_potion': row[8], 'hyper_potion': row[9], 'super_potion': row[10], 'full_heal': row[11],
                     'revive': row[12], 'max_revive': row[13], 'ether': row[14], 'max_ether': row[15], 'elixir': row[16], 'max_elixir': row[17]}

    in_bag_friendly = {**temp_dict1,**temp_dict2}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    counter = 0
    for row in in_party_hostile:
        n = 0
        if row != 0:
            current_pokemon = in_party_hostile[counter]
            temp_dict = {'pokemon_id': row[0], 'species_id': row[1], 'level': row[2],
                         'experience': row[3], 'experience_to_next': row[4], 'growth_rate_id': row[5],
                         'friendship': row[6], 'hp': row[7], 'atk': row[8], 'def_': seed_list[9],
                         'spd': row[10], 'spatk': row[11], 'spdef': row[12], 'nature': row[13],
                         'hp_nature': row[14], 'atk_nature': row[15], 'def_nature': row[16],
                         'spd_nature': row[17], 'spatk_nature': row[18], 'spdef_nature': row[19],
                         'hp_iv': row[20], 'atk_iv': row[21], 'def_iv': row[22],
                         'spd_iv': row[23], 'spatk_iv': row[24], 'spdef_iv': row[25],
                         'hp_ev': row[26], 'atk_ev': row[27], 'def_ev': row[28],
                         'spd_ev': row[29], 'spatk_ev': row[30], 'spdef_ev': row[31],
                         'hp_battle': row[32], 'atk_battle': row[33], 'def_battle': row[34],
                         'spd_battle': row[35], 'spatk_battle': row[36], 'spdef_battle': row[37],
                         'hp_current': row[38], 'ailment': row[39], 'held_item': row[40],
                         'ability': row[41], 'type1': row[42], 'type2': row[43],
                         'move1': row[44], 'move2': row[45], 'move3': row[46], 'move4': row[47],
                         'move1_pp': row[48], 'move2_pp': row[49], 'move3_pp': row[50],
                         'move4_pp': row[51], 'shiny': row[59], 'height': row[63], 'height_bonus': row[64], 'height_total': row[65],
                         'weight': row[66], 'weight_bonus': row[67], 'weight_total': row[68], 'ability_seed': row[76],
                         'battle_ev1': row[69], 'battle_ev2': row[70], 'battle_ev3': row[71], 'battle_ev4': row[72],
                         'battle_ev5': row[73], 'battle_ev6': row[74], 'catch_rate': row[75], 'ability_seed': row[76],
                         'hp_buff': 0, 'atk_buff': 0, 'def_buff': 0, 'spd_buff': 0, 'spatk_buff': 0, 'spdef_buff': 0,
                         'acc_buff': 0, 'eva_buff': 0,
                         'leveled': 0, 'participant': 0, 'choice': 0, 'value': 0, 'target_team': 0, 'target_pos': 0,
                         'switching': 0, 'priority': 0, 'team': 1, 'battle_id': int(counter),
                         'bound': 0, 'escape_block': 0, 'confusion': 0, 'curse': 0, 'embargo': 0, 'encore': 0,
                         'flinch': 0, 'heal_block': 0, 'identified': 0, 'infatuation': 0, 'leech_seed': 0,
                         'nightmare': 0, 'perish_song': 0, 'spooked': 0, 'taunt': 0, 'telekinesis': 0, 'torment': 0,
                         'aqua_ring': 0, 'bracing': 0, 'charging_turn': 0, 'center_of_attention': 0, 'defense_curl': 0,
                         'rooting': 0, 'magic_coat': 0, 'magnetic_levitation': 0, 'minimize': 0, 'protection': 0,
                         'team_protection': 0, 'recharging': 0, 'semi_invulnerable': 0, 'substitute': 0,
                         'taking_aim': 0, 'withdraw': 0}

            current_pokemon = dict(temp_dict)
            current_pokemon = calc_stats(current_pokemon)
            in_party_hostile[counter] = current_pokemon
            if current_pokemon['hp_current'] > 0:
                if on_field_hostile[n]['pokemon_id'] == 0 and n < max_on_side:
                    on_field_hostile[n] = current_pokemon
                    n = n + 1
        counter = counter + 1

    shiny_enemy = ''
    shiny_friendly = ''

    if on_field_hostile[0]['shiny'] == 1:
        shiny_enemy = 'shiny/'
    if on_field_friendly[0]['shiny'] == 1:
        shiny_friendly = 'shiny/'

    bot_picture = await client.send_file(main_player, 'C:/Users/Sylvester/Documents/PokemonSprites/%s%s.png' % (shiny_enemy, on_field_hostile[0]['species_id']))

    bot_message = await client.send_message(main_player,
                                            "A wild **%s** appeared. You chose **%s**!\n\n**Circle: Continue**" % (
                                                pokemon_name_dict[on_field_hostile[0]['species_id']],
                                                pokemon_name_dict[on_field_friendly[0]['species_id']]))
    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

    isbattle = True
    while bool(isbattle):

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # setup

        issetup = True
        while bool(issetup):
            counter = 0
            for i in on_field_friendly:
                if on_field_friendly[counter] != 0:

                    try:
                        await client.delete_message(bot_message)
                    except:
                        pass

                    shiny_enemy = ''
                    shiny_friendly = ''

                    if on_field_hostile[0]['shiny'] == 1:
                        shiny_enemy = 'shiny/'
                    if on_field_friendly[0]['shiny'] == 1:
                        shiny_friendly = 'shiny/'

                    try:
                        await client.delete_message(bot_picture)
                    except:
                        pass

                    hello = 0
                    t0 = time.time()
                    player_pokemon = Image.open('C:/Users/Sylvester/Documents/PokemonSprites/back/%s%s.png' % (
                    shiny_friendly, on_field_friendly[0]['species_id']))
                    enemy_pokemon = Image.open(
                        'C:/Users/Sylvester/Documents/PokemonSprites/%s%s.png' % (shiny_enemy,on_field_hostile[0]['species_id']))
                    background = Image.open('C:/Users/Sylvester/Documents/PokemonSprites/background.png')

                    offset_player = (10, 60)
                    offset_enemy = (160, 10)

                    background.paste(player_pokemon, offset_player)
                    background.paste(enemy_pokemon, offset_enemy)
                    t1 = time.time()
                    hello = t1 - t0
                    print("Time to create:", hello)
                    background.save('test.png')
                    t2 = time.time()
                    hello = t2 - t1
                    print("Time to save:", hello)
                    bot_picture = await client.send_file(main_player, 'test.png')
                    t3 = time.time()
                    hello = t3 - t2
                    print("Time to send:", hello)
                    bot_message = await client.send_message(main_player,
                                                            "**Player** Level %s %s has %s/%s health\n**Enemy** Level %s %s has %s/%s health\nWhat would you like to do?\n\n"
                                                            "**Boom: Fight**\n"
                                                            "**Arrows: Switch** \n"
                                                            "**Bags: Inventory**\n"
                                                            "**Run: Flee**" % (
                                                                on_field_friendly[counter]['level'],
                                                                pokemon_name_dict[
                                                                    on_field_friendly[counter]['species_id']],
                                                                on_field_friendly[counter]['hp_current'],
                                                                on_field_friendly[counter]['hp_battle'],
                                                                on_field_hostile[0]['level'],
                                                                pokemon_name_dict[
                                                                    on_field_hostile[0]['species_id']],
                                                                on_field_hostile[0]['hp_current'],
                                                                on_field_hostile[0]['hp_battle']))

                    bot_reaction_fight = await client.add_reaction(bot_message, emoji=emoji_dict['fight'])
                    bot_reaction_switch = await client.add_reaction(bot_message, emoji=emoji_dict['switch'])
                    bot_reaction_item = await client.add_reaction(bot_message, emoji=emoji_dict['item'])
                    bot_reaction_run = await client.add_reaction(bot_message, emoji=emoji_dict['run'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                    if player_response.reaction.emoji == emoji_dict['fight']:

                        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
                        # fight

                        isfight = True
                        while (isfight):

                            await client.delete_message(bot_message)
                            bot_message = await client.send_message(main_player,
                                                                    "Please select a move:\n\n"
                                                                    "**1: %s |-| PP: ???/???**\n"
                                                                    "**2: %s |-| PP: ???/???**\n"
                                                                    "**3: %s |-| PP: ???/???**\n"
                                                                    "**4: %s |-| PP: ???/???**" % (
                                                                        str(move_name_dict[
                                                                                on_field_friendly[counter][
                                                                                    "move1"]]),
                                                                        str(move_name_dict[
                                                                                on_field_friendly[counter][
                                                                                    "move2"]]),
                                                                        str(move_name_dict[
                                                                                on_field_friendly[counter][
                                                                                    "move3"]]),
                                                                        str(move_name_dict[
                                                                                on_field_friendly[counter][
                                                                                    "move4"]])))

                            if (on_field_friendly[counter]['move1']) != 0:
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['one'])
                            if (on_field_friendly[counter]['move2']) != 0:
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['two'])
                            if (on_field_friendly[counter]['move3']) != 0:
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['three'])
                            if (on_field_friendly[counter]['move4']) != 0:
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['four'])

                            bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                            if player_response.reaction.emoji == emoji_dict['one'] and (
                            on_field_friendly[counter]['move1']) != 0:
                                on_field_friendly[counter]['choice'] = 1
                                on_field_friendly[counter]['value'] = on_field_friendly[counter][
                                    "move1"]
                                on_field_friendly[counter]['target_team'] = 1
                                on_field_friendly[counter]['target_pos'] = 0
                                on_field_friendly[counter]['participant'] = 1
                                issetup = False
                                break
                            elif player_response.reaction.emoji == emoji_dict['two'] and (
                            on_field_friendly[counter]['move2']) != 0:
                                on_field_friendly[counter]['choice'] = 1
                                on_field_friendly[counter]['value'] = on_field_friendly[counter][
                                    "move2"]
                                on_field_friendly[counter]['target_team'] = 1
                                on_field_friendly[counter]['target_pos'] = 0
                                on_field_friendly[counter]['participant'] = 1
                                issetup = False
                                break
                            elif player_response.reaction.emoji == emoji_dict['three'] and (
                            on_field_friendly[counter]['move3']) != 0:
                                on_field_friendly[counter]['choice'] = 1
                                on_field_friendly[counter]['value'] = on_field_friendly[counter][
                                    "move3"]
                                on_field_friendly[counter]['target_team'] = 1
                                on_field_friendly[counter]['target_pos'] = 0
                                on_field_friendly[counter]['participant'] = 1
                                issetup = False
                                break
                            elif player_response.reaction.emoji == emoji_dict['four'] and (
                            on_field_friendly[counter]['move4']) != 0:
                                on_field_friendly[counter]['choice'] = 1
                                on_field_friendly[counter]['value'] = on_field_friendly[counter][
                                    "move4"]
                                on_field_friendly[counter]['target_team'] = 1
                                on_field_friendly[counter]['target_pos'] = 0
                                on_field_friendly[counter]['participant'] = 1
                                issetup = False
                                break
                            else:
                                isfight = False
                                break

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                    if player_response.reaction.emoji == emoji_dict['switch']:

                        isswitch = True
                        while bool(isswitch):
                            n = 0
                            current_pokemon = []
                            pokemon_exclude = 0
                            for i in on_field_friendly:
                                current_pokemon = on_field_friendly[n]
                                if bool(current_pokemon):
                                    if current_pokemon['hp_current'] > 0 and current_pokemon['switching'] == 0:
                                        pokemon_exclude = pokemon_exclude + 1
                                n = n + 1

                            n = 0
                            pokemon_available = 0
                            for i in in_party_friendly:
                                current_pokemon = in_party_friendly[n]
                                if bool(current_pokemon):
                                    if current_pokemon['hp_current'] > 0 and current_pokemon['switching'] == 0:
                                        pokemon_available = pokemon_available + 1
                                n = n + 1

                            pokemon_available = pokemon_available - pokemon_exclude

                            if pokemon_available < 1:
                                await client.delete_message(bot_message)
                                bot_message = await client.send_message(main_player,
                                                                        "You don't have any other Pokemon to switch to.\n\n**Circle: Continue**")
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                                isswitch = False
                                break

                            switch_list = ['None', 'None', 'None', 'None', 'None', 'None']
                            n = 0
                            for i in switch_list:
                                current_pokemon = in_party_friendly[n]
                                if current_pokemon != 0:
                                    txt = (pokemon_name_dict[current_pokemon['species_id']], '-', current_pokemon['hp_current'], '/', current_pokemon['hp_battle'],'HP')
                                    switch_list[n] = str(txt)
                                else:
                                    txt = ("None", "-", "???", "/", "???", "HP")
                                    switch_list[n] = str(txt)
                                n = n + 1

                            await client.delete_message(bot_message)
                            bot_message = await client.send_message(main_player,
                                                                    "Which Pokemon do you choose?\n\n"
                                                                    "1: %s\n"
                                                                    "2: %s\n"
                                                                    "3: %s\n"
                                                                    "4: %s\n"
                                                                    "5: %s\n"
                                                                    "6: %s\n" % (switch_list[0],switch_list[1],switch_list[2],switch_list[3],switch_list[4],switch_list[5]))


                            move_list_temp = ['one', 'two', 'three', 'four', 'five', 'six']
                            n = 0
                            for i in in_party_friendly:
                                if bool(in_party_friendly[n]):
                                    reaction_bool = False
                                    m = 0
                                    for i in on_field_friendly:
                                        if on_field_friendly[m]['pokemon_id'] != in_party_friendly[n][
                                            'pokemon_id'] and in_party_friendly[n][
                                            'hp_current'] > 0 and in_party_friendly[n]['switching'] == 0:
                                            reaction_bool = True
                                        m = m + 1
                                    if bool(reaction_bool):
                                        bot_reaction = await client.add_reaction(bot_message,
                                                                                 emoji=emoji_dict[move_list_temp[n]])
                                n = n + 1
                            bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                            if player_response.reaction.emoji == emoji_dict['one'] and bool(
                                    in_party_friendly[0]) and in_party_friendly[0]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 0
                                isswitch = False
                                issetup = False
                            elif player_response.reaction.emoji == emoji_dict['two'] and bool(
                                    in_party_friendly[1]) and in_party_friendly[1]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 1
                                isswitch = False
                                issetup = False
                            elif player_response.reaction.emoji == emoji_dict['three'] and bool(
                                    in_party_friendly[2]) and in_party_friendly[2]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 2
                                on_field_friendly[counter]['participant'] = 1
                                isswitch = False
                                issetup = False
                            elif player_response.reaction.emoji == emoji_dict['four'] and bool(
                                    in_party_friendly[3]) and in_party_friendly[3]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 3
                                isswitch = False
                                issetup = False
                            elif player_response.reaction.emoji == emoji_dict['five'] and bool(
                                    in_party_friendly[4]) and in_party_friendly[4]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 4
                                isswitch = False
                                issetup = False
                            elif player_response.reaction.emoji == emoji_dict['six'] and bool(
                                    in_party_friendly[5]) and in_party_friendly[5]['hp_current'] > 0:
                                on_field_friendly[counter]['choice'] = 2
                                on_field_friendly[counter]['value'] = 0
                                on_field_friendly[counter]['target_team'] = on_field_friendly[counter][
                                    'team']
                                on_field_friendly[counter]['target_pos'] = 5
                                isswitch = False
                                issetup = False
                            else:
                                isswitch = False
                                break

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                    if player_response.reaction.emoji == emoji_dict['item']:

                        isitem = True
                        while bool(isitem):
                            temp_bag_tab = ['1:.............','2:.............','3:.............','4:.............','5:.............']
                            try:
                                await client.delete_message(bot_message)
                            except:
                                pass
                            bot_message = await client.send_message(main_player,
                                                                "Populating Inventory...\n"
                                                                "%s\n"
                                                                "%s\n"
                                                                "%s\n"
                                                                "%s\n"
                                                                "%s" % (temp_bag_tab[0],temp_bag_tab[1],temp_bag_tab[2],temp_bag_tab[3],temp_bag_tab[4]))

                            emoji_list = ['fleft', 'left', 'one', 'two', 'three', 'four', 'five', 'right', 'fright', 'no']

                            n = 0
                            for i in emoji_list:
                                await client.add_reaction(bot_message, emoji=emoji_dict[emoji_list[n]])
                                n = n + 1

                            pockets_item_name = [[],[]]
                            pockets_item_amount = [[],[]]
                            temp_item_list_name = []
                            temp_item_list_amount = []
                            counter_a = 0
                            counter_b = 0
                            counter_c = 0
                            print(in_bag_friendly)

                            for i in global_bag_tabs:
                                for i in range(0,math.ceil(len(global_bag_tabs[counter_a])/5)):
                                    for i in range(0,5):
                                        temp_item_name = ".........."
                                        temp_item_amount = 0

                                        try:
                                            if in_bag_friendly[global_bag_tabs[counter_a][counter_b]] != 0:
                                                temp_item_name = global_bag_tabs[counter_a][counter_b]
                                                temp_item_amount = in_bag_friendly[global_bag_tabs[counter_a][counter_b]]
                                        except:
                                            pass

                                        temp_item_list_name.append(str(temp_item_name))
                                        temp_item_list_amount.append(int(temp_item_amount))
                                        counter_b += 1
                                        counter_c += 1
                                    counter_c = 0
                                    pockets_item_name[counter_a].append(list(temp_item_list_name))
                                    pockets_item_amount[counter_a].append(list(temp_item_list_amount))
                                    temp_item_list_name.clear()
                                    temp_item_list_amount.clear()
                                counter_b = 0
                                counter_a += 1

                            print(pockets_item_name)
                            print(pockets_item_amount)

                            default_pocket = [0,0]

                            isbrowse = True
                            while bool(isbrowse):
                                try:
                                    bot_message = await client.edit_message(bot_message,
                                                                        "**%s**\n"
                                                                        "1: **%s** - %s\n"
                                                                        "2: **%s** - %s\n"
                                                                        "3: **%s** - %s\n"
                                                                        "4: **%s** - %s\n"
                                                                        "5: **%s** - %s" % (global_pockets[default_pocket[0]],
                                                                                            pockets_item_name[default_pocket[0]][default_pocket[1]][0],pockets_item_amount[default_pocket[0]][default_pocket[1]][0],
                                                                                            pockets_item_name[default_pocket[0]][default_pocket[1]][1],pockets_item_amount[default_pocket[0]][default_pocket[1]][1],
                                                                                            pockets_item_name[default_pocket[0]][default_pocket[1]][2],pockets_item_amount[default_pocket[0]][default_pocket[1]][2],
                                                                                            pockets_item_name[default_pocket[0]][default_pocket[1]][3],pockets_item_amount[default_pocket[0]][default_pocket[1]][3],
                                                                                            pockets_item_name[default_pocket[0]][default_pocket[1]][4],pockets_item_amount[default_pocket[0]][default_pocket[1]][4]))
                                except:
                                    break
                                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                                item_choice = 0
                                istarget = False

                                if player_response.reaction.emoji == emoji_dict['fleft'] and default_pocket[0] > 0:
                                    try:
                                        default_pocket[0] -= 1
                                    except:
                                        pass
                                elif player_response.reaction.emoji == emoji_dict['left'] and default_pocket[1] > 0:
                                    try:
                                        default_pocket[1] -= 1
                                    except:
                                        pass
                                elif player_response.reaction.emoji == emoji_dict['fright'] and default_pocket[0] < 1:
                                    try:
                                        default_pocket[0] += 1
                                    except:
                                        pass
                                elif player_response.reaction.emoji == emoji_dict['right'] and default_pocket[1] < 1:
                                    try:
                                        default_pocket[1] += 1
                                    except:
                                        pass
                                elif player_response.reaction.emoji == emoji_dict['one'] and pockets_item_name[default_pocket[0]][default_pocket[1]][0] != "..........":
                                    item_choice = pockets_item_name[default_pocket[0]][default_pocket[1]][0]
                                    istarget = True
                                elif player_response.reaction.emoji == emoji_dict['two'] and pockets_item_name[default_pocket[0]][default_pocket[1]][1] != "..........":
                                    item_choice = pockets_item_name[default_pocket[0]][default_pocket[1]][1]
                                    istarget = True
                                elif player_response.reaction.emoji == emoji_dict['three'] and pockets_item_name[default_pocket[0]][default_pocket[1]][2] != "..........":
                                    item_choice = pockets_item_name[default_pocket[0]][default_pocket[1]][2]
                                    istarget = True
                                elif player_response.reaction.emoji == emoji_dict['four'] and pockets_item_name[default_pocket[0]][default_pocket[1]][3] != "..........":
                                    item_choice = pockets_item_name[default_pocket[0]][default_pocket[1]][3]
                                    istarget = True
                                elif player_response.reaction.emoji == emoji_dict['five'] and pockets_item_name[default_pocket[0]][default_pocket[1]][4] != "..........":
                                    item_choice = pockets_item_name[default_pocket[0]][default_pocket[1]][4]
                                    istarget = True
                                else:
                                    isbrowse = False
                                    isitem = False
                                    break


                                while bool(istarget):
                                    if item_dict[item_choice][0] == 34:

                                        bot_message_new = await client.send_message(main_player,
                                                                                    "Select a target.\n"
                                                                                    "**1: %s**" % pokemon_name_dict[on_field_hostile[0]['species_id']])
                                        bot_reaction_one = await client.add_reaction(bot_message_new,
                                                                                       emoji=emoji_dict['one'])
                                        bot_reaction_no = await client.add_reaction(bot_message_new,
                                                                                       emoji=emoji_dict['no'])
                                        player_response = await client.wait_for_reaction(message=bot_message_new,
                                                                                         user=main_player)
                                        if player_response.reaction.emoji == emoji_dict['one']:
                                            on_field_friendly[counter]['choice'] = 3
                                            on_field_friendly[counter]['value'] = item_choice
                                            on_field_friendly[counter]['target_team'] = on_field_hostile[counter][
                                                'team']
                                            on_field_friendly[counter]['target_pos'] = 0
                                            await client.delete_message(bot_message_new)
                                            istarget = False
                                            isbrowse = False
                                            isitem = False
                                            issetup = False
                                        else:
                                            istarget = False
                                            await client.delete_message(bot_message_new)
                                            break
                                    elif item_dict[item_choice][0] == 27:
                                        bot_message_new = await client.send_message(main_player,
                                                                                    "Select a target.\n"
                                                                                    "**1: %s**" % pokemon_name_dict[
                                                                                        on_field_friendly[0][
                                                                                            'species_id']])
                                        bot_reaction_one = await client.add_reaction(bot_message_new,
                                                                                     emoji=emoji_dict['one'])
                                        bot_reaction_no = await client.add_reaction(bot_message_new,
                                                                                    emoji=emoji_dict['no'])
                                        player_response = await client.wait_for_reaction(message=bot_message_new,
                                                                                         user=main_player)
                                        if player_response.reaction.emoji == emoji_dict['one']:
                                            on_field_friendly[counter]['choice'] = 3
                                            on_field_friendly[counter]['value'] = item_choice
                                            on_field_friendly[counter]['target_team'] = on_field_hostile[counter][
                                                'team']
                                            on_field_friendly[counter]['target_pos'] = 0
                                            await client.delete_message(bot_message_new)
                                            istarget = False
                                            isbrowse = False
                                            isitem = False
                                            issetup = False
                                        else:
                                            istarget = False
                                            await client.delete_message(bot_message_new)
                                            break
                                    else:
                                        bot_message_new = await client.send_message(main_player,
                                                                                "Sorry, you can't use this item yet.\n\n**Circle: Continue**")
                                        bot_reaction_yes = await client.add_reaction(bot_message_new, emoji=emoji_dict['yes'])
                                        player_response = await client.wait_for_reaction(message=bot_message_new,
                                                                                         user=main_player)
                                        await client.delete_message(bot_message_new)
                                        istarget = False
                                        break

                            try:
                                await client.delete_message(bot_message)
                            except:
                                pass

                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

                    if player_response.reaction.emoji == emoji_dict['run']:

                        isflee = True
                        while isflee == True:

                            await client.delete_message(bot_message)
                            bot_message = await client.send_message(main_player,
                                                                    "Are you sure you want to run away?")
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                            if player_response.reaction.emoji == emoji_dict['yes']:
                                battle_outcome = 0
                                isexit = True
                                isflee = False
                                issetup = False
                                break
                            else:
                                isflee = False


        #AI DECISION~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        counter = 0
        for i in on_field_hostile:
            on_field_hostile[counter]['choice'] = 1
            on_field_hostile[counter]['value'] = ai_battle(on_field_hostile[0],
                                                                   on_field_friendly[0])
            on_field_hostile[counter]['target_team'] = 0
            on_field_hostile[counter]['target_pos'] = 0
            counter = counter + 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        isdamage = False

        if isexit == False:
            isdamage = True
        battle_outcome = 0

        while bool(isdamage):

            def reset(dict):
                dict['choice'] = 0
                dict['value'] = 0
                dict['target'] = 0

            battle_list = priority(on_field_friendly, on_field_hostile)

            try:
                await client.delete_message(bot_message)
            except:
                pass

            counter = 0
            for i in battle_list:

                def find(lst, position, key, value):
                    for i, dic in enumerate(lst[position]):
                        if dic[key] == value:
                            return i
                    return -1

                current_pokemon = battle_list[counter]
                if current_pokemon['choice'] == 1:
                    forceswitch = False
                    if current_pokemon['hp_current'] > 0:
                        target_pokemon = on_field[current_pokemon['target_team']][current_pokemon['target_pos']]
                        current_pokemon, target_pokemon = await damage(current_pokemon, current_pokemon['value'], target_pokemon, weather, main_player)

                        if target_pokemon['hp_current'] <= 0:
                            target_pokemon['hp_current'] = 0

                            try:
                                await client.delete_message(bot_message)
                            except:
                                pass

                            if target_pokemon['team'] == 1:
                                battle_outcome = 1
                                isexit = True
                                break
                            if target_pokemon['team'] == 0:
                                bot_message = await client.send_message(main_player,
                                                                        "%s fainted.\n\n**Circle: Continue**" %
                                                                        pokemon_name_dict[
                                                                            target_pokemon['species_id']])
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                                forceswitch = True

                    else:
                        forceswitch = True

                    if bool(forceswitch):
                        isswitch = True
                        temp_pokemon = {}
                        while bool(isswitch):
                            temp_pokemon = {}

                            n = 0
                            pokemon_exclude = 0
                            for i in on_field_friendly:
                                temp_pokemon = on_field_friendly[n]
                                if bool(temp_pokemon):
                                    if temp_pokemon['hp_current'] > 0 and temp_pokemon['switching'] == 0:
                                        pokemon_exclude = pokemon_exclude + 1
                                n = n + 1

                            n = 0
                            pokemon_available = 0

                            for i in in_party_friendly:
                                temp_pokemon = in_party_friendly[n]
                                if bool(temp_pokemon):
                                    if temp_pokemon['hp_current'] > 0 and temp_pokemon['switching'] == 0:
                                        pokemon_available = pokemon_available + 1
                                n = n + 1

                            pokemon_available = pokemon_available - pokemon_exclude

                            if pokemon_available < 1:
                                await client.delete_message(bot_message)
                                bot_message = await client.send_message(main_player,
                                                                        "You don't have any other Pokemon to switch to.\n\n**Circle: Continue**")
                                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                                battle_outcome = 2
                                forceswitch = False
                                isswitch = False
                                isexit = True
                                break

                            switch_list = ['None', 'None', 'None', 'None', 'None', 'None']
                            n = 0
                            for i in switch_list:
                                temp_pokemon = in_party_friendly[n]
                                if bool(temp_pokemon):
                                    txt = (pokemon_name_dict[temp_pokemon['species_id']], '-', temp_pokemon['hp_current'], '/', temp_pokemon['hp_battle'],'HP')
                                    switch_list[n] = str(txt)
                                else:
                                    txt = ("None", "-", "???", "/", "???", "HP")
                                    switch_list[n] = str(txt)
                                n = n + 1

                            await client.delete_message(bot_message)
                            bot_message = await client.send_message(main_player,
                                                                    "Which Pokemon do you choose?\n\n"
                                                                    "1: %s\n"
                                                                    "2: %s\n"
                                                                    "3: %s\n"
                                                                    "4: %s\n"
                                                                    "5: %s\n"
                                                                    "6: %s\n" % (
                                                                        switch_list[0], switch_list[1], switch_list[2],
                                                                        switch_list[3], switch_list[4],
                                                                        switch_list[5]))

                            move_list_temp = ['one', 'two', 'three', 'four', 'five', 'six']
                            n = 0
                            for i in in_party_friendly:
                                if bool(in_party_friendly[n]):
                                    reaction_bool = False
                                    m = 0
                                    for i in on_field_friendly:
                                        if on_field_friendly[m]['pokemon_id'] != in_party_friendly[n][
                                            'pokemon_id'] and in_party_friendly[n][
                                            'hp_current'] > 0 and in_party_friendly[n]['switching'] == 0:
                                            reaction_bool = True
                                        m = m + 1
                                    if bool(reaction_bool):
                                        bot_reaction = await client.add_reaction(bot_message,
                                                                                 emoji=emoji_dict[move_list_temp[n]])
                                n = n + 1
                            bot_reaction_no = client.add_reaction(bot_message, emoji=emoji_dict['no'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                            if player_response.reaction.emoji == emoji_dict['one'] and bool(
                                    in_party_friendly[0]) and in_party_friendly[0]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][0]
                                isswitch = False
                            elif player_response.reaction.emoji == emoji_dict['two'] and bool(
                                    in_party_friendly[1]) and in_party_friendly[1]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][1]
                                isswitch = False
                            elif player_response.reaction.emoji == emoji_dict['three'] and bool(
                                    in_party_friendly[2]) and in_party_friendly[2]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][2]
                                isswitch = False
                            elif player_response.reaction.emoji == emoji_dict['four'] and bool(
                                    in_party_friendly[3]) and in_party_friendly[3]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][3]
                                isswitch = False
                            elif player_response.reaction.emoji == emoji_dict['five'] and bool(
                                    in_party_friendly[4]) and in_party_friendly[4]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][4]
                                isswitch = False
                            elif player_response.reaction.emoji == emoji_dict['six'] and bool(
                                    in_party_friendly[5]) and in_party_friendly[5]['hp_current'] > 0:
                                temp_pos_old = find(on_field, target_pokemon['team'], 'battle_id',
                                                    target_pokemon['battle_id'])
                                on_field[target_pokemon['team']][temp_pos_old] = \
                                in_party[target_pokemon['team']][5]
                                isswitch = False
                            else:
                                pass

                        forceswitch = False

                if current_pokemon['choice'] == 2:
                    try:
                        await client.delete_message(bot_message)
                    except:
                        pass
                    bot_message = await client.send_message(main_player, "%s, come back!" % (
                        pokemon_name_dict[current_pokemon['species_id']]))
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                    temp_pos_old = find(on_field, current_pokemon['team'], 'battle_id',
                                        current_pokemon['battle_id'])
                    on_field[current_pokemon['team']][temp_pos_old] = \
                    in_party[current_pokemon['target_team']][current_pokemon['target_pos']]

                    current_pokemon = in_party[(current_pokemon['target_team'])][current_pokemon['target_pos']]

                    await client.delete_message(bot_message)
                    bot_message = await client.send_message(main_player,
                                                            "Go, %s!" % (pokemon_name_dict[
                                                                current_pokemon['species_id']]))
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                if current_pokemon['choice'] == 3:
                    target_pokemon = on_field[current_pokemon['target_team']][current_pokemon['target_pos']]

                    try:
                        await client.delete_message(bot_message)
                    except:
                        pass

                    if current_pokemon['value'] in ['poke_ball', 'great_ball', "ultra_ball"]:
                        result = await attempt_catch(target_pokemon, current_pokemon['value'], main_player)
                    elif current_pokemon['value'] == 'potion':
                        current_pokemon['hp_current'] += 20
                        result = 0
                    elif current_pokemon['value'] == 'super_potion':
                        current_pokemon['hp_current'] += 60
                        result = 0
                    elif current_pokemon['value'] == 'hyper_potion':
                        current_pokemon['hp_current'] += 120
                        result = 0
                    else:
                        result = 0

                    in_bag_friendly[current_pokemon['value']] -= 1

                    if current_pokemon['value'] in global_bag_tabs:
                        cursor.execute('UPDATE player_item_balls SET %s = %s - 1 WHERE player_id = %s' % (current_pokemon['value'],current_pokemon['value'],main_player.id))

                    if current_pokemon['hp_current'] > current_pokemon['hp_battle']:
                        current_pokemon['hp_current'] = int(current_pokemon['hp_battle'])

                    if result == 1:
                        battle_outcome = 4
                        isdamage = False
                        isexit = True
                        break

                if current_pokemon['choice'] == 4:
                    print('choice 4')
                counter = counter + 1

            isdamage = False

        if bool(isexit):
            if battle_outcome == 0:
                try:
                    await client.delete_message(bot_message)
                except:
                    pass
                bot_message = await client.send_message(main_player,
                                                        "You successfully escaped.\n\n**Circle: Continue**")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            if battle_outcome == 1:
                try:
                    await client.delete_message(bot_message)
                except:
                    pass
                bot_message = await client.send_message(main_player,
                                                        "The wild %s fainted.\n\n**Circle: Continue**" %
                                                        pokemon_name_dict[on_field_hostile[0]['species_id']])
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)
                print(str(main_player), "beat", pokemon_name_dict[on_field_hostile[0]['species_id']])

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                experience_list = experience(in_party_friendly, on_field_hostile[0])
                trainer_experience = math.ceil(math.sqrt(sum(experience_list)) / 4)

                counter = 0
                for n in experience_list:
                    current_pokemon = in_party_friendly[counter]
                    if not current_pokemon:
                        counter = counter + 1
                    else:
                        if experience_list[counter] > 0:
                            bot_message = await client.send_message(main_player, "%s gained %s experience!" % (
                                pokemon_name_dict[current_pokemon['species_id']],
                                experience_list[counter]))
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                            await client.delete_message(bot_message)
                        current_pokemon['experience'] = current_pokemon[
                                                                               'experience'] + experience_list[counter]

                        while current_pokemon['experience_to_next'] <= current_pokemon['experience']:
                            current_pokemon, move = level_up(current_pokemon)
                            current_pokemon['leveled'] = 1

                            bot_message = await client.send_message(main_player, "%s grew to level %s!" % (
                                pokemon_name_dict[current_pokemon['species_id']],
                                current_pokemon['level']))
                            current_pokemon['hp_current'] = current_pokemon[
                                'hp_battle']
                            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                            await client.delete_message(bot_message)
                            if move != 0:
                                current_pokemon = await learn_move(move, in_party_friendly[
                                    counter], main_player)

                        current_pokemon["participant"] = 0
                        counter = counter + 1

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                await evolve(in_party_friendly, main_player)

            if battle_outcome == 2:

                counter = 0
                for i in in_party_friendly:
                    current_pokemon = in_party_friendly[counter]

                    if current_pokemon != 0:
                        current_pokemon['hp_current'] = current_pokemon[
                            'hp_battle']
                    counter = counter + 1

                try:
                    await client.delete_message(bot_message)
                except:
                    pass
                bot_message = await client.send_message(main_player,
                                                        "You have been sent to the nearest Pokemon Center.\n\n**Circle: Continue**")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            if battle_outcome == 4:

                try:
                    catch(seed_list, 4, str(main_player), main_player.id)
                except:
                    print("catch failed")
                try:
                    await client.delete_message(bot_message)
                except:
                    pass
                bot_message = await client.send_message(main_player,
                                                        "You caught a wild %s!\n\n**Circle: Continue**" %
                                                        pokemon_name_dict[on_field_hostile[0]['species_id']])
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            if trainer_experience > 0:
                bot_message = await client.send_message(main_player, "You gained %s trainer experience!" % (
                    trainer_experience))
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            player_experience_total = trainer_experience + player_experience

            while player_experience_to_next <= player_experience_total:
                player_level = player_level + 1
                player_experience_to_next = player_experience_list[player_level]
                bot_message = await client.send_message(main_player, "You reached level %s!" % (player_level))
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                await client.delete_message(bot_message)

            save_progress(in_party_friendly)
            save_outcome(battle_outcome, player_level, player_experience_total, player_experience_to_next, main_player)
            player_spawn_dict[main_player.id] = 0
            isbattle = False
            bot_message = await client.send_message(main_player, "Progress saved.")
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)

#ATTEMPT_CATCH~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def attempt_catch(target_pokemon, poke_ball, main_player):
    hp_current = target_pokemon['hp_current']
    hp_max = target_pokemon['hp_battle']
    rate = target_pokemon['catch_rate']
    ailment = target_pokemon['ailment']
    ball = poke_ball
    bonus_status = 1
    bonus_ball = 1

    if ailment == 2 or ailment == 3:
        bonus_status = 2
    elif ailment == 1 or ailment == 4 or ailment == 5:
        bonus_status = 1.5

    if ball == 'great_ball':
        bonus_ball = 1.5
    elif ball == 'ultra_ball':
        bonus_ball = 2

    a = ((((3*hp_max) - (2*hp_current))*rate*bonus_ball)/(3*hp_max))*bonus_ball

    bot_message = await client.send_message(main_player, "Toss!")
    time.sleep(1.25)
    catch_message = ''

    for i in range(0,4):
        b = int(65536/math.sqrt(math.sqrt(255/a)))
        if a > 255:
            b = 65537

        c = random.randint(1,65536)
        if c >= b:
            try:
                await client.delete_message(bot_message)
            except:
                pass
            bot_message = await client.send_message(main_player, "The wild %s broke free!" % pokemon_name_dict[target_pokemon['species_id']])
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            await client.delete_message(bot_message)
            return 0
        else:
            catch_message += 'shake... '
            bot_message = await client.edit_message(bot_message, "%s" % catch_message)
            time.sleep(1.25)

    bot_message = await client.edit_message(bot_message, "Caught!")
    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
    await client.delete_message(bot_message)
    return 1

            #LEARN_MOVE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def learn_move(move,current_pokemon,main_player):
    move_list = ['move1', 'move2', 'move3', 'move4']
    move_pp_list = ['move1_pp', 'move2_pp', 'move3_pp', 'move4_pp']
    counter = 0
    open_move = 0
    for n in move_list:
        if current_pokemon[move_list[counter]] == 0:
            open_move = counter + 1
            break
        counter = counter + 1

    if open_move > 0:
        current_pokemon[move_list[open_move - 1]] = move
        current_pokemon[move_pp_list[open_move - 1]] = move_pp_dict[move]
        bot_message = await client.send_message(main_player, "%s learned %s!" % (
            pokemon_name_dict[current_pokemon['species_id']], move_name_dict[move]))
        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
    else:
        islearn = True
        while bool(islearn):
            bot_message = await client.send_message(main_player,
                                                    "%s would like to learn %s! Which move would you like to replace?\n\n**1: %s **|-|** 2: %s **|-|** 3: %s **|-|** 4: %s **|-|** X: Skip Move**" % (
                                                        pokemon_name_dict[
                                                            current_pokemon['species_id']],
                                                        move_name_dict[move],
                                                        move_name_dict[current_pokemon["move1"]],
                                                        move_name_dict[current_pokemon["move2"]],
                                                        move_name_dict[current_pokemon["move3"]],
                                                        move_name_dict[current_pokemon["move4"]]))
            bot_reaction_one = await client.add_reaction(bot_message, emoji=emoji_dict['one'])
            bot_reaction_two = await client.add_reaction(bot_message, emoji=emoji_dict['two'])
            bot_reaction_three = await client.add_reaction(bot_message, emoji=emoji_dict['three'])
            bot_reaction_four = await client.add_reaction(bot_message, emoji=emoji_dict['four'])
            bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

            old_move = 0

            if player_response.reaction.emoji == emoji_dict['one']:
                old_move = current_pokemon["move1"]
                current_pokemon["move1"] = move
                current_pokemon["move1_pp"] = move_pp_dict[move]
            elif player_response.reaction.emoji == emoji_dict['two']:
                old_move = current_pokemon["move2"]
                current_pokemon["move2"] = move
                current_pokemon["move2_pp"] = move_pp_dict[move]
            elif player_response.reaction.emoji == emoji_dict['three']:
                old_move = current_pokemon["move3"]
                current_pokemon["move3"] = move
                current_pokemon["move3_pp"] = move_pp_dict[move]
            elif player_response.reaction.emoji == emoji_dict['four']:
                old_move = current_pokemon["move4"]
                current_pokemon["move4"] = move
                current_pokemon["move4_pp"] = move_pp_dict[move]
            else:
                await client.delete_message(bot_message)
                bot_message = await client.send_message(main_player, "Move skipped.")
                bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                islearn = False
                break

            await client.delete_message(bot_message)
            bot_message = await client.send_message(main_player, "%s forgot %s and learned %s!" % (
                pokemon_name_dict[current_pokemon['species_id']], move_name_dict[old_move],
                move_name_dict[move]))
            bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
            player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
            islearn = False
            break

    if bool(bot_message):
        await client.delete_message(bot_message)
    return(current_pokemon)

#EVOLVE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def evolve(temp_evolve, main_player):
    counter = 0
    for row in temp_evolve:
        current_pokemon = temp_evolve[counter]
        potential_evolutions = []
        if bool(current_pokemon) == False:
            counter = counter + 1
        else:
            if current_pokemon['leveled'] == 1:
                for row in evolves_from_list:
                    if row[1] == current_pokemon['species_id']:
                        potential_evolutions.append(row[0])

            current_time = time.strftime("%p")
            n = 0

            if bool(potential_evolutions) == True:
                for x in potential_evolutions:
                    current_pokemon = temp_evolve[counter]
                    row = evolution_level_dict[potential_evolutions[n]]
                    evolve = True
                    if bool(row[0]) == True:
                        if row[0] <= current_pokemon['level']:
                            temp = 1
                        else:
                            evolve = False
                    if bool(row[1]) == True:
                        if row[1] == 1 and current_pokemon['is_female'] == 0:
                            temp = 1
                        elif row[1] == 2 and current_pokemon['is_female'] == 1:
                            temp = 1
                        else:
                            evolve = False
                    if bool(row[2]) == True:
                        evolve = False
                    if bool(row[3]) == True:
                        if row[3] == current_pokemon['item']:
                            temp = 1
                        else:
                            evolve = False
                    if bool(row[4]) == True:
                        if row[4] == "day" and current_time == "AM":
                            temp = 1
                        if row[4] == "night" and current_time == "PM":
                            temp = 1
                        else:
                            evolve = False
                    if bool(row[5]) == True:
                        evolve = False
                    if bool(row[6]) == True:
                        evolve = False
                    if bool(row[7]) == True:
                        evolve = False
                    if bool(row[8]) == True:
                        evolve = False

                    if evolve == True:
                        break
                    if evolve == False:
                        n = n + 1

                if evolve == True:
                    new_species = potential_evolutions[n]
                    bot_message = await client.send_message(main_player,
                                                            "%s is evolving!\n\n**Circle: Continue** |-| **X: Cancel**" % (
                                                            pokemon_name_dict[current_pokemon['species_id']]))
                    bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                    bot_reaction_no = await client.add_reaction(bot_message, emoji=emoji_dict['no'])
                    player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

                    if player_response.reaction.emoji == emoji_dict['yes']:
                        await client.delete_message(bot_message)
                        bot_message = await client.send_message(main_player, "%s evolved into %s!" % (
                        pokemon_name_dict[current_pokemon['species_id']], pokemon_name_dict[new_species]))
                        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)
                        current_pokemon['species_id'] = new_species
                        await client.delete_message(bot_message)

                        #~~~~~~~~~~~~~~~UPDATE SPECIES~~~~~~~~~~~~~~~~~~~~~~

                        current_pokemon['hp'] = pokemon_base_stat_dict[current_pokemon['species_id']][0]
                        current_pokemon['atk'] = pokemon_base_stat_dict[current_pokemon['species_id']][1]
                        current_pokemon['def_'] = pokemon_base_stat_dict[current_pokemon['species_id']][2]
                        current_pokemon['spd'] = pokemon_base_stat_dict[current_pokemon['species_id']][3]
                        current_pokemon['spatk'] = pokemon_base_stat_dict[current_pokemon['species_id']][4]
                        current_pokemon['spdef'] = pokemon_base_stat_dict[current_pokemon['species_id']][5]

                        current_pokemon['hp_battle'] = int((2 * current_pokemon['hp'] + current_pokemon['hp_iv'] + int(current_pokemon['hp_ev'] / 4)) * current_pokemon['level'] / 100) + current_pokemon['level'] + 10
                        current_pokemon['atk_battle'] = int((int((2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon['level'] / 100) + 5) * current_pokemon['atk_nature'])
                        current_pokemon['def_battle'] = int((int((2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon['level'] / 100) + 5) * current_pokemon['atk_nature'])
                        current_pokemon['spd_battle'] = int((int((2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon['level'] / 100) + 5) * current_pokemon['atk_nature'])
                        current_pokemon['spatk_battle'] = int((int((2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon['level'] / 100) + 5) * current_pokemon['atk_nature'])
                        current_pokemon['spdef_battle'] = int((int((2 * current_pokemon['atk'] + current_pokemon['atk_iv'] + int(current_pokemon['atk_ev'] / 4)) * current_pokemon['level'] / 100) + 5) * current_pokemon['atk_nature'])

                        current_pokemon['hp_current'] = current_pokemon['hp_battle']

                        current_pokemon['ability'] = pokemon_ability_dict[current_pokemon['species_id']][current_pokemon['ability_seed']-1]

                        current_pokemon['type1'] = pokemon_type_dict[current_pokemon['species_id']][0]
                        current_pokemon['type2'] = pokemon_type_dict[current_pokemon['species_id']][1]

                        current_pokemon['height'] = pokemon_height_dict[current_pokemon['species_id']]
                        current_pokemon['height_total'] = round(current_pokemon['height']* current_pokemon['height_bonus'],2)
                        current_pokemon['weight'] = pokemon_weight_dict[current_pokemon['species_id']]
                        current_pokemon['weight_total'] = round(current_pokemon['weight']*current_pokemon['weight_bonus'],2)

                        current_pokemon['battle_ev1'] = pokemon_ev_dict[current_pokemon['species_id']][0]
                        current_pokemon['battle_ev2'] = pokemon_ev_dict[current_pokemon['species_id']][1]
                        current_pokemon['battle_ev3'] = pokemon_ev_dict[current_pokemon['species_id']][2]
                        current_pokemon['battle_ev4'] = pokemon_ev_dict[current_pokemon['species_id']][3]
                        current_pokemon['battle_ev5'] = pokemon_ev_dict[current_pokemon['species_id']][4]
                        current_pokemon['battle_ev6'] = pokemon_ev_dict[current_pokemon['species_id']][5]

                        query = (
                                'SELECT move_id FROM pokemon_moves WHERE pokemon_method_id = 1 AND version_id = %s AND pokemon_id = %s AND level = %s' % (
                            version_id, current_pokemon['species_id'], current_pokemon['level']))
                        cursor.execute(query)
                        temp_tuple = cursor.fetchall()

                        move = 0
                        for row in temp_tuple:
                            if not temp_tuple:
                                move = 0
                            else:
                                move = row[0]

                        if move != 0:
                            current_pokemon = await learn_move(move,current_pokemon,main_player)

                    elif player_response.reaction.emoji == emoji_dict['no']:
                        await client.delete_message(bot_message)
                        bot_message = await client.send_message(main_player,
                                                                "%s did not evolve.\n\n**Circle: Continue**" % (
                                                                pokemon_name_dict[current_pokemon['species_id']]))
                        bot_reaction_yes = await client.add_reaction(bot_message, emoji=emoji_dict['yes'])
                        player_response = await client.wait_for_reaction(message=bot_message, user=main_player)

            counter = counter + 1
