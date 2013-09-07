import getopt, sys
import requests
import json

api_key = ""
secret_key = ""
api_url = "http://ws.audioscrobbler.com/2.0/"
artists = []
tags = {}
tagcloud = {}

#default to an awesome user
user_name = "iLikeSpoons"

# Reat the api-key and secret-key for the last.fm api from a
# file given as a parameter.
def read_config(arg):
    global api_key, secret_key
    try:
        config = open(arg)
        api_key, secret_key = config.read().splitlines()
        api_key = api_key.rpartition(":")[2]
        secret_key = secret_key.rpartition(":")[2]
    except IOError:
        print("error reading file")
    else:
        print("Config file successfully read\n")

# An example of how to use the last.fm api to get userinfo for a user
def get_user_info():
    payload = {"method": "user.getinfo",
               "user": user_name,
               "api_key": api_key,
               "format": "json"}
    r = requests.get(api_url, params=payload)
    print(r.status_code)
    if r.status_code == 200:
        json_response = r.json()
        return json_response

# Use the last.fm api to get all the top tags for every one of the top
# 50 bands for a given user.
def get_tag_clouds():
    global artists, tags
    payload = {"method": "user.getTopArtists",
               "user": user_name,
               "period": "overall",
               "api_key": api_key,
               "format": "json"}
    r = requests.get(api_url, params=payload)
    print(r.status_code)
    print(r.headers["content-type"])
    if r.status_code == 200:
        json_response = r.json()
        count = 0
        print("getting tags for given user:")
        for group in json_response["topartists"]["artist"]:
            artists.append({"name": group["name"], "playcount": int(group["playcount"])})
            print("".join((str(2*count), "%", "".join(["." for i in range(count)]))), end="\r")
            count += 1
            payload = {"method": "artist.gettoptags",
                       "artist": group["name"],
                       "api_key": api_key,
                       "format": "json"}
            r = requests.get(api_url, params=payload)
            artist_tags = r.json()["toptags"]["tag"]
            taglist = []
            for tag in artist_tags:
                if int(tag["count"]) > 1:
                    taglist.append({"name": tag["name"], "count": int(tag["count"])})
            tags.update({group["name"]: taglist})
        generate_tagcloud()
    #now we have a set of tag clouds!

# Generate a tagcloud from the joint tags and playcounts
# the counts are generated kinda randomly, this still needs tweaking
# and an option to export the object into json for visualisation.
def generate_tagcloud():
    global tagcloud
    for artist_obj in artists:
        score_mul = artist_obj["playcount"]
        artist = artist_obj["name"]
        for tag_obj in tags[artist]:
            if tag_obj["name"] in tagcloud:
                curr_value = tagcloud[tag_obj["name"]]
                tagcloud[tag_obj["name"]] = curr_value + (tag_obj["count"]/100)*(score_mul/100)
            else:
                tagcloud.update({tag_obj["name"]: (tag_obj["count"]/100)*(score_mul/100)})
    for tag in tagcloud:
        if tagcloud[tag] > 1:
            print(" - ".join((tag, str(tagcloud[tag]))))

# Read command line parameters, do errythin'
def main(argv):
    global api_key, secret_key, user_name
    opts, args = getopt.getopt(argv, "c:hu:", ["config=", "help", "user="])
    config_file_specified = False
    for opt, arg in opts:
        if opt in ("-c, --config"):
            config_file_specified = True
            read_config(arg)
        elif opt in ("-h", "--help"):
            print("specify a config file or an api key for last.fm")
        elif opt in ("-u, --user"):
            user_name = arg
    if not config_file_specified and len(args) < 1:
        print("please specify a valid config file or an api key for last.fm")
    elif not config_file_specified:
        api_key = args[0]
        if len(args) > 1:
            secret_key = args[1]

    print("".join(("getting info for user ", user_name)))
    #get_user_info()
    get_tag_clouds()

if __name__ == "__main__":
    main(sys.argv[1:])
