# FoodRescue AI 🌱
### Smart Food Surplus Prediction and Rescue Platform

**FoodRescue AI** is a machine-learning-based prototype designed to help reduce food waste by predicting surplus food, prioritizing rescue requests, and matching available food with suitable receivers.

## 🚨 Problem Statement

Edible food is often wasted in colleges, hostels, restaurants, and events because surplus quantities are not identified early and suitable receivers may not be found in time.

## 💡 Our Solution

FoodRescue AI follows a simple workflow:

**Predict → Prioritize → Match → Rescue → Measure**

The platform estimates surplus food, assigns an urgency level, recommends suitable receivers, tracks rescue status, and displays impact statistics.

## ✨ Key Features

- **Food Surplus Prediction:** Estimates surplus meals using a machine learning model.
- **Urgency Prioritization:** Classifies requests by urgency to help identify high-priority cases.
- **Food Safety Prototype:** Displays preliminary rescue guidance based on food type and preparation time.
- **Receiver Matching:** Recommends receivers based on capacity and estimated distance.
- **Rescue Tracking:** Tracks whether a food donation has been rescued.
- **Impact Dashboard:** Displays donation records, estimated surplus, rescue status, and impact statistics.

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-learn, Random Forest Regressor
- **Database:** SQLite
- **Frontend:** HTML, CSS
- **Templating:** Jinja2
- **Data Processing:** NumPy, Pandas

## ⚙️ How It Works

1. Enter the expected number of people, food prepared, and previous surplus.
2. Select the food type and enter preparation time.
3. The model estimates the surplus quantity.
4. The application assigns an urgency level and displays prototype safety guidance.
5. The system recommends a suitable receiver.
6. Update the rescue status and review the dashboard.

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/anjalicodes-prog/FoodRescue-AI.git
cd FoodRescue-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment on Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

Open this address in your browser:

`http://127.0.0.1:5000`

## 🤖 Machine Learning Note

The current Random Forest model is a proof of concept trained on synthetic sample data. Its predictions must be validated using real historical food data before practical deployment.

## ⚠️ Food Safety Disclaimer

The food safety feature provides preliminary prototype guidance only. It does not certify food as safe to eat. Real-world rescue decisions must follow applicable food safety regulations and consider storage temperature, handling, contamination risks, and professional guidance.

## 🌍 Sustainable Development Impact

FoodRescue AI supports responsible consumption and production by aiming to reduce avoidable food waste and improve the coordination of surplus food donations.

## 🔮 Future Scope

- Integration with verified NGOs, food banks, and community kitchens.
- Real-time location and distance calculation.
- Improved prediction using real-world historical datasets.
- Notifications for urgent rescue requests.
- More detailed impact reporting.

## 👩‍💻 Project Information

**Project:** FoodRescue AI  
**Domain:** Sustainable Development  
**Repository:** https://github.com/anjalicodes-prog/FoodRescue-AI

*Developed as a hackathon prototype.*
