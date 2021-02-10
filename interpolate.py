from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import json

# pretend this url accept post requests with a single json CupSale object as the payload
# real requests here will fail
api_url = "https://api.rainforest.com/sales"

@dataclass
class ProductSales:
    # change in total number of cups sold
    delta: int = None
    # totol number of cups sold
    total: int = None
    date: datetime = None
    product_id: int = None

def json_dump(obj):
  if isinstance(obj, datetime):
      return (str(obj.year)+"-"+str(obj.month)+"-"+str(obj.day))
  return obj.__dict__

def interpolate_and_post(current: ProductSales, prev: ProductSales) -> None:
    #if there is nothing yet as previous in database or we get different products then we just return the current
    if prev is None or current.product_id != prev.product_id:
      prev = current
    date_diff = current.date - prev.date
    last_ttl = prev.total
    result_arr = []
    # if already same day just return the current 
    if date_diff.days <= 0:
      result_arr.append(current);
    else:
      delta_avg = 1
      delta_avg = int(current.delta / date_diff.days)
      remain_delta = current.delta - (delta_avg * date_diff.days)
      for i in range(date_diff.days):
        tmp_delta = delta_avg
        if remain_delta > 0:
          tmp_delta += 1
          remain_delta -= 1
        last_ttl += tmp_delta
        result_arr.append(ProductSales(delta=tmp_delta,total=last_ttl,date=prev.date + timedelta(i+1), product_id=current.product_id))
    #print(result_arr)
    # send the array as json post to the api url
    #json_str = {'CupSale': json.dumps(result_arr, default=json_dump, sort_keys=True)}
    #print(json_str) we can use json str but in request post must use attr data not json
    json_obj = []
    for tmp_prdct in result_arr:
      json_obj.append(json.dumps(tmp_prdct, default=json_dump))
    print(json_obj)
    try:
      r = requests.post(url = api_url, json = {'CupSale': json_obj}) 
    except Exception as err:
      print(f'Post Request Error Occurred: {err}')
    else:
      pass #to check the response print(r.text) 
    """
    Recieves the current ProductSales and last ProductSales we have in our database and posts new
    cup sales objects to our api.

    If there are missing days between current and prev, then we must do the following things:
    1. Create a ProductSales object for each missing day
    2. Split the current day's delta evenly between current day and all missing days.
       These values for delta should be integers and it is okay if some values are 1 above/below the others.
       The important thing is that the sum of delta values still adds up to the current CupSale object's original delta
    3. Set the total, date, and product_id fields to the correct values

    Then, post the current day's cup sales to 

    For example (note that the date field should be a datetime object, not a string):
    current = ProductSales(delta=11, total=21, date=today, product_id=9)
    prev = ProductSales(delta=5, total=10, date=2 days ago, product_id=9)

    These should be posted 
    ProductSales(delta=6, total=21, date=today, product_id=9)
    ProductSales(delta=5, total=15, date=1 day ago, product_id=9)
    6 + 5 adds up to 11, could have been in a different order so long as the totals for each day are correct
    """
    #pass



#check test example
#current = ProductSales(11, 21, datetime(2021, 2, 10), 9)
#prev = ProductSales(delta=5, total=10, date=datetime(2021, 2, 7), product_id=9);
#interpolate_and_post(current, prev);
