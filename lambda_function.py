import boto3
import json
from boto3.dynamodb.conditions import Key
import logging

# API payload
# CREATE
## Request Payload
#   "body": {
#     "category": "test",
#     "sub_category": "test",
#     "type": "test",
#     "bone_in": "test",
#     "prep": "test",
#     "freshness": "test",
#     "amount": "test",
#     "cooking_method": "test",
#     "liquid_amount": "test",
#     "pressure_level": "test",
#     "estimated_pressure_build_time": "test",
#     "temperature": "test",
#     "cook_time": "test",
#     "photo": "test"
#   }

# GET
## Request Payload
#   "queryStringParameters": {
#     "category": "test",
#     "sub_category": "",
#     "type": "",
#     "bone_in": "",
#     "prep": "",
#     "freshness": "",
#     "amount": "",
#     "cooking_method": ""
#     }

## Response
#     {
#       "search_params": {
#         "category": [],
#         "sub_category": [],
#         "type": [],
#         "bone_in": [],
#         "prep": "[],
#         "freshness": [],
#         "amount": [],
#         "cooking_method": [],        
#       },
#       "results": {
#           [
              
#             {
#                 "liquid_amount": "test",
#                 "pressure_level": "test",
#                 "estimated_pressure_build_time": "test",
#                 "temperature": "test",
#                 "cook_time": "test",
#                 "photo": "test"
#             }
#           ]
#       }
#    }


# Setting a constant number of categories for sample
# Typically this can come from a cache data source for faster loading
# Categories can be updated based on need
CATEGORIES = ['Grains', 'Legumes', 'Meat', 'Poultry', 'Vegetables']
SEARCH_PARAMS_TREE = {
    1: 'category',
    2: 'sub_category',
    3: 'type',
    4: 'bone_in',
    5: 'prep',
    6: 'freshness',
    7: 'amount',
    8: 'cooking_method'
}

dynamo = boto3.resource('dynamodb').Table('cooking_presets')

def lambda_handler(event, context):
    operation = event['httpMethod']

    if operation == 'POST':
        return _create_preset(event['body'])
    elif operation == 'GET':
        return _search_preset(event['queryStringParameters'])
    else:
        raise ValueError('Unrecognized operation "{}"'.format(operation))
        
def _search_preset(search_criteria):
    # Category is required to get at least one item
    try:
        if not search_criteria:
            # Default category to Grains
            search_criteria = {}
            search_criteria['category'] = 'Grains'
        
        partition_key = search_criteria['category']
        sort_key = _build_ingredients_key(search_criteria)
        
        
        if sort_key:
            ingredients_results = dynamo.query(
                KeyConditionExpression=
                    Key('category').eq(partition_key) & Key('ingredients').begins_with(f"SI#{sort_key}")
                )['Items']
            preset_results = dynamo.query(
                KeyConditionExpression=
                    Key('category').eq(partition_key) & Key('ingredients').begins_with(sort_key)
                )['Items']
        else:
            ingredients_results = dynamo.query(
                KeyConditionExpression=
                    Key('category').eq(partition_key) & Key('ingredients').begins_with(f"SI#")
                )['Items']
            preset_results = dynamo.query(
                KeyConditionExpression=
                    Key('category').eq(partition_key) & Key('ingredients').Not.begins_with(f"SI#")
                )['Items']
    
        search_results = _build_search_payload(ingredients_results, len(search_criteria))
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'search_params': search_results, 'results': preset_results[:20]}),
            "isBase64Encoded": False
        }
    except Exception as e:
        logging.error(e)
        return {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'message': 'Cooking preset search unsuccessful'}),
            "isBase64Encoded": False
        }
    
def _create_preset(preset_criteria):
    try:
        data = _formatted_payload(preset_criteria)['data']
        search_index = _formatted_payload(preset_criteria)['search_index']
        # Save the data
        dynamo.put_item(Item=data)
        # Save the search index
        dynamo.put_item(Item=search_index)
        return {
            "statusCode": 201,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'message': 'Cooking preset creation successful'}),
            "isBase64Encoded": False
        }
    except Exception as e:
        logging.error(e)
        return {
            "statusCode": 422,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            "body": json.dumps({'message': 'Cooking preset creation unsuccessful'}),
            "isBase64Encoded": False
        }
        
        
def _formatted_payload(payload):
    payload['ingredients'] = f"{payload['category']}#{payload['sub_category']}#{payload['type']}#{payload['bone_in']}#{payload['prep']}#{payload['freshness']}#{payload['amount']}#{payload['cooking_method']}"
    return {'data': payload, 'search_index': {'category': payload['category'], 'ingredients': f"SI#{payload['ingredients']}"}}
    

# Builds the Sort Key consisting of the ingredients other than category
def _build_ingredients_key(ingredients_search):
    sort_key = ""
    for v in SEARCH_PARAMS_TREE.values():
        if v in ingredients_search.keys():
            sort_key = f"{sort_key}{ingredients_search[v]}#"
    # Last # in key is not required
    return sort_key[:-1]


def _build_search_payload(search_indexes, search_tree_depth):
    search_params = {
        'category': CATEGORIES,
        'sub_category': [],
        'type': [],
        'bone_in': [],
        'prep': [],
        'freshness': [],
        'amount': [],
        'cooking_method': []         
    }

    for idx in search_indexes:
        max_depth = max(SEARCH_PARAMS_TREE.keys())
        depth = max_depth if search_tree_depth == max_depth else search_tree_depth + 1
        ingredients = idx['ingredients'].split('#')
        while(depth > 1):
            search_params[SEARCH_PARAMS_TREE[depth]].append(ingredients[depth])
            depth = depth - 1
        
    response_payload = {
        "search_params": {
            "category": CATEGORIES,
            "sub_category": list(set(search_params['sub_category'])),
            "type": list(set(search_params['type'])),
            "bone_in": list(set(search_params['bone_in'])),
            "prep": list(set(search_params['prep'])),
            "freshness": list(set(search_params['freshness'])),
            "amount": list(set(search_params['amount'])),
            "cooking_method": list(set(search_params['cooking_method']))      
        }
    }
    
    return response_payload
    
