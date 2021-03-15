# Chefman Assessment

## Problem Statement
Design a search API that returns cooking presets based on the ingredients selected by a user

## Demo
[Live URL](https://680tktblrd.execute-api.us-east-1.amazonaws.com/demo/cooking-presets?category=Vegetables&sub_category=Potatoes&type=Russet Potato&bone_in=-&prep=Whole&freshness=Fresh&amount=2 lb&cooking_method=Pressure Cook)

## Project Structure
- `lambda_function.py` contains the Python Lambda code for the REST API
- `postman_collection.json` contains the Postman API requests. This file can be loaded to Postman and the search critieria can be selected in the params list to view results based on search.

## Solution Overview
The design includes
    
    1. Setting data for ingredients and corresponding cooking presets
    2. Searching cooking presets based on ingredients

**Example scenario for search**
`Poultry -> Chicken Breast -> Bone-In -> 1 lb -> Pressure Cook` search should return `Liquid Amount: ½ cup, Pressure Level: High, Pressure Build time: 9, Cook Time: 18`

### System Architecture
![Chefman](https://user-images.githubusercontent.com/7777038/111091737-53618800-850a-11eb-8dd0-2c8477064932.png)

**Architecture Components**

- API Gateway: Implements a REST API with a `/cooking-presets` endpoint that accepts
  1. `GET` request for searching and retrieving the cooking presets based on ingredients
  2. `POST` request to store the ingredients and the correspoinding cooking presets

- Lambda: Acts as a proxy source to transform the API requests and response data and store and retrieve the results from the data source

- DynamoDB: Is the primary data source to store the ingredients and cooking presets along with a search index. 

### Data Model
DynamoDB provides the advantage of schemaless storage helping in scaling the data source without any migration downtimes

The data model has two facets

1. Data Store: Stores the ingredients and cooking presets
2. Search Index: Saves the search index comprising of all the ingredients

DynamoDB uses two keys as identifiers

1. Partition Key: Category of ingredients which is the primary group for any item is used as a partition key. Ex: `Vegetables`
2. Sort Key: All the ingredients are used as a composite key to build the sort key. This design helps in hierarchical searches. Ex: `Poultry#Chicken Breast#Bone-In#1 lb#Pressure Cook`

The cooking presets are stored as key-value pairs

### API
The API is powered by a REST interface that is deployed on an AWS API Gateway. 

The API has a `POST` endpoint to create data and a `GET` endpoint to retrieve data.


**Save Cooking Presets**
```
# Request
POST /cooking-presets
-d 
 {
    "category": "test",
    "sub_category": "test",
    "type": "test",
    "bone_in": "test",
    "prep": "test",
    "freshness": "test",
    "amount": "test",
    "cooking_method": "test",
    "liquid_amount": "test",
    "pressure_level": "test",
    "estimated_pressure_build_time": "test",
    "temperature": "test",
    "cook_time": "test",
    "photo": "test"
  }
```

**Search Cooking Presets**
```
# Request
GET /cooking-presets?category=Meat&sub_category=Beef

# Response
{
    "search_params": {
        "search_params": {
            "category": [
                "Grains",
                "Legumes",
                "Meat",
                "Poultry",
                "Vegetables"
            ],
            "sub_category": [
                "Potatoes"
            ],
            "type": [
                "Russet Potato",
                "Red Potato",
                "Sweet Potato"
            ],
            "bone_in": [],
            "prep": [],
            "freshness": [],
            "amount": [],
            "cooking_method": []
        }
    },
    "results": [...]
}
```

### Reasons
**DynamoDB vs Graph DB**
A problem related to hierarchical/tree based search can be solved using a Graph model. A node at each level comprises of the various ingredients. Ex: Categories at level 1, Sub Categories at level 2 and so on. But graph databases do not scale massively at a low cost. Graph DBs are cost effective to solve problems involving complex relationships. Hence, I have chosen a hierarchical model built on DynamoDB. DynamoDB returns results with sub millisecond latency which is critical in a search feature like the current problem. DynamoDB helps both as as storage engine and search engine

**API Caching**
The search page is often a highly visited page, hence caching is required. The current solution caches the list of categories and the results defaulted to 'Grains' category in the ephemeral lambda storage but in real-time it will be cached on the API Gateway cache response. 

**Search Index**
The search index is designed to save the hierarchical/tree nature of the ingredients in the sort key. A search request from the client hits the partition key(category) first and then based on the search params it hits the sort keys that match the search params. The search critieria is recursively populated with the next node in the hierarchy along with the matched cooking preset results.

**Response structure**
The response for search has two keys

1. search_params
2. results

The `search_params` contain the grouped ingredients based on the user selection. Ex: If the user searches for a category Meat then the search_params will contain the sub_category key with Beef and Meat Products. 

The `results` contain the cooking presets that match the search criteria. Returning the results for each level of search helps to build richer clients where users keep seeing the data continuously. 
