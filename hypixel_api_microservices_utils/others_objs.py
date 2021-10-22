from datetime import datetime
from time import time

class Timestamp:
    def __init__(self, value=None):
        if value is None:
            value = time()
        if value > 9000000000:
            #the value is in milliseconds
            value /= 1000
        self.value = round(value, 2)
    
    def to_str(self):
        return str(datetime.fromtimestamp(self.value)) + " UTC 0"

class EstimatedPriceHist:
    JUMP_INTERVALL_FOR_SMART_MEDIAN = 60*15 #15 min, better if this is a MAX_INTERVALL's multiple
    MAX_INTERVALL_FOR_SMART_MEDIAN = 60*60*2 #2h
    SOLD_LENGHT_ADMISSIBLE_FOR_SMART_MEDIAN = 9 #when there is 9 or more solds for a smart intervall, it uses it

    INTERVALL_USED_FOR_SOLD_ITEMS = MAX_INTERVALL_FOR_SMART_MEDIAN

    BLACKLISTED_SOLD_STORAGE_ITEMS = ("SPOOKY_PIE", "NEW_YEAR_CAKE") #item which we won't store their sold hist

    INTERVALL_KEPT_FOR_SOLD_HISTORY = 3600*24

    @classmethod
    def find_median(cls, raw_data, return_timestamp=False):
        if len(raw_data) < 1:
            if return_timestamp: return None, None
            return None
        low_half_len = len(raw_data) // 2 - 1 #- 1 because we'll use it for an index
        if len(raw_data) % 2 == 0: #the median is between 2 values
            price_median = (raw_data[low_half_len][0] + raw_data[low_half_len + 1][0]) / 2
            timestamp_median = Timestamp((raw_data[low_half_len][1] + raw_data[low_half_len + 1][1]) / 2)

            if return_timestamp: return price_median, timestamp_median
            return price_median

        else:
            if return_timestamp: return raw_data[low_half_len] #will also be a tuple
            return raw_data[low_half_len][0] #takes only the value, not timestamp

    #the raw hist must be : list(tuple(price: int, timestamp: int)) and organised in augmenting order
    def __init__(self, raw_hist: list):
        self.raw_hist = raw_hist
    
    def add(self, price: int, timestamp: Timestamp):
        hist_index = 0
        for hist in self.raw_hist:
            if hist[0] > price:
                break
            else:
                hist_index += 1
        #we insert for an organisation in augmented order
        self.raw_hist.insert(hist_index, (price, timestamp.value))
    
    def get_for_an_older_timestamp(self, older_timestamp_kept: int or Timestamp, convert_to_tuple=True):
        if type(older_timestamp_kept) is Timestamp:
            older_timestamp_kept = older_timestamp_kept.value
        
        filtered_raw_hist = []
        for hist in self.raw_hist:
            if hist[1] >= older_timestamp_kept:
                filtered_raw_hist.append(hist)
        if convert_to_tuple:
            return tuple(filtered_raw_hist)
        else:
            return filtered_raw_hist
    
    def get_for_an_intervall(self, intervall: int, convert_to_tuple=True):
        older_timestamp = time() - intervall
        return self.get_for_an_older_timestamp(older_timestamp, convert_to_tuple)

    def get_median(self, intervall_used: int or None, return_sold_hist_lenght_used=False):        
        if intervall_used is None:
            #we're using the full data
            if return_sold_hist_lenght_used:
                return self.find_median(self.raw_hist), len(self.raw_hist)
            return self.find_median(self.raw_hist) #return value, Timestamp
        else:
            filtered_raw_hist = self.get_for_an_intervall(intervall_used)
            if return_sold_hist_lenght_used:
                return self.find_median(filtered_raw_hist), len(filtered_raw_hist)
            return self.find_median(filtered_raw_hist) #return value, Timestamp
    
    def get_smart_median(self):
        #we will use dichotomy to find the smart intervall
        smarter_sold_hist = ()
        smarter_intervall = self.MAX_INTERVALL_FOR_SMART_MEDIAN #will be a max in logic processing

        old_current_intervall = self.JUMP_INTERVALL_FOR_SMART_MEDIAN * 10 #whatever number when the diff between old and current intervall > JUMP_INTERVALL
        current_intervall = self.MAX_INTERVALL_FOR_SMART_MEDIAN / 2
        sold_hist_for_current_intervall = self.get_for_an_intervall(current_intervall)

        while abs(old_current_intervall - current_intervall) >= self.JUMP_INTERVALL_FOR_SMART_MEDIAN:
            #print(current_intervall, len(sold_hist_for_current_intervall))
            if len(sold_hist_for_current_intervall) >= self.SOLD_LENGHT_ADMISSIBLE_FOR_SMART_MEDIAN: #if we have more or same as the better lenght
                smarter_sold_hist = sold_hist_for_current_intervall
                smarter_intervall = current_intervall

                old_current_intervall = current_intervall
                current_intervall /= 2
            else:
                old_current_intervall = current_intervall
                current_intervall = (current_intervall + smarter_intervall) / 2 #the mean
            
            sold_hist_for_current_intervall = self.get_for_an_intervall(current_intervall)
        
        if len(smarter_sold_hist) > 0:
            return self.find_median(smarter_sold_hist), smarter_intervall, smarter_sold_hist
        else:
            return None, smarter_intervall, smarter_sold_hist #we haven't found a smart median

    def cleanup(self):
        self.raw_hist = self.get_for_an_intervall(self.INTERVALL_KEPT_FOR_SOLD_HISTORY, False)

    """@classmethod
    def get_smart_median_for_multiple_hists(cls, estimated_price_sold_hist_objs: tuple):
        #better if the first obj contains the lowest sold amount
        working_for_all = False
        obj_to_median = {}
        obj_to_median[estimated_price_sold_hist_objs[0]], current_intervall = estimated_price_sold_hist_objs[0].get_smart_median()

        while not working_for_all and current_intervall <= cls.MAX_INTERVALL_FOR_SMART_MEDIAN:
            working_for_all = True #will be set to False if any obj doesn't work
            for sold_hist_obj in estimated_price_sold_hist_objs:
                cur_median, cur_lenght = sold_hist_obj.get_median(current_intervall, return_sold_hist_lenght_used=True)
                if cur_lenght >= cls.MAX_INTERVALL_FOR_SMART_MEDIAN:
                    obj_to_median[sold_hist_obj] = cur_median
                else:
                    working_for_all = False
                    obj_to_median[sold_hist_obj], current_intervall = sold_hist_obj.get_smart_median()
                    break"""

"""# Smart median test
from random import randint
a = EstimatedPriceHist([(randint(0, 2200)-200, Timestamp(randint(round(time()-15_000), round(time())))) for i in range(200)])
print(a.raw_hist)
sm = a.get_smart_median()
print(sm)
print(len(sm[3]))
"""

class GlobalHAM:
    run = True
    current_events = []
    temp_disabled_items = {} #{"id": {"expiring_timestamp": 56164078}}