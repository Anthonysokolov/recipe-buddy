import json
from botocore.vendored import requests
import random


def lambda_handler(event, context):
    '''
    Main function to handle a request to the lambda function
    '''
    if event['request']['type'] == "LaunchRequest":
        return statement('Recipe Buddy', 'What food would you like to include in a recipe?', False)
    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)
        

def statement(title, body, endSession, session_attributes = {}):
    '''
    Build response in json format
    '''
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = endSession
    return build_response(speechlet, session_attributes)
    
    
def build_PlainSpeech(body):
    '''
    Build speech in json format
    '''
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech
    
    
def build_SimpleCard(title, body):
    '''
    Build alexa card in json format
    '''
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card
    
    
def build_response(message, session_attributes):
    '''
    Build json response
    '''
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response
    
    
def intent_router(event, context):
    '''
    Handle intents
    '''
    intent = event['request']['intent']['name']
    # Custom Intents
    if intent == "getPriceIntent":
        return get_food_slot(event, context)
    if intent == 'getIngredientsIntent':
        return get_ingredients(event, context)
    # Required Intents
    if intent == "AMAZON.CancelIntent":
        return stop_intent(event, context)
    if intent == "AMAZON.HelpIntent":
        return help_intent(event, context)
    if intent == "AMAZON.StopIntent":
        return stop_intent(event, context)
    if intent == "AMAZON.FallbackIntent":
        return fallback_intent(event, context)
    if intent == "AMAZON.NavigateHomeIntent":
        return navigate_home_intent(event, context)
    
def get_food_slot(event, context):
    '''
    Retrieves the ingredient that the user wants a recipe with
    '''
    try:
        food = event['request']['intent']['slots']['food']['value']
    except Exception:
        return statement('Recipe Buddy','I could not find that food', True)
        
    return get_recipe(food)
    

def get_recipe(food):
    '''
    Finds a recipe containing the requested food using the Food2Fork API
    '''
    key = '792b7425bc065f090f0d644b1a0b0cf7'
    
    search = 'https://www.food2fork.com/api/search'
    sparams = {'key':key,'q':food,'sort':'r'}
    
    sresponse = requests.get(search,params=sparams).json()
    
    try:
        rid = sresponse['recipes'][random.randint(0,29)]['recipe_id']
    except IndexError:
        return statement('Recipe Buddy','Sorry, I could not find a recipe with that ingredient', True)
        
    get = 'https://www.food2fork.com/api/get'
    gparams = {'key':key,'rId':rid}
    
    gresponse = requests.get(get,params=gparams).json()
    
    rname = gresponse['recipe']['title']
    ingredients = gresponse['recipe']['ingredients']
    
    s = 'Using ' + food + ', You can make ' + rname + '. Would you like to hear the ingredients of the recipe?'
    
    return statement('Recipe Buddy',s, False,{'ingredients':ingredients,'recipe':rname})
    
    
def get_ingredients(event, context):
    '''
    Returns the ingredients of a recipe
    '''
    recipe = event['session']['attributes']['recipe']
    ingredients = event['session']['attributes']['ingredients']
    s = 'The ingredients of ' + recipe + ' are '
    for i in ingredients:
        s += i + ', '
    return statement('Recipe Buddy', s, True)


# Required intents
def help_intent(event, context):
    var = "Ask Recipe Buddy what food you would like to learn about"
    return statement("How To", var, False)
    

def stop_intent(event, context):
    var = "Thank you for using Recipe Buddy"
    return statement("Exit", var, True)
    

def fallback_intent(event, context):
    var = 'What food would you like a recipe with?'
    return statement('Recipe Buddy', var, False)

def navigate_home_intent(event, context):
    var = 'What food would you like to learn about?'
    return statement('Recipe Buddy', var, False)