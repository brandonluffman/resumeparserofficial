import json
import spacy

nlp = spacy.load("en_core_web_lg")

# Load skills from the JSON file
job_description = """
Leveraging AWS to build out our APIs, data model, authorization, and other infrastructure
Building out and streamlining our frontend infrastructure
Implementing and maintaining our React web forms
Collaborating with other engineers to create a seamless integration with the computational backend
Creating a best-in-class user experience for our prospects and customers
"""

# Process the job description with spaCy
doc = nlp(job_description)

# Extract all entities
all_entities = [(ent.text, ent.label_) for ent in doc.ents]

print("Extracted Entities:", all_entities)









# ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjNDNjZCRjIzMjBGNkY4RDQ2QzJERDhCMjI0MEVGMTFENTZEQkY3MUYiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJQR2FfSXlEMi1OUnNMZGl5SkE3eEhWYmI5eDgifQ.eyJuYmYiOjE3MDgzMDIwMjEsImV4cCI6MTcwODMwNTYyMSwiaXNzIjoiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20iLCJhdWQiOlsiZW1zaV9vcGVuIiwiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20vcmVzb3VyY2VzIl0sImNsaWVudF9pZCI6InRoZ2Voa3VxeGhmbmRqODciLCJlbWFpbCI6ImJyYW5kb25sdWZmMTBAZ21haWwuY29tIiwiY29tcGFueSI6IlBoYW50b20iLCJuYW1lIjoiQnJhbmRvbiBMdWZmbWFuIiwiaWF0IjoxNzA4MzAyMDIxLCJzY29wZSI6WyJlbXNpX29wZW4iXX0.ttmeYk_l0RGUtUXgsSEWc11tS8YHYD3bdov0UXpTuKXGWwyVpTBBWeVTpxsd1ENLFpr2-FfdGWvdU9vOGg00QaGoZjnengZjIRQRS7Nc6fNsywuC3YiIn4DgvBbWt5YpawXN6AKXvsfMTYKItfIi_wgnBpWwYbbCoIZYCImIEOoJvSmkfSJjrmINhb9Y1GwDnr_L-o1w_C74IJdIiF4jEYuD6AgrJrSPnbKvNBhXqOI-Icla120euChcb8dcDezxJfjvv5st2rs4PHYn25gQAG9FaQG-W-fhiKW_9A8MiRwMxbzqGBiT2-iDHzxOy_aqhMX6MDqN-hnrMsCPaXZlEw'



# url = "https://emsiservices.com/skills/versions/latest/extract"

# querystring = {"language":"en"}

# payload = f'{{ "text": "{text}", "confidenceThreshold": 0.6 }}'
# headers = {
#     'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjNDNjZCRjIzMjBGNkY4RDQ2QzJERDhCMjI0MEVGMTFENTZEQkY3MUYiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJQR2FfSXlEMi1OUnNMZGl5SkE3eEhWYmI5eDgifQ.eyJuYmYiOjE3MDgzMDIwMjEsImV4cCI6MTcwODMwNTYyMSwiaXNzIjoiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20iLCJhdWQiOlsiZW1zaV9vcGVuIiwiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20vcmVzb3VyY2VzIl0sImNsaWVudF9pZCI6InRoZ2Voa3VxeGhmbmRqODciLCJlbWFpbCI6ImJyYW5kb25sdWZmMTBAZ21haWwuY29tIiwiY29tcGFueSI6IlBoYW50b20iLCJuYW1lIjoiQnJhbmRvbiBMdWZmbWFuIiwiaWF0IjoxNzA4MzAyMDIxLCJzY29wZSI6WyJlbXNpX29wZW4iXX0.ttmeYk_l0RGUtUXgsSEWc11tS8YHYD3bdov0UXpTuKXGWwyVpTBBWeVTpxsd1ENLFpr2-FfdGWvdU9vOGg00QaGoZjnengZjIRQRS7Nc6fNsywuC3YiIn4DgvBbWt5YpawXN6AKXvsfMTYKItfIi_wgnBpWwYbbCoIZYCImIEOoJvSmkfSJjrmINhb9Y1GwDnr_L-o1w_C74IJdIiF4jEYuD6AgrJrSPnbKvNBhXqOI-Icla120euChcb8dcDezxJfjvv5st2rs4PHYn25gQAG9FaQG-W-fhiKW_9A8MiRwMxbzqGBiT2-iDHzxOy_aqhMX6MDqN-hnrMsCPaXZlEw",
#     'Content-Type': "application/json"
#     }

# response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

# response_json = json.loads(response.text)
# skills = [skill['skill']['name'] for skill in response_json['data']]
# print(skills)


# url = "https://emsiservices.com/skills/versions/latest/skills"

# querystring = {"typeIds":"ST1,ST2","fields":"name"}

# headers = {'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjNDNjZCRjIzMjBGNkY4RDQ2QzJERDhCMjI0MEVGMTFENTZEQkY3MUYiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJQR2FfSXlEMi1OUnNMZGl5SkE3eEhWYmI5eDgifQ.eyJuYmYiOjE3MDgzMDIwMjEsImV4cCI6MTcwODMwNTYyMSwiaXNzIjoiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20iLCJhdWQiOlsiZW1zaV9vcGVuIiwiaHR0cHM6Ly9hdXRoLmVtc2ljbG91ZC5jb20vcmVzb3VyY2VzIl0sImNsaWVudF9pZCI6InRoZ2Voa3VxeGhmbmRqODciLCJlbWFpbCI6ImJyYW5kb25sdWZmMTBAZ21haWwuY29tIiwiY29tcGFueSI6IlBoYW50b20iLCJuYW1lIjoiQnJhbmRvbiBMdWZmbWFuIiwiaWF0IjoxNzA4MzAyMDIxLCJzY29wZSI6WyJlbXNpX29wZW4iXX0.ttmeYk_l0RGUtUXgsSEWc11tS8YHYD3bdov0UXpTuKXGWwyVpTBBWeVTpxsd1ENLFpr2-FfdGWvdU9vOGg00QaGoZjnengZjIRQRS7Nc6fNsywuC3YiIn4DgvBbWt5YpawXN6AKXvsfMTYKItfIi_wgnBpWwYbbCoIZYCImIEOoJvSmkfSJjrmINhb9Y1GwDnr_L-o1w_C74IJdIiF4jEYuD6AgrJrSPnbKvNBhXqOI-Icla120euChcb8dcDezxJfjvv5st2rs4PHYn25gQAG9FaQG-W-fhiKW_9A8MiRwMxbzqGBiT2-iDHzxOy_aqhMX6MDqN-hnrMsCPaXZlEw'}

# response = requests.request("GET", url, headers=headers, params=querystring)
# response_json = json.loads(response.text)

# # Extract skill names
# skill_names = [skill['name'] for skill in response_json['data']]

# # Write skill names to a JSON file
# with open('skills.json', 'w') as file:
#     json.dump(skill_names, file, indent=4)

# url = "https://auth.emsicloud.com/connect/token"

# payload = "client_id=thgehkuqxhfndj87&client_secret=wHdYRRCy&grant_type=client_credentials&scope=emsi_open"
# headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# response = requests.request("POST", url, data=payload, headers=headers)

# print(response.text)