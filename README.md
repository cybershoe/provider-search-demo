Provider Search Demo
====================

## Prerequisites

- Access to a MongoDB Atlas cluster with permission to 
- python/pip
- npm/npx

## Installation

### Backend

1) Create a python environment and install prerequisites
```
cd service
python3 -m venv venv
source ./venv/bin/activate

pip install -r requirements.txt
```

2) Setup your MongoDB connection string as an environment variable
```
export MONGODB_URI="mongodb+srv://<username>:<password>@mycluster.mongodb.net/"
```

3) Load the example dataset and build the search index
```
python load_data.py < providers.json
python create_index.py < index.json
```

4) Start the service
```
fastapi dev app/app.py
```

You should now have the search API running at http://localhost:8000

### Frontend

In another terminal:

1) Install prerequisites
```
cd frontend
npm install
```

2) Launch the frontend app
```
npm start
```

You should now have the frontend app running at http://localhost:1234

> [!NOTE] If your API and frontend are not running on their default ports or 
> on different systems, set the `CORS_ORIGINS` environment variable to a 
> JSON-formatted list of origin URLs. 
> 
> eg:
> ```
> export CORS_ORIGINS="['https://10.0.0.240:8443','http://10.0.0.240:8080']"