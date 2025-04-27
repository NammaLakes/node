import os
import subprocess
import requests
import shutil

# Configuration
REPO_OWNER = "NammaLakes"
REPO_NAME = "node"
BRANCH = "main"
LOCAL_REPO_PATH = r"local_repo_path"    
BACKUP_PATH = ""  #add if this is  a private repo 

# GitHub API URL for commits
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={BRANCH}"

# Optional: GitHub Personal Access Token
GITHUB_TOKEN = ""  # keep empty if public repo


def get_latest_commit():
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        commits = response.json()
        return commits[0]["sha"] if commits else None
    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: {e}")
        return None


def get_local_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=LOCAL_REPO_PATH,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error getting local commit: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception getting local commit: {e}")
        return None


def create_backup():
    try:
        if os.path.exists(BACKUP_PATH):
            shutil.rmtree(BACKUP_PATH)
        shutil.copytree(LOCAL_REPO_PATH, BACKUP_PATH)
        print("Backup created successfully.")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def restore_backup():
    try:
        if os.path.exists(BACKUP_PATH):
            if os.path.exists(LOCAL_REPO_PATH):
                shutil.rmtree(LOCAL_REPO_PATH)
            shutil.copytree(BACKUP_PATH, LOCAL_REPO_PATH)
            print("Rollback successful.")
        else:
            print("No backup found to restore.")
    except Exception as e:
        print(f"Error restoring backup: {e}")


def update_repository():
    if create_backup():
        try:
            print("Pulling latest changes from GitHub...")
            result = subprocess.run(
                ["git", "pull", "origin", BRANCH],
                cwd=LOCAL_REPO_PATH,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("Repository updated successfully.")
                shutil.rmtree(BACKUP_PATH)
            else:
                print(f"Update failed: {result.stderr}. Restoring backup...")
                restore_backup()
        except Exception as e:
            print(f"Update process failed: {e}. Rolling back...")
            restore_backup()
    else:
        print("Skipping update due to failed backup.")


def main():
    print("Checking for updates...")
    latest_commit = get_latest_commit()
    local_commit = get_local_commit()

    if latest_commit and local_commit:
        if latest_commit != local_commit:
            print("New update found! Applying changes...")
            update_repository()
        else:
            print("No new updates available.")
    else:
        print("Could not retrieve commit data.")


if __name__ == "__main__":
    main()
