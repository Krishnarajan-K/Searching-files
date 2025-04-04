
# File Search Utility

Overview:

This Python script scans a specified folder for files and ranks them based on how well their filenames match a user-provided search term. The ranking is determined using a suitability score, which prioritizes exact matches, filenames that start with the search term, and occurrences of the search term within filenames.


## Features

-Lists all files in a specified folder.

-Calculates a suitability score based on how well filenames match the search term.

-Sorts results based on the score, number of occurrences, and filename.

-Uses environment variables to set the folder path.

-Handles errors for missing folders and permission issues.


## Installation



 1. Clone the repository or    download the script. git clone `<https://github.com/Krishnarajan-K/Searching_files.git>`




 2. Create and Activate a Virtual Environment:
 ``  python3 -m venv venv
``

 

 3.  Install Dependencies:
  `` pip install -r requirements.txt``

 4. set up Environment variables:
` echo REPO_PATH="C:/path/to/your/files" > .env`
 
 5. Run the FastAPI Server with Uvicorn :
 `uvicorn webpage_search.main:app --host 127.0.0.1 --port 8000 --reload
`







    
## Environment Variables
 This path is used to detect or search the files..

` REPO_PATH=C:\Users\user1\Desktop\BookStack_development `



## 🔗 Links
https://github.com/Krishnarajan-K/Searching-files.git

## Screenshots

[App Screenshot]![search](https://github.com/user-attachments/assets/0219cf1c-7268-4c37-998a-5a52e911477c)


![front page](https://github.com/user-attachments/assets/71ba5a2d-7981-4ea8-a187-dbf215b3d1e0)
