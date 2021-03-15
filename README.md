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

### API
API request/response

### Reasons

### Alternatives
