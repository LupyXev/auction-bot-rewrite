try:
    from hypixel_api_microservices_utils.others_objs import Timestamp, EstimatedPriceHist
    from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
except:
    from others_objs import Timestamp, EstimatedPriceHist
    from logs_obj import init_a_new_logger

from json import load, loads
from time import time

logger = init_a_new_logger("Hypixel data objs HAM")

class Tier:
    tier_dict = {}

    @classmethod
    def get_tier(cls, tier_id):
        if tier_id in cls.tier_dict:
            return cls.tier_dict[tier_id]
        else:
            return None

    def __init__(self, tier_id: str, coef: int):
        self.tier_id = tier_id
        self.coef = coef
        self.tier_dict[tier_id] = self

Tier("COMMON", 1)
Tier("UNCOMMON", 2)
Tier("RARE", 4)
Tier("EPIC", 10)
Tier("LEGENDARY", 20)
Tier("MYTHIC", 40)
Tier("SUPREME", 40) #considering supreme same as Mythic
Tier("SPECIAL", 100)
Tier("VERY_SPECIAL", 200)

class Reforge:
    reforge_dict = {}

    @classmethod
    def loader(cls, json_data):
        dict_data = loads(json_data)
        
        for reforge_id, raw_sold_history in dict_data.items():
            obj = cls.get_reforge(reforge_id)
            if obj is None: #we can't have a correct obj
                logger.error(f"reforge obj is None when loading basic items by loader : {reforge_id}, {raw_sold_history}")
            else:
                obj.estimated_price_sold_hist.raw_hist = raw_sold_history

    @classmethod
    def get_reforge(cls, reforge_id):
        if reforge_id in cls.reforge_dict:
            return cls.reforge_dict[reforge_id]
        else:
            #will create a new obj
            new_obj = Reforge(reforge_id)
            return new_obj

    def __init__(self, reforge_id: str, estimated_price_sold_hist: EstimatedPriceHist or None =None):
        self.reforge_id = reforge_id
        self.reforge_dict[reforge_id] = self

        if estimated_price_sold_hist is None:
            self.estimated_price_sold_hist = EstimatedPriceHist([])
        elif estimated_price_sold_hist is EstimatedPriceHist:
            self.estimated_price_sold_hist = estimated_price_sold_hist
        else:
            logger.error(f"estimated_price_sold_hist gave for __init__ bad type : {type(estimated_price_sold_hist)}")
        
    def for_save(self):
        return self.reforge_id, self.estimated_price_sold_hist.raw_data
    
    @classmethod
    def cleanup(cls):
        for reforge in cls.reforge_dict.values():
            reforge.estimated_price_sold_hist.cleanup()

class EnchantType:
    enchant_type_dict = {}

    @classmethod
    def loader(cls, json_data):
        dict_data = loads(json_data)
        del(json_data)
        for enchant_id, enchant_id_data in dict_data.items():
            enchant_type_obj = cls.get_enchant_type(enchant_id)

            for enchant_level, raw_sold_history in enchant_id_data.items():
                obj = enchant_type_obj.get_enchant(int(enchant_level))
                if obj is None: #we can't have a correct obj
                    logger.error(f"enchant obj is None when loading basic items by loader : {enchant_id}, {enchant_id_data}")
                else:
                    obj.estimated_price_sold_hist.raw_hist = raw_sold_history

    @classmethod
    def get_enchant_type(cls, enchant_type_id: str):
        if enchant_type_id in cls.enchant_type_dict:
            return cls.enchant_type_dict[enchant_type_id]
        else:
            #will create a new obj
            new_obj = EnchantType(enchant_type_id)
            return new_obj
    
    def __init__(self, enchant_type_id: str):
        self.enchant_type_id = enchant_type_id
        self.enchant_type_dict[enchant_type_id] = self
        self.enchant_by_levels_dict = {} #will store Enchant obj for each level
    
    def get_enchant(self, level: int):
        if level in self.enchant_by_levels_dict:
            return self.enchant_by_levels_dict[level]
        else:
            #will create a new obj
            new_obj = Enchant(level, self)
            self.enchant_by_levels_dict[level] = new_obj
            return new_obj
    
    @classmethod
    def cleanup(cls):
        for enchant_type in cls.enchant_type_dict.values():
            for enchant_level in enchant_type.enchant_by_levels_dict.values():
                enchant_level.estimated_price_sold_hist.cleanup()

