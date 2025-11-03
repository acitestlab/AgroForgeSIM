from fastapi import FastAPI
app = FastAPI()

@app.post("/simulate")
def simulate(payload: dict):
    # payload: fields[], cropParams, weather[], management
    # return: timeseries + yield + harvest plan
    pass

@app.get("/runs/{id}/results.csv")
def download_results(id: str): ...
