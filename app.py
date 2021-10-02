from fastapi import FastAPI, HTTPException
import pandas as pd
import io
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse


def data(filepath: str):
    # file
    return pd.read_csv(filepath)


app = FastAPI()

path = "static"
file = {
    "nurtrition": "H27houkokusho2_01_nurtrition.csv",
    "enegy": "H27houkokusho2_56_enegy.csv",
}
        

@app.get("/")
def get_root():
    """health check

    Returns:
        (str): hello
    """
    return "hello"


def get_df(path, kind):
    return pd.read_csv(os.path.join(path, file.get(kind, "")))


@app.get("/csv")
def get_csv(kind: str = "nurtrition") -> dict:
    df = get_df(path, kind)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={file.get(kind, 'example.csv')}"

    return response


@app.get("/csv_str")
def get_json(kind: str = "nurtrition"):
    try:
        df = get_df(path, kind)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="file not found")
    except IsADirectoryError as e:
        raise HTTPException(status_code=404, detail=f"file not found: {e}")

    #return JSONResponse(content=jsonable_encoder(json_str))
    return df.to_csv()


@app.get("/json")
def get_json(kind: str = "nurtrition"):
    try:
        df = get_df(path, kind)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="file not found")
    except IsADirectoryError as e:
        raise HTTPException(status_code=404, detail=f"file not found: {e}")

    json_str = df.to_json(orient="records", force_ascii=False)
    #return JSONResponse(content=jsonable_encoder(json_str))
    return JSONResponse(content=json_str)


app.mount("/static", StaticFiles(directory="static"), name="static")
