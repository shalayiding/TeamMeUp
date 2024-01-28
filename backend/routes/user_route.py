from flask import request,Flask,jsonify,session,redirect, url_for,Blueprint,make_response
from services.discord_oauth2 import DCoauth
from models.match import DB_Matchs
from models.users import DB_Users
import config as keys
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from datetime import timedelta

# setting blueprint and mongodb properties
user_bp = Blueprint('user_bp', __name__)
db_match = DB_Matchs(keys.mongodb_link,"Matchs","game")
db_user = DB_Users(keys.mongodb_link,'Matchs','user')



# get user detail information if the user is login or using discord bot
@user_bp.route('/user/me',methods=['GET'])
@jwt_required(locations=['cookies','headers'])
def finduser():
    current_user = get_jwt_identity()
    user = db_user.find_user_by_id(current_user['_id'])
    data = {"dc_id":user["dc_id"],
            "dc_global_name":user["dc_global_name"],
            "register_source":user["register_source"],
            "dc_avatar_uri":user["dc_avatar_uri"],
            "email":user["email"],
            }
    
    return jsonify({"data":data})



@user_bp.route('/user/login',methods=['GET'])




# @user_bp.route('/user/register',methods=['POST'])
# def register_user():
#     data = request.json 
#     # get user info
#     user_id = data.get('id')
#     token = data.get('token')
#     avatar_uri = data.get('avatar_uri')
#     email = data.get('email')
#     global_name = data.get('global_name')
#     register_parts = (user_id and avatar_uri and global_name and email)
#     if register_parts and db_user.check_user_exist(user_id,email) == None:
#         register_type = "web"
#         if token == keys.discord_bot_token:
#             register_type = "bot"
#         try :
#             register_result = db_user.register_user(user_id,
#                                 global_name,
#                                 register_type,
#                                 avatar_uri,
#                                 email)
#             return jsonify({"Message":"You have register to the database"}),200
#         except Exception as e:
#             return jsonify({"Message":e}),400
#     else:
#         return jsonify({"Message":"Either user exist or are not able to register you"}),400      
    

        
    
#oauth2 with to link/discord
@user_bp.route('/link/discord',methods=['GET'])
def linkDiscord():
    code = request.args.get('code')
    if code:
        discord_oauth = DCoauth()
        try :
            data = discord_oauth.exchange_code(str(code))
        except Exception as e:
            return jsonify({"msg":"Cannot Link you discord account, try to back to the home page and do it again"},401)
        
        
        if data['access_token']:
            user = discord_oauth.get_current_user(data['access_token'])
            
            if not user:
                return jsonify({"msg":"Didn't find your profile in linkedin"},404)
            
            try :
                found_user = db_user.check_user_exist(user['id'],user['email'])
                mongodb_id = ""
                if found_user == None:
                    mongodb_id = db_user.register_user(user['id'],
                                            user['global_name'],
                                            "web",
                                            f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}",
                                            user['email'])
                
                expires = timedelta(hours=3)
                access_token = create_access_token(identity={"_id":found_user},expires_delta=expires)
                response = make_response(redirect("http://localhost:3000/"))
                
                response.set_cookie("access_token_cookie", access_token, httponly=True)
                return response   
            except Exception as e:
                return jsonify({"msg":"Something went wrong while registerinig you"},401)  
             
        else:
            return jsonify({"msg":"No access token found "},404)
    else:
        return jsonify({"msg":"No code provided, discord linked faild"},404)


    
    