class Enchant:
    def __init__(self, level: int, enchant_type: EnchantType, estimated_price_sold_hist: EstimatedPriceHist or None =None):
        self.level = level
        self.basic = enchant_type

        if estimated_price_sold_hist is None:
            self.estimated_price_sold_hist = EstimatedPriceHist([])
        else:
            self.estimated_price_sold_hist = estimated_price_sold_hist
        
    def for_save(self):
        return (self.basic.enchant_type_id, self.level), self.estimated_price_sold_hist.raw_data

class RuneType:
    rune_type_dict = {}

    @classmethod
    def loader(cls, json_data):
        dict_data = loads(json_data)
        del(json_data)
        for rune_id, rune_id_data in dict_data.items():
            rune_type_obj = cls.get_rune_type(rune_id)

            for rune_level, raw_sold_history in rune_id_data.items():
                obj = rune_type_obj.get_rune(int(rune_level))
                if obj is None: #we can't have a correct obj
                    logger.error(f"enchant obj is None when loading basic items by loader : {rune_id}, {rune_id_data}")
                else:
                    obj.estimated_price_sold_hist.raw_hist = raw_sold_history

    @classmethod
    def get_rune_type(cls, rune_type_id: str):
        if rune_type_id in cls.rune_type_dict:
            return cls.rune_type_dict[rune_type_id]
        else:
            #will create a new obj
            new_obj = RuneType(rune_type_id)
            return new_obj
    
    def __init__(self, rune_type_id: str):
        self.rune_type_id = rune_type_id
        self.rune_type_dict[rune_type_id] = self

        self.rune_by_levels_dict = {} #will store Rune objs
    
    def get_rune(self, rune_level: int):
        if rune_level in self.rune_by_levels_dict:
            return self.rune_by_levels_dict[rune_level]
        else:
            #will create a new obj
            new_obj = Rune(rune_level, self)
            self.rune_by_levels_dict[rune_level] = new_obj
            return new_obj
    
    @classmethod
    def cleanup(cls):
        for rune_type in cls.rune_type_dict.values():
            for rune_level in rune_type.rune_by_levels_dict.values():
                rune_level.estimated_price_sold_hist.cleanup()

class Rune:
    def __init__(self, level: int, rune_type: RuneType, estimated_price_sold_hist: EstimatedPriceHist or None =None):
        self.level = level
        self.basic = rune_type

        if estimated_price_sold_hist is None:
            self.estimated_price_sold_hist = EstimatedPriceHist([])
        else:
            self.estimated_price_sold_hist = estimated_price_sold_hist
        
    def for_save(self):
        return (self.basic.rune_type_id, self.level), self.estimated_price_sold_hist.raw_data

#TODO manage additional attrs

class AdditionalAttribute:
    def __init__(self, value: any, raw_sold_hist:list=[]):
        self.value = value
        self.estimated_price_sold_hist = EstimatedPriceHist(raw_sold_hist)

class AdditionalAttributeUnspecialized(AdditionalAttribute):
    ATTRIBUTES_NAME_FOR_THIS_CLASS = ("hot_potato_count", "hotPotatoBonus", "skin", "talisman_enrichment",
    "art_of_war_count", "farming_for_dummies_count")
    """ATTRIBUTES_WITH_STEP_VALUES = {}

    obj_by_attributes_type_and_value = {} #ex: "skin" : {"Shimmer": obj} for a shimmer skin

    @classmethod
    def get_additional_attr(cls, attr_name: str, attr_value: any):
        if attr_name in cls.obj_by_attributes_type_index_and_value and attr_value in cls.obj_by_attributes_type_index_and_value[attr_name]:
            return cls.obj_by_attributes_type_index_and_value[attr_name][attr_value]
        else:
            return None

    def __init__(self, attr_name:str, value: any, raw_sold_hist:list=[]):
        #we must to take special value for attributes which can take big int values (like kills)
        AdditionalAttribute.__init__(self, value, raw_sold_hist=raw_sold_hist)
        try:
            self.attr_index = self.ATTRIBUTES_NAME_FOR_THIS_CLASS.index(attr_name)
        except:
            logger.error(f"{attr_name} not in attr types of AdditionalAttributeUnspecialized")
        self.obj_by_attributes_type_and_value[attr_name][attr_value] = self"""

