from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import ast
from rasa_sdk.events import SlotSet
import requests
import ast


class Zomato:

    def __init__(self):
        self.api_key="68d8d61fb2aaf00ee69e723b5fc570e7"
        self.base_url = "https://developers.zomato.com/api/v2.1/"


    def getCityId(self,city_name):
        '''
        Takes city name as argument.
        Returns the corressponding city_id.
        '''
        city_name = city_name.split(' ')
        city_name = '%20'.join(city_name)
        print(city_name)
        headers = {'Accept': 'application/json', 'user-key': self.api_key}
        r = requests.get(self.base_url + "cities?q=" + city_name, headers=headers)
        #a = ast.literal_eval(r)
        data=r.json()
        #print(data['location_suggestions'][0]['id'])

        #if there is no such city....it should be an invalid city name...
        if len(data['location_suggestions']) == 0:
            raise Exception('invalid_city_name')
            
        else:
            return data['location_suggestions'][0]['id']

    def get_cuisines(self, city_ID):
        """
        Takes City ID as input.
        Returns dictionary of all cuisine names and their respective cuisine IDs in a given city.
        """

        headers = {'Accept': 'application/json', 'user-key': self.api_key}
        r = (requests.get(self.base_url + "cuisines?city_id=" + str(city_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)
        all_cuisines_in_a_city=a['cuisines']


        cuisines={}

        for cuisine in all_cuisines_in_a_city:
            current_cuisine=cuisine['cuisine']
            cuisines[current_cuisine['cuisine_name'].lower()]=current_cuisine['cuisine_id']


        return cuisines


    def get_cuisine_id(self,cuisine_name,city_id):
        '''
        Takes cuisine name and city id as argument.
        Returns the cuisine id for that cuisine.
        '''
        cusines=self.get_cuisines(city_id)
        return cusines[cuisine_name.lower()]


    def get_all_restraunts(self,city,cuisine):
        '''
        Takes city name and cuisine name as arguments.
        Returns a list of 20 restaurants.
        '''
        city_id=self.getCityId(city)
        cuisine_id=self.get_cuisine_id(cuisine,city_id)

        headers = {'Accept': 'application/json', 'user-key': self.api_key}
        r =requests.get(self.base_url + "search?entity_id=" + str(city_id)+"&cuisines="+str(cuisine_id), headers=headers)

        list_ofall_rest=r.json()["restaurants"]
        names_of_all_rest=[]
        for rest in list_ofall_rest:
            names_of_all_rest.append(rest["restaurant"]["name"])


        return names_of_all_rest



class LocationExtractor:
    
    def __init__(self):
        self.api_token="c596f13460364db9915e6f3f98ffdac2"
        self.base_url="https://api.dandelion.eu/datatxt/nex/v1/"
    
    def extractLocation(self,text):
        list_cities=[]
        params={"token":self.api_token,"min_confidence":0.7,"lang":"en"}
        r=requests.get(self.base_url+"?text="+text+"&include=types%2Cabstract%2Ccategories",params)
        all_locations=r.json()
        
        for x in all_locations["annotations"]:
            list_cities.append(x["label"])
            
        return list_cities

class ActionSetLocation(Action):


    def name(self):
        return "action_set_location"

    def run(self, dispatcher,tracker,domain):
        user_input=tracker.latest_message['text']
        le=LocationExtractor()
        location_name=le.extractLocation(str(user_input))
        print(location_name)
        
        return [SlotSet("location",location_name[0])]


class ActionSetCuisine(Action):
    def name(self):
        return "action_get_cuisine_show_restaurants"


    def run(self, dispatcher,tracker,domain):
        cuisine_type=tracker.get_slot('cuisine')
        location_name=tracker.get_slot('location')
        print(cuisine_type)
        print(location_name)

        zom=Zomato()

        list_all_restaurants=zom.get_all_restraunts(location_name,str(cuisine_type))
        
        for r in list_all_restaurants:
            dispatcher.utter_message(r)

        return []
        

class ActionShowRestaurants(Action):

    def name(self):
        return "action_show_restaurants"

    def run(self, dispatcher,tracker,domain):
        zo=Zomato()
        le=LocationExtractor()
        user_input=tracker.latest_message['text']
        cuisine_type=tracker.get_slot('cuisine')
        location_name=le.extractLocation(str(user_input))
        print(user_input)
        print(cuisine_type)
        print(location_name)
        list_all_restaurants=zo.get_all_restraunts(location_name[0],str(cuisine_type))
        
        for r in list_all_restaurants:
            dispatcher.utter_message(r)

        return []
        
