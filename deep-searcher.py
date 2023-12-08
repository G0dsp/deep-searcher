import re
import requests
import random

def scrape(newdata):
    try:
        yourquery = newdata
        yourquery = yourquery.replace(" ", "+")
        url = f"https://ahmia.fi/search/?q={yourquery}"
        request = requests.get(url)
        request.raise_for_status()  
        content = request.text
        regexquery = r'<a href="(.*?)"'
        mineddata = re.findall(regexquery, content)

        n = random.randint(1, 9999)
        filename = f"sites_{n}.txt"

        print(f"Saving to {filename}")

        mineddata = list(dict.fromkeys(mineddata))

        cleaned_links = []
        for k in mineddata:
         
            cleaned_link = k.split('=')[-1].strip()
            
           
            if cleaned_link.startswith("/blacklist/report?onion="):
               
                cleaned_link = cleaned_link[len("/blacklist/report?onion="):]
            
            cleaned_links.append(cleaned_link)

        with open(filename, "w") as newfile:
            for link in cleaned_links:
                link = link + "\n"
                newfile.write(link)

        print("All the links written to a text file:", filename)

        with open(filename) as input_file:
            head = [next(input_file) for x in range(5)]
            contents = "\n".join(map(str, head))
            print(contents)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

newdata = input("[*] Please Enter Your Query: ")
scrape(newdata)