class AdditionalAttributeSpecialized(AdditionalAttribute):
    ATTRIBUTES_NAME_FOR_THIS_CLASS = ("spider_kills", "zombie_kills", "wood_singularity_count", "drill_part_upgrade_module", "drill_fuel", 
    "stored_drill_fuel", "drill_part_fuel_tank", "drill_part_engine", "ability_scroll", "power_ability_scroll",
    "raider_kills", "eman_kills", "item_durability", "bow_kills", "pickonimbus_durability", "sword_kills", "necromancer_souls")

class BasicItem:
    basicitem_dict = {} #id: {Tier: {dungeon_level: BasicItem}}
    ALIAS = {}
    with open("data/alias.json", "r") as f:
        ALIAS = dict(load(f))
    
    DUNGEON_ENCHANTED_ITEMS = {}
    with open("data/dungeon-enchanted-items.json", "r") as f:
        DUNGEON_ENCHANTED_ITEMS = tuple(load(f))
    
    ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD = {}#id: name
    ITEM_IDS_NOT_IN_ALIAS_SENT_TO_DISCORD = []

    @classmethod
    def loader(cls, json_data):
        dict_data = loads(json_data)
        del(json_data)
        for item_id, item_id_data in dict_data.items():
            for tier_id, tier_id_data in item_id_data.items():
                for dungeon_level_str, raw_sold_history in tier_id_data.items():
                    obj = cls.get_basicitem(item_id=item_id, 
                        tier=Tier.get_tier(tier_id),
                        dungeon_lvl=int(dungeon_level_str))
                    if obj is None: #we can't have a correct obj
                        logger.error(f"basic item obj is None when loading basic items by loader : {item_id}, {item_id_data}")
                    else:
                        obj.estimated_price_sold_hist.raw_hist = raw_sold_history

    @classmethod
    def get_basicitem(cls, item_id: str, tier: Tier, dungeon_lvl: int):
        if item_id in cls.basicitem_dict and tier in cls.basicitem_dict[item_id] and dungeon_lvl in cls.basicitem_dict[item_id][tier]:
            return cls.basicitem_dict[item_id][tier][dungeon_lvl]
        else:
            if item_id in cls.ALIAS:
                new_obj = BasicItem(item_id, tier, dungeon_lvl)
                return new_obj
            else:
                if item_id not in cls.ITEM_IDS_NOT_IN_ALIAS_SENT_TO_DISCORD and item_id not in cls.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD: #not already alerted or to alert
                    cls.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD[item_id] = None
                    #logger.debug(f"item {item_id} not in alias, skipped")
                return None
    
    def __init__(self, item_id: str, tier: Tier, dungeon_level: int, estimated_price_sold_hist: EstimatedPriceHist or None =None):
        if item_id not in self.ALIAS:
            logger.error(f"{item_id} not in alias when init BasicItem obj")
            if item_id not in self.ITEM_IDS_NOT_IN_ALIAS_SENT_TO_DISCORD and item_id not in self.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD:
                self.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD[item_id] = None
            return
        self.item_id = item_id

        alias_data = self.ALIAS[item_id]
        self.item_name = alias_data[0]
        self.first_detection = alias_data[2]
        self.complex = alias_data[1]

        if item_id in self.DUNGEON_ENCHANTED_ITEMS:
            self.can_be_drop_enchanted = True
        else:
            self.can_be_drop_enchanted = False
        
        self.tier = tier
        if tier is None:
            logger.error(f"The item's tier is None when init a BasicItem : {item_id}")

        self.dungeon_level = dungeon_level

        if self.item_id not in self.basicitem_dict:
            self.basicitem_dict[self.item_id] = {}
        if self.tier not in self.basicitem_dict[self.item_id]:
            self.basicitem_dict[self.item_id][self.tier] = {}
        
        self.basicitem_dict[self.item_id][self.tier][self.dungeon_level] = self

        if estimated_price_sold_hist is None:
            self.estimated_price_sold_hist = EstimatedPriceHist([])
        else:
            self.estimated_price_sold_hist = estimated_price_sold_hist
        
        #for less alerting new items
        self.coef_for_alerting_this_item = self.ALIAS[item_id][2]
        try:
            days_since_add = (time() - self.ALIAS[item_id][2]) / 3600 / 24
            function_result = -1.0 * days_since_add**2 + 100.0 #f(x)=-x^2+100

            coef = function_result / 10
            if coef < 1: #if the coef advise to reduce the min_profitability
                coef = 1
            self.coef_for_alerting_this_item = coef
        except:
            logger.error(f"error with coef for alerting this item with item id {item_id}")
            self.coef_for_alerting_this_item = 1
    
    def get_lowests_bins(self, number_of_lowests_bins=3):
        lowests = [None] * number_of_lowests_bins
        for auction in tuple(Auction.auction_uuid_to_obj.values()):
            if auction.item.basic.item_id == self.item_id:
                price = auction.starting_bid
                for lowest_index in range(number_of_lowests_bins):
                    if lowests[lowest_index] is None or price < lowests[lowest_index]:
                        lowests[lowest_index] = price
                        break #to avoid an auction to be in multiple lowests bins
        return lowests
        
    def for_save(self):
        return (self.item_id, self.tier.tier_id, self.dungeon_level), self.estimated_price_sold_hist.raw_data

    @classmethod
    def cleanup(cls):
        for item_id_dict in cls.basicitem_dict.values():
            for tier_dict in item_id_dict.values():
                for basic_item in tier_dict.values():
                    basic_item.estimated_price_sold_hist.cleanup()

