# Planet Subscription API

https://developers.planet.com/docs/subscriptions/

The following methods have been added: 
- `api.filters.build_delivery_subscription_request`
- `api.ClientV1.create_delivery_subscription`
- `api.ClientV1.cancel_delivery_subscription`
- `api.ClientV1.get_individual_delivery_subscription`
- `api.ClientV1.get_delivery_subscriptions`
- `api.ClientV1.get_delivery_subscription_results`

I used 'delivery subscriptions' instead of 'subscriptions' as there is already a 
'subscription' within planet namespace for analytic subscriptions. 

To use the subscriptions API, create a client. You'll need an API key, usually 
stored in `PL_API_KEY`. 
```
import os
from planet import api

client = api.ClientV1(os.environ['PL_API_KEY'])
```

To fetch a subscription by ID, use...
```
subscription_id = '56b4c00d-062e-4c5c-8d8c-860c789665ef'
subscription = client.get_individual_delivery_subscription(subscription_id)

print(subscription)
```

If the subscription can't be found, the API will raise the 
`planet.api.exceptions.MissingResource` exception.

To fetch all subscriptions that your user has access to, use...
```
subscriptions = client.get_delivery_subscriptions()

print(subscriptions)
```

To cancel a subscription with the given ID, use...
```
subscription_id = '56b4c00d-062e-4c5c-8d8c-860c789665ef'
result = client.cancel_delivery_subscription(subscription_id)

print(result.response.status_code)
```

This will return an empty response with a status code of 200 if the cancellation
is successful. You can only cancel a subscription that has a `status` of 'pending
' or 'running'. Otherwise the API will raise the `planet.api.exceptions.BadQuery`
exception.

To create a subscription, you'll need some more information.

Create a geometry with the coordinates you'd like to subscribe to...
```
aoi = [[[...], [...]]]
geom = {
    'coordinates': aoi,
    'type': 'MultiPolygon',
}
```

then define what types of products you'd like to receive...
```
item_types = [
    'PSOrthoTile'
]

asset_types = [
    "analytic",
    "analytic_xml",
    "udm",
    "udm2"
]
```

You can use `api.filters` the same way that you use them when creating a Quick Search. 
Let's use a geometry filter, along with a date range, and an instrument name. This will 
filter imagery that contains our AOI, from 2021-09-18 until 2021-09-21, for only PS2 and 
PS2.SD instrument types. 

Remember that currently, you can only create subscriptions starting in the future. There
is no back-fill functionality for the subscriptions API. The API will return an error
if the `gt` date is in the past.

```
filters = api.filters.and_filter(
    api.filters.geom_filter(geom, 'geometry'),
    api.filters.date_range('published', gt='2021-09-18', lte='2021-09-21'),
    api.filters.string_filter('instrument', 'PS2', 'PS2.SD')
)

tools = []
```

Tools are not required and the only 'tool' supported is image `clip`. We want 
all our returned imagery to be clipped to our AOI boundary, so let's define 
`tools` with the same AOI as our geometry filter...

```
    tools = [
        {
            'type': 'clip',
            'parameters': {
                'aoi': {
                    'coordinates': [[[...], [...]]],
                    'type': 'MultiPolygon' 
                }
            }
        }
    ]
```

Define your delivery location. The subscriptions API only supports cloud delivery.
We're using Google Cloud Storage...

``` 
delivery = {
    'type': 'google_cloud_storage',
    'parameters': {
        'bucket': '...',
        'credentials': '...'
    }
}
```

Give your subscription a name (not required to be unique but probably should be)
and wa-la! It's done. 

```
name = 'my-subscription-for-this-area'

request = api.filters.build_delivery_subscription_request(
    filters,
    name,
    item_types,
    asset_types,
    delivery, 
    tools
)

result = client.create_delivery_subscription(request)
```

The API will raise exceptions if your geometry is invalid, your AOI contains > 500 vertices, 
you have self-intersecting geometry, and such. So make sure you follow the rules! 

_Your cloud delivery credentials will be tested when you create a subscription. 
If they are invalid or do not have the required permissions, the API will raise
an exception. So if your request returns OK, you're in the clear._

After a few days (hopefully the next day) you should start receiving deliveries in your cloud 
storage. The follow the name/directory format of `storage-id/subscription-id/delivery-id/file-names...`

You can also view the delivered results of a given subscription id with...
```
subscription_id = '56b4c00d-062e-4c5c-8d8c-860c789665ef'
results = client.get_delivery_subscription_results(subscription_id)
```

You can also query for results with a `created` or `updated` or `completed` in 
a some date range by adding them as arguments.
