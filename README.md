# Chefman Assessment

## Problem Statement
Design a search API that returns cooking presets based on the ingredients selected by a user

## Demo

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
Why Dynamo vs Graph
Why API Cache

### Alternatives