class Estimation:
    def __init__(self, linked_item):
        self.linked_item = linked_item

        self.complex_linked_item = BasicItem.ALIAS[linked_item.basic.item_id][1]

        self.already_estimated = False
        self.fully_successfully_estimated = False
        self.total = None

        self.enchants = {} #Enchant: [estimation, [Quartile1, Quartile2]]
        self.runes = {} #Rune: [estimation, [Quartile1, Quartile2]]
        #we do not init item_without_attributes, reforge

        self.trust_rate = None
    
    def estimate_for_sold_item(self):
        if self.complex_linked_item:
            #TODO handle complex items
            return 999, None, None

        def estimate_one_attr(estimated_price_sold_hist, total, missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght):
            #for sold item, so 1 item in sold hist is enough and we're using a 2h intervall
            attr_median, cur_sold_hist_lenght = estimated_price_sold_hist.get_median(EstimatedPriceHist.INTERVALL_USED_FOR_SOLD_ITEMS, return_sold_hist_lenght_used=True)
            
            if cur_sold_hist_lenght < sold_hist_obj_of_attr_with_less_sold_lenght[1]:
                if sold_hist_obj_of_attr_with_less_sold_lenght[2] is not None:
                    total += sold_hist_obj_of_attr_with_less_sold_lenght[2]
                
                sold_hist_obj_of_attr_with_less_sold_lenght = [estimated_price_sold_hist, cur_sold_hist_lenght, attr_median]
                attr_median = 0 #to disable adding to total

            if attr_median is None: #haven't correctly estimated
                return missing_prices_number + 1, sold_hist_obj_of_attr_with_less_sold_lenght, total
            else:
                total += attr_median
                return missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght, total #correctly estimated
            
        missing_prices_number = 0
        total = 0

        sold_hist_obj_of_attr_with_less_sold_lenght = [None, 99999999, None] #sold_hist_obj, lenght, value for adding to total if there is another attr with less sold lenght

        #estimate the item
        missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght, total = estimate_one_attr(self.linked_item.basic.estimated_price_sold_hist, total, missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght)
        
        if self.linked_item.reforge is not None:
            #estimate the reforge
            missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght, total = estimate_one_attr(self.linked_item.reforge.estimated_price_sold_hist, total, missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght)

        for enchant in self.linked_item.enchants:
            #estimate the enchant
            missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght, total = estimate_one_attr(enchant.estimated_price_sold_hist, total, missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght)

        for rune in self.linked_item.runes:
            #estimate the rune
            missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght, total = estimate_one_attr(rune.estimated_price_sold_hist, total, missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght)
        
        #end
        return missing_prices_number, sold_hist_obj_of_attr_with_less_sold_lenght[0], total
    
    def estimate(self):
        if self.complex_linked_item:
            #TODO handle complex items
            return None, 0
        
        def estimate_one_attr(estimated_price_sold_hist, intervalls_used, total, price_and_quartiles):
            attr, intervall, smart_hist = estimated_price_sold_hist.get_smart_median()
            sold_amount_used = len(smart_hist)

            quartiles = (None, None)
            if sold_amount_used >= 2: #sold_amount_used = len(smart_hist)
                quartile_lenght = sold_amount_used / 4
                quartile_1_index, quartile_3_index = quartile_lenght, quartile_lenght * 3

                def get_quartile(quartile_index, smart_hist):
                    
                    beyond_decimal_point = quartile_index*10 % 10 / 10
                    quartile_index_without_decimal = int(quartile_index - beyond_decimal_point)
                    return (smart_hist[quartile_index_without_decimal][0] * beyond_decimal_point + smart_hist[quartile_index_without_decimal + 1][0] * (1 - beyond_decimal_point)) / 2

                quartiles = (get_quartile(quartile_1_index, smart_hist), get_quartile(quartile_3_index, smart_hist))

            del(smart_hist)
            if attr is None: #haven't correctly estimated
                #(estimation, intervall_used, (Quartile1, Quartile2))
                return False, (attr, Timestamp(time() - intervall), quartiles, sold_amount_used), total
            else:
                if intervall < intervalls_used[0]:
                    intervalls_used[0] = intervall
                if intervall > intervalls_used[1]:
                    intervalls_used[1] = intervall
                
                total += attr
                price_and_quartiles.append((attr, quartiles))
                #(estimation, intervall_used, (Quartile1, Quartile2))
                return True, (attr, Timestamp(time() - intervall), quartiles, sold_amount_used), total #correctly estimated

        currently_correctly_estimated = True
        total = 0
        intervalls_used = [999999999999999, 0] #min, max
        price_and_quartiles = [] #price, quartiles

        #estimate the item 
        currently_correctly_estimated, self.item_only, total = estimate_one_attr(self.linked_item.basic.estimated_price_sold_hist, intervalls_used, total, price_and_quartiles)
        
        if self.linked_item.reforge is not None:
            #estimate the reforge
            currently_correctly_estimated, self.reforge, total = estimate_one_attr(self.linked_item.reforge.estimated_price_sold_hist, intervalls_used, total, price_and_quartiles)

        for enchant in self.linked_item.enchants:
            #estimate the enchant
            currently_correctly_estimated, self.enchants[enchant], total = estimate_one_attr(enchant.estimated_price_sold_hist, intervalls_used, total, price_and_quartiles)

        for rune in self.linked_item.runes:
            #estimate the rune
            currently_correctly_estimated, self.runes[rune], total = estimate_one_attr(rune.estimated_price_sold_hist, intervalls_used, total, price_and_quartiles)
        
        #end
        if currently_correctly_estimated:
            self.total = total
        self.fully_successfully_estimated = currently_correctly_estimated
        self.already_estimated = True

        self.intervalls_used = intervalls_used

        if currently_correctly_estimated:
            #calculate the quartiles trust rate
            MIN_PRICE_PERCENTAGE_OF_AN_ATTR_TO_BE_IN_TRUST_RATE = 0.1
            quartiles_trust = 1 #bc we multiply quartiles between them
            for price, quartiles in price_and_quartiles:
                if price / total >= MIN_PRICE_PERCENTAGE_OF_AN_ATTR_TO_BE_IN_TRUST_RATE and quartiles[0] is not None:
                    this_attr_quartiles_trust = (quartiles[0] / quartiles[1])
                    if this_attr_quartiles_trust < 0.1: this_attr_quartiles_trust = 0.1

                    quartiles_trust *= this_attr_quartiles_trust
            
            return total, quartiles_trust
        else:
            return None, 0 #quartiles trust rate is 0

