# 🏨 WebScraping_Booking 

A Python automation tool that uses **Selenium WebDriver** to scrape hotel prices from Booking.com and store the results in a **MongoDB database**.

This script allows users to search for a hotel, extract the **lowest available price (with and without taxes)**, capture a **screenshot proof**, and save all results for later analysis.

---

## 🚀 Features

- 🔎 Hotel search by name
- 📅 Dynamic date selection
- 👨‍👩‍👧 Guest configuration (adults, children, ages)
- 🛏️ Optional room selection
- 💶 Automatic currency conversion to Euro
- 📊 Price extraction:
  - Price without taxes
  - Price with taxes
- 📸 Screenshot capture as proof
- 🗄️ MongoDB integration:
  - Store search results
  - Avoid duplicate entries
- 🧠 Handles multiple Booking.com scenarios (hotel page vs search results page)
- 🪟 Automatic pop-up handling

---

## ⚙️ Requirements

- Python 3.7+
- Google Chrome installed
- MongoDB Atlas account (or local MongoDB instance)

### Python Libraries

Install dependencies with:

```bash
pip install selenium pillow beautifulsoup4 pymongo
```

---

## 📦 Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

2. Update MongoDB connection string in the script:

```python
client = MongoClient("your-mongodb-uri")
```

⚠️ **Important**  
Never expose your MongoDB credentials in public repositories. Use environment variables instead.

3. Update ChromeDriver path if needed:

```python
service = Service(r"path/to/chromedriver.exe")
```

4. (Optional) Update screenshot save location:

```python
folder_path = r"C:\path\to\your\folder"
```

---

## ▶️ Usage

Run the script:

```bash
python pymongo_version.py
```

Then follow the prompts:

- Enter hotel name  
- Enter arrival date (`xx Mois xxxx`)  
- Enter departure date (`xx Mois xxxx`)  
- Enter number of adults  
- Enter number of children  
- Enter children ages (if applicable)  
- Choose number of rooms (optional)  

---

## 📅 Date Format

Dates must follow:

```
DD Month YYYY
```

### ✅ Examples:
- `05 Janvier 2025`
- `12 Mars 2024`

---

## 🧠 How It Works

1. **User Input**
   - Validates dates and inputs

2. **Web Automation**
   - Opens Booking.com
   - Inputs search criteria
   - Navigates dynamically

3. **Scraping**
   - Uses Selenium + BeautifulSoup
   - Extracts:
     - Base price
     - Taxes (if available)
     - Total price

4. **Screenshot**
   - Saves proof locally
   - Displays image

5. **Database Storage**
   - Stores results in MongoDB
   - Prevents duplicate entries based on:
     - Hotel
     - Dates
     - Guests configuration

---

## 🗂️ Data Stored in MongoDB

Each document contains:

```json
{
  "hotel_name": "...",
  "date_arrival": "...",
  "date_departure": "...",
  "number_of_adults": ...,
  "number_of_children": ...,
  "children_ages": [...],
  "price_without_taxes": ...,
  "price_with_taxes": ...,
  "proof_screenshot_path": "..."
}
```

---

## 🧩 Key Functions

- `valide()` → Validates date format  
- `get_user_input()` → Collects input  
- `select_date()` → Calendar navigation  
- `adjust_guests()` → Guest configuration  
- `get_kids_ages()` → Input children ages  
- `close_pop_up()` → Handles pop-ups  
- `scroll_until_element_visible()` → Dynamic scrolling  
- `insert_data_into_mongodb()` → Insert with duplicate check  
- `print_all_documents()` → Debug database contents  
- `main()` → Main workflow  

---

## 📸 Output

### Console:
- Price without taxes  
- Price with taxes  

### Files:
- Screenshot:
```
proof-<random_number>.png
```

### Database:
- Stored in MongoDB collection `booking_database`

---

## ⚠️ Important Notes

- Website structure may change → selectors may break
- Requires stable internet connection
- MongoDB credentials must be secured
- ChromeDriver version must match Chrome browser
- Some delays handled using `time.sleep()` and explicit waits

---

## 🛠️ Troubleshooting

- **MongoDB connection error**
  - Check URI and network access
  - Verify credentials

- **Duplicate data not inserted**
  - Script prevents duplicates by design

- **Element not found**
  - Booking.com structure may have changed

- **ChromeDriver error**
  - Ensure correct version is installed

- **Dates rejected**
  - Check format (`DD Month YYYY`)

---

## 🔐 Security Warning

⚠️ Do NOT expose:
- MongoDB connection string
- Passwords or API keys

Use environment variables for production:

```bash
export MONGO_URI="your-uri"
```

---

## 📜 License

This project is for educational purposes only.  
Use responsibly and respect Booking.com terms of service.

---

## 👩‍💻 Author

- **Eya Belkhodja**
