

# Backend for the ChatBot using Langchain
## Setup
1. Clone the project 

2. ```cmd 
   cd Air-Ai-Flask
    ```
    
3. ```cmd 
   pip install virtualenv 
    ```  
    
4. ```cmd  
    virtualenv -p python3 venv 
    ```  
    
5. ```cmd   
    source venv/bin/activate 
   ```  

6. ```cmd  
    pip install -r requirements.txt
    ```  
before running you must populate the .env file with
``` env
   SECRET_KEY="  " you can get the api key from https://breezometer.com/products/air-quality-api free
   OPENAI_API_KEY="" openai key
 ```

## Develop
Run the app.py to start your 
```cmd  
    python app.py
  ```  
