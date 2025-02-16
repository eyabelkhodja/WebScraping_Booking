from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image
from bs4 import BeautifulSoup
from random import randint

import math
import time
import re

from pymongo import MongoClient

#crée une connection avec ma base de donnée sur mongodb
client = MongoClient("mongodb+srv://belkhodjaeya16:Eya3615Mongodb@eyastage.z2pxfys.mongodb.net/Eyastage?retryWrites=true&w=majority&appName=Eyastage")
db = client['scraping_booking']
collection = db['booking_database']

#fonction pour vérifier la validité de la date donnée par l'utilisateur
def valide(ch):
    if len(ch) > 9:
        if ch[:2].isdigit():
            if not (0 < int(ch[:2]) < 32):
                print("Problème de jour")
                return False
            
            if not (2023 < int(ch[-4:]) < 2026):
                print("Problème d'année")
                return False
            
            if not (ch[2] == " " and ch[-5] == " "):
                print("Problème d'espaces")
                return False
            
            if not (ch[3] == ch[3].upper()):
                print("Problème de majuscules")
                return False

            ch1 = ch[3:-5]
            if ch1.upper() in ["JANVIER", "MARS", "AVRIL", "MAI", "JUIN", 
                               "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE"]:
                return True
            
            if ch1 in ["Décembre", "Février"]:
                return True
        
    return False

#fonction pour que l'utilisateur donne les éléments clés pour éffectuer une recherche concluante
def get_user_input():
    name_hotel = input("Donner le nom de votre hôtel: ").strip()
    date_arrival = ""
    date_departure = ""
    
    while not valide(date_arrival):
        date_arrival = input("Donner la date d'arrivée correcte de la forme xx Mois xxxx: ").strip()
    
    while not valide(date_departure):
        date_departure = input("Donner la date de départ correcte de la forme xx Mois xxxx: ").strip()

    adults = int(input("\nDonner le nombre d'adultes: "))
    kids = int(input("Donner le nombre d'enfants: "))
    
    return name_hotel, date_arrival, date_departure, adults, kids

#fonction pour closer le pop-up qui s'affiche en première (et parfois deuxième) page SI il est présent sur la page
def close_pop_up(driver):
    time.sleep(5)
    try:
        #essayer de localiser le pop-up en utilisant selenium
        pop_up_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Ignorer les infos relatives à la connexion']"))
        )
        pop_up_button.click()
    except Exception as e:
        print(f"Error closing pop-up with normal click: {e}. Trying with JavaScript...")
        try:
            #essayer de localiser le pop-up en utilisant javascript car la méthode précédente a raté
            pop_up_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Ignorer les infos relatives à la connexion']")
            driver.execute_script("arguments[0].click();", pop_up_button)
        except Exception as e:
            print(f"Error closing pop-up with JavaScript: {e}")

def click_element_with_js(driver, element):
    driver.execute_script("arguments[0].click();", element)

#fonction pour rechercher le mois si il n'est pas visible dans la première page du calendrier de dates
def navigate_to_next_month(driver):
    try:
        next_month_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Mois suivant']"))
        )
        next_month_button.click()
    except Exception as e:
        print(f"Error clicking next month: {e}")

#fonction pour sélectionner la date saisie par l'utilisateur
def select_date(driver, date):
    try:
        while True:
            try:
                date_element = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@aria-label='{date}']"))
                )
                date_element.click()
                break
            except Exception:
                navigate_to_next_month(driver)
    except Exception as e:
        print(f"Failed to select date '{date}': {e}")

#fonction pour ajuster les voyageurs selon la saisie de l'utilisateur
def adjust_guests(driver, adults, kids, kids_ages):
    selector=driver.find_elements(By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.e137a4dfeb.d1821e6945")
    try:
        adult_button = selector[0]
        if adults > 2:
            for j in range(adults - 2):
                adult_button.click()
        elif adults < 2:
            adult_button_decrement = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.e137a4dfeb.af4d87ec2f"))
            )
            for k in range(2 - adults):
                adult_button_decrement.click()
    except Exception as e:
        print(f"An error occurred while trying to adjust the number of adults: {e}")

    try:
        if kids > 0:
            kid_button = selector[1]
            for i in range(kids):
                kid_button.click()
                time.sleep(1)
                #l'ajustement de l'âge des enfants est obligatoir sur booking pour effectuer une recherche
                adjust_age(driver, kids_ages[i], i)
    except Exception as e:
        print(f"An error occurred while trying to adjust the number of kids: {e}")

