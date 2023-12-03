import scratchattach as scratch3
import time
from datetime import datetime
import os

#session = scratch3.Session(".eJxVkE1vgzAMhv8L55XFIZDRG2WnHqZ10r5OkUlMyShJBakqddp_XyJx6SmSH_vJa_9ml4VmhxNl26z12qt2IKc4gzp7yIIfyUUghQBWyB4Yk0LXBRKVhaEKtGRCMtyKj83zJ4fpSQzt4bV5389f8rAf5uYmoubkj9Zt7DmZipxzyKFi8Y1I4SUMKmVQ1kReQlGXICEi84Pu6FWwE928S_maiWar8fGFrurbz-P9_IDLEJs6XYm6F4zrEpEJI7DrAHoGUsgeeQeI3BCwtB4tQXs_2iS_RiGZe2WHOh4g5Uo1ciH-Hqx3-QqW_I3Op7W4W5v__gErW2vs:1r8vNV:coyUxW-fg_KYQTbikx3PZbl7U_E", username="Coco_Chen_2019") #replace with your session_id and username
session = scratch3.login(os.environ["SCRATCH_USER_NAME"], os.environ["SCRATCH_CREDENTIAL"])
conn = session.connect_cloud("933459770") #replace with your project id
#conn = scratch3.connect_tw_cloud("933459770") #replace with your project id
#conn = scratch3.TwCloudConnection(project_id="933459770", username="Coco_Chen_2019")

#value = scratch3.get_var("933459770", "FROM_HOST_1")
#conn.set_var("myvariable", "this is fun var!")

client = scratch3.CloudRequests(conn)
#client = scratch3.CloudRequests(conn, used_cloud_vars=["1","2","3","4","5",...])
#conn.set_var("FROM_HOST_1", 90)
#value = scratch3.get_var("933459770", "FROM_HOST_1")
#print(value)

project = session.connect_project("933459770")
index = -1

@client.request
def get_time():
    # This function will be called when the client receives "get_time" from the cloud variable
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

@client.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong" #sends back 'pong' to the Scratch project

@client.event
def on_ready():
    print("Request handler is running")

@client.request
def message_count(argument1):
    print(f"Message count requested for user {argument1}")
    user = scratch3.get_user(argument1)
    return user.message_count()

@client.request
def foo(argument1):
    print(f"Data requested for user {argument1}")
    user = scratch3.get_user("LazyEyeTV")
    stats = user.stats()

    print(stats)

    return stats

@client.request
def comments():
    print(f"received at {datetime.now()}")
    global index
    comments = project.comments()
    if comments:
        if index < -1 * len(comments):
            index = -1
        print(datetime.now(), comments[index])
        author = comments[index]["author"]['username']
        content = comments[index]["content"]
        index -= 1
        return f'{author} said "{content}"'

client.run() #make sure this is ALWAYS at the bottom of your Python file
