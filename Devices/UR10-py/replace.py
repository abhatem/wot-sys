import json
import _pickle as pickle

# Load the files
with open("TM.json", "r") as f:
    tm_dict = json.load(f)

with open("config.json", "r") as f:
    config = json.load(f)

# Convert the dictionaries to strings
tm_string = json.dumps(tm_dict)
config_string = json.dumps(config)

# Create a new dictionary using the keys and values from config.json
config_for_TM = {}

for key_old in config:
    key_new = r"{{" + str(key_old) + r"}}"
    config_for_TM[key_new] = config[key_old]

# Replace the keys in the TM string with their values from the config dictionary
for key, value in config_for_TM.items():
    tm_string = tm_string.replace('"{}"'.format(key), str(value))
    tm_string = tm_string.replace(key, str(value))

# Convert the modified TM string back to a dictionary
tm_modified_dict = json.loads(tm_string)

# Set additional fields in the modified TM dictionary
tm_modified_dict["@type"] = config["@type"]
tm_modified_dict["securityDefinitions"] = config["securityDefinitions"]
tm_modified_dict["security"] = ["nosec_sc"]

# Copy links from TM.json
tm_modified_dict["links"] = tm_dict["links"]

# Update the forms for actions and properties
for key in tm_modified_dict["actions"]:
    tm_modified_dict["actions"][key]["forms"] = [{
        "href": "actions/{}".format(key),
        "contentType": "application/json",
        "op": "invokeaction",
        "htv:methodName": "POST"
    }]

for key in tm_modified_dict["properties"]:
    if tm_modified_dict["properties"][key]["readOnly"] == True:
        tm_modified_dict["properties"][key]["forms"] = [{
            "href": "properties/{}".format(key),
            "op": ["readproperty"],
            "contentType": "application/json"
        }]
    elif tm_modified_dict["properties"][key]["readOnly"] == False and tm_modified_dict["properties"][key]["writeOnly"] == False:
        tm_modified_dict["properties"][key]["forms"] = [{
            "href": "properties/{}".format(key),
            "op": "readproperty",
            "contentType": "application/json",
            "htv:methodName": "GET"
        },
        {
            "href": "properties/{}".format(key),
            "htv:methodName": "PUT",
            "op": "writeproperty",
            "contentType": "application/json"
        }]

# Write the modified dictionary to convertedTD.json
with open('convertedTD.json', 'w') as file:
    file.write(json.dumps(tm_modified_dict, indent=1, sort_keys=True))
