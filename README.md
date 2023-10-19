# Two Way Integration

 
 ## ✍️ Table of Contents
- [Project Breakdown](#project-breakdown)
- [About the Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributions](#contributions)

## 🔨 Project Breakdown 
- Building Local API which handles GET, POST, PUT and DELETE http requests. 
- Changes made to the Local DB will be reflected in Stripe test accounts.
- Changes made to the Stripe test account will be reflected in local db.

## 💻 About The Project
Zenskar Assignment for handling customer catalog and the system should be adaptable to different situations and different product catalogs.

### 🔧 Built With
  - FastAPI
  - Redis ~ Redis Queue for sending modification tasks to consumer and the producer can prcoess these tasks
  - SQLite ~ Local DB
  - SQLAlchemy ~ ORM for focusing on logic 
  - Stripe
  - Webhooks ~ for sending events from stripe to local endpoint
  - ngrok ~ for forward referencing local url to public endpoint
  

## 🚀 Getting Started
To get a local copy up and running follow these simple steps.

### 🔨 Installation
1. Clone the repo

```sh
git clone https://github.com/dhananjaypai08/Two-Way-Integration/
```

2. Create a Virtual Environment and activate

```sh
python3 -m venv [your_environment_name]
.\[your_environment_name]\Scripts\activate
```
3. Create .env file
   
Add STRIPE_API_KEY=[Your api key here]

- create a stripe account
- Install NGROK on your computer
- Start the ngrok terminal
- Write ```ngrok http 8000```
This would give a public endpoint mapped to localhost:port=8000

Add STRIPE_WEBHOOK_SECRET=[your webhook secret here] 

create a public webhook endpoint and add the ngrok terminal public provided and select events for customer that are ```customer_created, customer_updated, customer_deleted``` To track Inward modifications 

##### Format
```sh
STRIPE_API_KEY="api_key"
STRIPE_WEBHOOK_SECRET="webhook_secret"
```

4. Installing dependencies and requirements

```sh
cd Two-Way-Integration
pip3 install -r requirements.txt
```

5. Starting the Producer and consumer Service (Redis)

```sh
python inward.py
python outward.py
```

Note: Enter both commands in two different terminals

6. Running the model and the APP
```sh
python3 model.py 
python3 main.py
```

## 🧠 Usage
Built version:
- Python v3.10.5
- FastAPI v0.103.2

The Basic goal is to make two way syncing.

Inward: from Stripe account to Local server using webhooks and ngrok

Outward: from local server to Stripe account using stripe API

## 🏃♂️ Future Plans
- Containerization of services
- Integration of redis message broker to produce and consume tasks for the two sync
- Any changes to the resource catalog should be first sent to the message broker which will process these requests.
