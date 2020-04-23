import requests
import math

def get_questions_id(url):
    questions_id = []
    response = requests.get(url)
    data_lst = response.json()
    for item in data_lst:
        if item["ask_question"] == True:
            questions_id.append(item["question_ID"])
    return questions_id

def get_questions(base_url, questions_id_lst):
    questions = {}
    for questions_id in questions_id_lst:
        url = base_url + questions_id
        response = requests.get(url)
        data = response.json()
        questions[questions_id] = data["question"]
    return questions

def get_gps(url):
    response = requests.get(url)
    data = response.json()
    latlng = data["lat_long"]
    return latlng

def get_user_availability(url):
    response = requests.get(url)
    data = response.json()

def find_dist(gps1, gps2):
    earth_radius = 6373.0
    gps1_lst = gps1.split(",")
    gps2_lst = gps2.split(",")

    lat1 = math.radians(float(gps1_lst[0]))
    lon1 = math.radians(float(gps1_lst[1]))
    lat2 = math.radians(float(gps2_lst[0]))
    lon2 = math.radians(float(gps2_lst[1]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_in_km = earth_radius * c
    distance_in_m = distance_in_km * 1000

    return distance_in_m

def main():
    user_id = "1000"
    home_assistant_url = "https://daisy-project.herokuapp.com/home-assistant/user/" + user_id
    home_assistant_gps = get_gps(home_assistant_url)
    phone_url = "https://daisy-project.herokuapp.com/phone/user/" + user_id
    phone_gps = get_gps(phone_url)
    distance = find_dist(home_assistant_gps, phone_gps)
    print("Distance between phone and picroft: {}m".format(distance))

if __name__ == "__main__":
    main()
