import os
from pprint import pprint as print

from planet import api

client = api.ClientV1(os.environ['PL_API_KEY'])

subscription_id = '61977bc7-0683-4ed4-b183-b420041f0650'

subscription = client.get_individual_delivery_subscription(subscription_id)

print(subscription.get())