class Item:
    def __init__(self, item_name: str, basicitem: BasicItem, reforge: Reforge or None, enchants: Enchant or tuple or list, runes: Rune or tuple or list, additional_data: tuple=()):
        self.item_name = item_name
        self.basic = basicitem
        self.reforge = reforge

        if type(enchants) is Enchant:
            enchants = [enchants]
        self.enchants = tuple(enchants) #will always be stored in a tuple, void tuple if no enchants

        if type(runes) is Rune:
            runes = [runes]
        self.runes = tuple(runes) #will always be stored in a tuple, void tuple if no runes

        self.estimation = Estimation(self)

class Auction:
    auction_uuid_to_obj = {}
    MIN_ABSOLUTE_PROFITABILITY_FOR_ALERTING = 200_000
    MIN_PROFITABILITY_PERCENTAGE_FOR_ALERTING = 0.1 #as coefficient, not % (ex: 20% = 0.2)

    def __init__(self, uuid: str, seller_uuid: str, start: Timestamp or int, end: Timestamp or int, item_count: int, item: Item, starting_bid: int):
        self.uuid = uuid
        self.seller_uuid = seller_uuid

        if type(start) is Timestamp:
            self.start = start
        elif type(start) is int:
            self.start = Timestamp(start)
        else:
            logger.error("bad start type")
        
        if type(end) is Timestamp:
            self.end = end
        elif type(end) is int:
            self.end = Timestamp(end)
        else:
            logger.error("bad end type")
        
        self.item_count = item_count
        self.item = item
        self.starting_bid = starting_bid
        self.starting_bid_cost_per_item = self.starting_bid / self.item_count

        #we do not calculate profitability so there's no profitability attribute

        #adding the auction to the dict
        self.auction_uuid_to_obj[uuid] = self
    
    def calculate_profitability(self, cur_run):#returns must_be_alerted, absolute profitability, percentage profitability
        value, quartiles_trust = self.item.estimation.estimate()
        if value is None: #couldn't estimate propely
            return False, None, None, None
        #else not needed because of return
        absolute_profitability = value - self.starting_bid
        percentage_profitability = value / self.starting_bid - 1

        if cur_run != 0:
            lowest_bins = self.item.basic.get_lowests_bins()
            lowest_bins_trust = 0
            lowest_bins_not_none = 0
            for lowest_bin in lowest_bins:
                if not lowest_bin is None:
                    lowest_bins_trust += lowest_bin
                    lowest_bins_not_none += 1

            missing_lowest_bins_penalty = (len(lowest_bins) - lowest_bins_not_none) / 4

            lowest_bins_trust /= lowest_bins_not_none + missing_lowest_bins_penalty #the mean plus the penalty
            lowest_bins_trust /= self.starting_bid_cost_per_item #divided by the price
            lowest_bins_trust = lowest_bins_trust ** 3 #to increase the gap, the signifiance of lowest bins cheaper than the item's price
            if lowest_bins_trust > 1: lowest_bins_trust = 1
        else:
            lowest_bins_trust = 0.4 #40% of trust
        trust = quartiles_trust / 2 + lowest_bins_trust / 2

        if absolute_profitability >= self.MIN_ABSOLUTE_PROFITABILITY_FOR_ALERTING and percentage_profitability >= self.item.basic.coef_for_alerting_this_item * self.MIN_PROFITABILITY_PERCENTAGE_FOR_ALERTING:
            return True, absolute_profitability, percentage_profitability, trust
        #else not needed because of return
        return False, absolute_profitability, percentage_profitability, trust

class SoldAuction:
    #must be SOLD, NOT cancelled or expired
    def __init__(self, linked_auction: Auction):
        self.linked_auction = linked_auction

    def sold(self, price: int):
        if self.linked_auction.item.basic.item_id in EstimatedPriceHist.BLACKLISTED_SOLD_STORAGE_ITEMS:
            #we won't store the sold hist or calculate the price
            return
        
        #we'll calculate the item's price or its attributes
        estimation = self.linked_auction.item.estimation

        missing_prices_number, sold_hist_obj_of_attr_with_less_sold, total_attrs_hist = estimation.estimate_for_sold_item() #will estimate (again but in sold mode)

        if self.linked_auction.uuid in Auction.auction_uuid_to_obj:
            Auction.auction_uuid_to_obj.pop(self.linked_auction.uuid) #delete the auction obj

        if missing_prices_number > 1: #more than 1 missing attr's price
            return #we can't determinate a price

        #we're going to determinate the price of the less hist data attr, even if it has a 0 data lenght
        sold_hist_obj_of_attr_with_less_sold.add(price - total_attrs_hist, Timestamp())

logger.debug("init ended")