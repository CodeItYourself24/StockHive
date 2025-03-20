from fastapi import FastAPI, HTTPException
import os
import pandas as pd

app = FastAPI()

# Path to the folder containing stock CSV files
DATA_FOLDER = "daily_technical_data"

def daily_data():
    stock_list = []
    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".csv"):
            print(file)
            # Read the CSV file
            file_path = os.path.join(DATA_FOLDER, file)
            df = pd.read_csv(file_path)

            # Parse the Date column with explicit format
            try:
                print(df['Date'].head())  # Print the first few rows of the Date column
                df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d", errors='coerce')  # Adjust format if needed
                print("Parsed Dates:", df['Date'])
                df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
                if df.empty:
                    print(f"Skipped file {file}: No valid data.")
                    continue  # Skip empty dataframes

                latest_data = df.sort_values('Date').iloc[-1]  # Get the most recent row
                stock_details = {
                    "name": str(latest_data["Name"]),
                    "ticker": str(file.replace(".csv", "")),
                    "latest_date": latest_data["Date"].strftime("%d-%m-%Y"),
                    "open": float(latest_data["Open"]),
                    "high": float(latest_data["High"]),
                    "low": float(latest_data["Low"]),
                    "close": float(latest_data["Close"]),
                    "volume": int(latest_data["Volume"]),
                    "circuit": int(latest_data["Circuit"]),
                }
                print("Processed Stock Details:", stock_details)
                stock_list.append(stock_details)
            except Exception as e:
                print(f"Error processing file {file}: {e}")
    return stock_list

@app.get("/technical")
def get_stocks():
    stocks = daily_data()
    return {"stocks": stocks}



@app.get("/technical/daily/{ticker}")
def get_daily_data(ticker: str):
    # Construct the file path for the given ticker
    file_path = os.path.join(DATA_FOLDER, f"{ticker}.csv")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Data for ticker '{ticker}' not found.")
    
    # Read the CSV file
    try:
        df = pd.read_csv(file_path)

        # Parse the Date column
        df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d", errors='coerce')
        df = df.dropna(subset=['Date'])  # Drop rows with invalid dates
        df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
        # Convert the data to a list of dictionaries for JSON serialization
        data = df.sort_values('Date').to_dict(orient="records")

        # Return the JSON response
        return {
            "ticker": ticker,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data for ticker '{ticker}': {str(e)}")






if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
