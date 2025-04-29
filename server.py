from fastapi import FastAPI, Query
from typing import List
import subprocess
import os
import shutil
from datetime import datetime

app = FastAPI()

# Configuration
LOCAL_REPO_BASE = r""   #it shoukd be the path to the folder where the node id(sensor) are stored
BRANCH = "main"
LOG_FILE = os.path.join(LOCAL_REPO_BASE, "update_logs.txt")

@app.post("/update-node/")
async def update_node(node_id: str = Query(...)):
    return await process_node_update(node_id)

@app.post("/update-multiple-nodes/")
async def update_multiple_nodes(node_ids: List[str] = Query(...)):
    results = {}
    for node_id in node_ids:
        result = await process_node_update(node_id)
        results[node_id] = result
    return results

async def process_node_update(node_id):
    repo_path = os.path.join(LOCAL_REPO_BASE, node_id)
    backup_path = os.path.join(LOCAL_REPO_BASE, f"{node_id}_backup")

    if not os.path.exists(repo_path):
        log(f"ERROR: Node {node_id} does not exist.")
        return {"error": f"Node {node_id} does not exist."}

    try:
        # Backup
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        shutil.copytree(repo_path, backup_path)
        print(f"Backup created for {node_id}.")
        log(f"Backup created for {node_id}.")

        # Git pull
        result = subprocess.run(
            ["git", "pull", "origin", BRANCH],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"Update successful for {node_id}.")
            shutil.rmtree(backup_path)  # Remove backup after success
            log(f"SUCCESS: Updated {node_id}")
            return {"message": f"Node {node_id} updated successfully."}
        else:
            print(f"Update failed for {node_id}: {result.stderr}")
            rollback(repo_path, backup_path)
            log(f"ERROR: Update failed for {node_id}. Rolled back.")
            return {"error": f"Update failed for {node_id}. Rolled back."}

    except Exception as e:
        print(f"Exception during update for {node_id}: {e}")
        rollback(repo_path, backup_path)
        log(f"EXCEPTION: {e}")
        return {"error": f"Exception during update for {node_id}. Rolled back."}

def rollback(repo_path, backup_path):
    if os.path.exists(backup_path):
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        shutil.copytree(backup_path, repo_path)
        print("Rollback successful.")
        log("Rollback successful.")
    else:
        print("No backup found to rollback.")
        log("No backup found to rollback.")

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")