#fonction pour saisir l'âge des enfants si il y en a
def get_kids_ages(kids_count):
    kids_ages = []
    for i in range(kids_count):
        while True:
            try:
                age = int(input(f"Enter the age for kid {i + 1}: "))
                if 0 <= age <= 17:
                    kids_ages.append(age)
                    break
                else:
                    print("Please enter a valid age between 0 and 17.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
    
    return kids_ages

#fonction pour selectioner l'âge des enfants sur la page
def adjust_age(driver, kids_ages, index):
    try:
        age_selectors = driver.find_elements(By.NAME, "age")  
        #plus le nombre d'enfants augmente plus le nombre de boutons âge apparaissent, et chaque indexe de bouton correspond à l'indexe de son enfant respectif
        age_selector = age_selectors[index]
        age_selector.click()
        age_selector.send_keys(str(kids_ages))  
        time.sleep(1)  
    except Exception as e:
        print(f"An error occurred while adjusting ages: {e}")

#fonction pour vérifier qu'un élément est présent sur l'écran et observable par l'utilisateur pour la capture d'écran
def is_element_visible(driver, element):
    try:
        if not element:
            return False
        
        bounding_box = element.rect
        is_visible_in_viewport = driver.execute_script(
            "return (arguments[0].getBoundingClientRect().top >= 0 && " +
            "arguments[0].getBoundingClientRect().bottom <= window.innerHeight);",
            element
        )
        
        if element.is_displayed() and is_visible_in_viewport:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking element visibility: {e}")
        return False

#fonction pour scroller le long de la page jusqu'à ce que l'élement recherché soit visible selon les critères de la fonction précédente
def scroll_until_element_visible(driver, by, value):
    try:
        current_position = 0  
        scroll_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            try:
                element = driver.find_element(by,value)
                
                if is_element_visible(driver, element):
                    break 
            except Exception:
                pass 

            #scroller en utilisant javascript
            driver.execute_script("window.scrollBy(0, 700);")
            current_position += 400  
            time.sleep(1)  

            new_scroll_height = driver.execute_script("return document.body.scrollHeight")
            if new_scroll_height > scroll_height:
                scroll_height = new_scroll_height

            if current_position >= scroll_height:
                print("Reached the bottom of the page. Element not found.")
                break  
    except Exception as e:
        print(f"Error scrolling to element: {e}")

def print_all_documents():
    try:
        documents = collection.find()
        document_count = collection.count_documents({})  # Get the count of documents
        if document_count == 0:
            print("No documents found in the collection.")
        else:
            for doc in documents:
                print(doc)
    except Exception as e:
        print(f"Error fetching documents from MongoDB: {e}")

#fonction pour insérer le résultat de notre recherche dans notre base de donnée mongodb
def insert_data_into_mongodb(data):
    try:
        existing_doc = collection.find_one({"hotel_name": data['hotel_name'],
                                            "date_arrival": data['date_arrival'],
                                            "date_departure": data['date_departure'],
                                            "number_of_adults": data['number_of_adults'],
                                            "number_of_children": data['number_of_children'],
                                            "children_ages": data['children_ages']})
        if existing_doc:
            print("Document already exists.")
        else:
            result = collection.insert_one(data)
            print(f"Data successfully inserted into MongoDB with _id: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

def main():
    chambres=1
    #générer un nombre aléatoire pour l'appelation du screenshot pour que chqaue essai du code nous donner une image nommée différemment
    x=randint(0,9999999999999999999)

    #enregistrer l'adresse de sauvegarde des screenshots preuve
    folder_path = r"C:\Users\belkh\OneDrive\Desktop\selenium\proof"    
    filename = f"{folder_path}/proof-{x}.png"

    name_hotel, date_arrival, date_departure, adults, kids = get_user_input()
    
    if date_arrival[0] == "0":
        date_arrival = date_arrival[1:]

    if date_departure[0] == "0":
        date_departure = date_departure[1:]

    kids_ages = get_kids_ages(kids) if kids > 0 else []

    #vérifier si l'utilisateur veut préciser le nombre de chambres (information optionnelle pour la recherche)
    answer=""
    while not (answer.upper()=="OUI" or answer.upper()=="NON"):
        answer= input("\nVoulez-vous décider combien de chambres vous voulez? Répondez par oui ou non: ")

    if (answer.upper()=='OUI'):
        chambres=int(input("Donner le nombre de chambres: "))

    service = Service(r"C:\Users\belkh\OneDrive\Desktop\selenium\chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    try:
        driver.maximize_window()
        time.sleep(2)
        driver.get("https://www.booking.com/index.fr.html")
        time.sleep(3)

        close_pop_up(driver)

        #saisie des éléments de recherche donnés par l'utilisateur dans booking:
        nom_hotel = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.NAME, "ss"))
        )
        nom_hotel.send_keys(name_hotel)
        time.sleep(2)

        button_resultat = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='autocomplete-result-0']/div"))
        )
        button_resultat.click()
        time.sleep(2)

        select_date(driver, date_arrival)
        time.sleep(2)
        select_date(driver, date_departure)
        time.sleep(2)

        accomodation = driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/form/div[1]/div[3]/div/button')
        accomodation.click()

        adjust_guests(driver, adults, kids, kids_ages)

        #il existe deux cas distincts à prendre en considération:
        # Premier cas: si il y a des enfants ou plus de deux adultes au moins, la fenêtre de l'offre la moins chère apparait sur la page de l'hôtel 
        if (kids>0 or adults>2):
            #choix du nombre de chambres si il a été donné par l'utilisateur
            if (chambres!=1):
                searching=driver.find_elements(By.CSS_SELECTOR,'button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.e137a4dfeb.d1821e6945')
                bouton_chambre=searching[2]
                for i in range (chambres-1):
                    bouton_chambre.click()
                
            confirm = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            confirm.click()
            time.sleep(2)

            close_pop_up(driver)

            #accéder à la page de l'hôtel
            find_url = driver.find_element(By.CSS_SELECTOR, "a[data-testid='title-link']")
            data_url = find_url.get_attribute("href")

            if data_url:
                driver.get(data_url)
            else:
                print("No URL found.")

            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)

            #changer la devise en euro pour une meilleure comparaison
            devise_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='header-currency-picker-trigger']")
            devise_button.click()
            time.sleep(2)

            euro = driver.find_element(By.CSS_SELECTOR, "button[data-testid='selection-item']")
            euro.click()
            time.sleep(2)

            upper_half_html = driver.execute_script("return document.documentElement.outerHTML;")
            soup = BeautifulSoup(upper_half_html, "html.parser")

            time.sleep(2)

            scroll_until_element_visible(driver, By.XPATH, '//*[@id="group_recommendation"]/h3')

            #certains hôtels n'ont pas de taxes supplémentaire, nous devons donc prendre en considération les deux cas
            try:
                total_price_element = soup.find("table", {"class": "totalPrice-inner"})
                if total_price_element:
                    price_span = total_price_element.find("span", {"class": "prco-valign-middle-helper"})
                    taxes_span = total_price_element.find("div", {"class": "prd-taxes-and-fees-under-price"})

                    if price_span and taxes_span:
                        price_text = re.sub(r'\D', '', price_span.get_text(strip=True))
                        taxes_text = taxes_span.get_text(strip=True).split(":")[-1].strip()
                        taxes_text = re.sub(r'\D', '', taxes_text)

                        price = float(price_text)
                        print(f"Le prix le moins cher pour booking.com hors taxes est de: €{price}")

                        # Premier cas: il y a des taxes supplémentaires
                        if (taxes_text.isdigit()):
                            taxes_and_fees = float(taxes_text)
                            total_price = math.ceil(price + taxes_and_fees)
                            print(f"Le prix le moins cher pour booking.com avec taxes est de: €{total_price}")
                        # Deuxième cas: il n y a pas de taxes supplémentaires
                        else:
                            total_price=price

                        #prise et enregistrement du screenshot
                        driver.save_screenshot(filename)
                        print(f"Screenshot pris et enregistré sous le nom {filename}.")

                        screenshot = Image.open(filename)
                        screenshot.show()

                        #texte à insérer dans notre base de données mongodb
                        result = {
                            "hotel_name": name_hotel,
                            "date_arrival": date_arrival,
                            "date_departure": date_departure,
                            "number_of_adults": adults,
                            "number_of_children": kids,
                            "children_ages": kids_ages,
                            "price_without_taxes": price,
                            "price_with_taxes": total_price,
                            "proof_screenshot_path": filename  # Change here
                        }

                        try:
                            collection.insert_one(result)
                            print("Data successfully inserted into MongoDB.")
                        except Exception as e:
                            print(f"Error inserting data into MongoDB: {e}")

                        print(f"Inserting result into MongoDB: {result}")
                        insert_data_into_mongodb(result)

                    else:
                        print("Could not find price or taxes elements.")
                else:
                    print("Total price element not found.")
            
            except Exception as e:
                print(f"Error extracting prices: {e}")
        # Deuxième cas: il y a un ou deux adultes seulement et l'offre ne s'affiche pas dans la page de l'hôtel. l'offre la moins chère est présentée dans la page du résultat de recherche cependant.
            if (chambres!=1):
                bouton_chambre= WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id=":r9:"]/div/div[3]/div[2]/button[2]'))
            )
                for i in range (chambres-1):
                    bouton_chambre.click()
                
            confirm = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            confirm.click()
            time.sleep(2)

            devise_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='header-currency-picker-trigger']")
            devise_button.click()
            time.sleep(2)

            euro = driver.find_element(By.CSS_SELECTOR, "button[data-testid='selection-item']")
            euro.click()
            time.sleep(5)

            try:
                taxes_span = driver.find_element(By.XPATH,'//*[@id="bodyconstraint-inner"]/div[2]/div/div[2]/div[3]/div[2]/div[2]/div[3]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div[3]')
                taxes_text = taxes_span.text.replace("€", "").replace(",", "").replace(" ", "").split(":")[-1].strip()
                
                price_span = driver.find_element(By.CSS_SELECTOR,'span[data-testid="price-and-discounted-price"]')
                price_text = price_span.text.replace("€", "").replace(",", "").replace(" ", "")
                price = float(price_text)
                print(f"Le prix le moins cher pour booking.com hors taxes est de: €{price}")

                if taxes_text.isdigit():
                    taxes_and_fees = float(taxes_text)
                    total_price = math.ceil(price + taxes_and_fees)
                    print(f"Le prix le moins cher pour booking.com avec taxes est de: €{total_price}")
                else:
                    total_price=price

            except Exception as e:
                price_span = driver.find_element(By.CSS_SELECTOR,'span[data-testid="price-and-discounted-price"]')
                price_text = price_span.text.replace("€", "").replace(",", "").replace(" ", "")
                price = float(price_text)

                print(f"Le prix le moins cher pour booking.com hors taxes est de: €{price}")
                total_price=price

            driver.save_screenshot(filename)
            print(f"Screenshot pris et enregistré sous le nom {filename}.")

            screenshot = Image.open(filename)
            screenshot.show()

            result = {
                "hotel_name": name_hotel,
                "date_arrival": date_arrival,
                "date_departure": date_departure,
                "number_of_adults": adults,
                "number_of_children": kids,
                "children_ages": kids_ages,
                "price_without_taxes": price,
                "price_with_taxes": total_price,
                "proof_screenshot_path": filename  # Change here
            }

            try:
                collection.insert_one(result)
                print("Data successfully inserted into MongoDB.")
            except Exception as e:
                print(f"Error inserting data into MongoDB: {e}")

            insert_data_into_mongodb(result)


    finally:
        driver.quit()

if __name__ == "__main__":
    main()



