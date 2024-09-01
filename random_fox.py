import requests
import pprint


def fox():
    url = "https://randomfox.ca/floof"
    response = requests.get(url)
    response_json = response.json()
    if response.status_code:
        data = response.json()
        # print(data.get('image'))
        return data.get('image')


# if __name__ == '__main__':
#     fox()
fox()