# MB_DemoCarApp

## Requirements

    Python 3.10 or 3.11 recommended
    Microsoft Access Database Engine (for '.accdb' support through ODBC driver)

    Download Access DB driver:  
    [https://www.microsoft.com/en-us/download/details.aspx?id=13255](https://www.microsoft.com/en-us/download/details.aspx?id=13255)

    Local installation of requirements.txt
    In Terminal run: 'pip install -r requirements.txt'

    Contents of requirements.txt

    pandas - For DataFrame operations, merging and transformations
    pyodbc - To connect and run SQL queries on MS Access database
    python-dotenv - To load environment variables from a .env file, like DB path
    pytest - To run unit tests and validate application logic
    openpyxl - To read/write Excel files
