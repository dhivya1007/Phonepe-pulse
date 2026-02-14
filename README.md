# Phonepe-pulse
This project extracts, transforms, and visualizes data from the official PhonePe Pulse GitHub repository by PhonePe to analyze India’s digital payment trends. Python processes the data, MySQL/PostgreSQL stores it, and Streamlit with Plotly delivers interactive dashboards for insights.

The dashboard enables:

📈 State-wise transaction analysis

💳 Payment category distribution

🛡️ Insurance penetration insights

📱 Device & brand usage trends

🗺️ India state-level choropleth visualization

🏆 Top & Bottom performing states and districts

🛠️ Tech Stack

Python

Streamlit – Interactive dashboard

Plotly Express – Data visualization

PostgreSQL – Data storage

SQLAlchemy – Database connection

Pandas – Data processing

📂 Project Structure
PhonePe-Project/
│
├── phone_pe files/                     # Raw datasets & GeoJSON
│   ├── *.csv                           # All extracted CSV data files
│   └── india_states.geojson             # GeoJSON file for India map visualization
│
├── phone_pe-data_extraction.ipynb       # Data extraction & transformation notebook
├── phone_pe-dashboard.py                # Streamlit dashboard application
│
└── README.md                            # Project documentation

📁 phone_pe files/

Contains:

Cleaned and transformed CSV files

india_states.geojson used for state-level choropleth map visualization

📓 phone_pe-data_extraction.ipynb

Extracts data from the PhonePe Pulse GitHub repository

Cleans and transforms JSON data

Converts data into structured CSV files

Prepares data for database upload (PostgreSQL)

📊 phone_pe-dashboard.py

Streamlit-based interactive dashboard

Connects to PostgreSQL database

Performs SQL queries

Generates visualizations using Plotly

Includes state-level and district-level analytics

Displays India choropleth map

📊 Dashboard Features
1️⃣ Home

Overview of PhonePe ecosystem

Dashboard purpose & insights

2️⃣ Data Exploration

Tabbed analytics for:

🔹 Aggregated Data

Insurance trends

Transaction growth analysis

User device & brand insights

Year & Quarter trend analysis

🔹 Map Data

District-wise transaction comparison

State-level engagement summary

Top 5 & Bottom 5 performance analysis

🔹 Top Data

Reserved for advanced ranked insights

3️⃣ India Map Visualization

Interactive state-wise choropleth map for:

Transaction Amount

Transaction Count

Insurance Amount

Insurance Count

App User Count

📈 Key Insights Generated

Identification of high-performing digital payment states

Regional transaction behavior comparison

Device dominance trends across states

District-level growth potential analysis

Payment-type contribution breakdown

⚙️ How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/yourusername/PhonePe-Project.git
cd PhonePe-Project
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Data Preparation (Optional)
If you want to extract or update the PhonePe data:
jupyter notebook phone_pe-data_extraction.ipynb
4️⃣ Set Environment Variable for Database (Recommended)
export DATABASE_URL="postgresql://username:password@host:port/dbname"
5️⃣ Run the Streamlit Dashboard
streamlit run phone_pe-dashboard.py
