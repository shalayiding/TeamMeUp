# handle different mongodb event  
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime,timedelta
from bson.objectid import ObjectId

# all the user class operation will be here 
class DB_Users:
    def __init__(self,db_url,db_name,collection_name) -> None:
        self.clint = MongoClient(db_url,server_api = ServerApi('1'))
        self.db = self.clint[db_name]
        self.collection = self.db[collection_name]

    
    #change the existing db and collection 
    def switch_db_collection(self,db_name,collection_name):
        self.db = self.clint[db_name]
        self.collection = self.db[collection_name]
    
    
    # check if the user exist and return the mongodb register id
    def check_user_exist(self,discord_id,email):
        query = {}
        if discord_id:
            query['dc_id'] = discord_id
        if email:
            query['email'] = email
        result = self.collection.find_one(query)
        if result:
            return str(result['_id'])
        else:
            return None

    # register new user and give them id for that
    def register_user(self,discord_id,global_name,source,avatar_uri,email=""):
        data = {"dc_id":discord_id,
                "dc_global_name":global_name,
                "register_source":source,
                "dc_avatar_uri":avatar_uri,
                "email":email}
        result = self.collection.insert_one(data)
        if result:
            return result.inserted_id
        else :
            return None        
        
        
    #find a user using thier mongodb it return the bson document         
    def find_user_by_id(self, user_id_str):
        try:
            user_id = ObjectId(user_id_str)
        except Exception as e:
            print(f"Error converting to ObjectId: {e}")
            return None

        user_document = self.collection.find_one({"_id": user_id})

        return user_document