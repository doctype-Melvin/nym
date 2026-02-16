from fastapi import FastAPI, HTTPException
import sqlite3
import pandas as pd
from pydantic import BaseModel

app = FastAPI(title = 'ComplyAPI')
DB_PATH = "complyable_vault.db"

class ApprovalRequest(BaseModel):
    filepath: str
    final_text: str
    integrity_hash: str

@app.get("/pending")
def get_pending():
    connect = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM pending_review WHERE status = 'PENDING", connect)
    connect.close()
    return df.to_dict(orient='records')

@app.post("/commit")
def commit_file(approval: ApprovalRequest):
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    try:
        cursor.execute("UPDATE pending_review SET status ='APPROVED' WHERE filepath = ?", (approval.filepath,))
        cursor.execute("""
                       INSERT INTO final_commit (filepath, final_content, integrity_hash)
                       VALUES (?, ?, ?)
                       """, (approval.filepath, approval.final_text, approval.integrity_hash))
        
        connect.commit()
        return {"status": "success", "message": f"Document {approval.filepath} committed."}
    except Exception as e:
        connect.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        connect.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)