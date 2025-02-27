import os
import shutil
import subprocess

def download_folder_from_github(repo_url, folder_path, destination):
    """
    Downloads a specific folder from a GitHub repository using sparse-checkout,
    manually editing .git/info/sparse-checkout so that only the specified folder
    (and its contents) are included.

    :param repo_url: The URL of the GitHub repository.
    :param folder_path: The path to the folder within the repo to download
                       (e.g., "software/robot/software/TWIPR-Software").
    :param destination: The destination directory where the folder will be saved.
    """
    # Create a temporary directory for the repository
    temp_dir = os.path.join(os.path.expanduser("~"), "temp_repo")

    # Ensure the temp directory doesn't already exist
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    try:
        # 1. Clone the repo with minimal checkout (no-checkout)
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, temp_dir],
            check=True
        )

        # 2. Change to the repo directory
        os.chdir(temp_dir)

        # 3. Enable sparse-checkout in non-cone mode
        subprocess.run(["git", "sparse-checkout", "init", "--no-cone"], check=True)

        # 4. Manually write the desired path to .git/info/sparse-checkout
        #    This ensures only folder_path (and its subdirectories) are checked out.
        folder_path_stripped = folder_path.strip("/")
        sparse_checkout_file = os.path.join(".git", "info", "sparse-checkout")
        with open(sparse_checkout_file, "w", encoding="utf-8") as f:
            # Trailing slash ensures we include subfolders inside folder_path_stripped.
            f.write(folder_path_stripped + "/\n")

        # 5. Finally, checkout the contents
        subprocess.run(["git", "checkout"], check=True)

        # 6. Move or copy the desired folder to the destination
        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)

        source_folder = os.path.join(temp_dir, folder_path_stripped)

        shutil.copytree(
            source_folder,
            os.path.join(destination, os.path.basename(folder_path_stripped)),
            dirs_exist_ok=True
        )

    finally:
        ...
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    download_folder_from_github(
        repo_url="https://github.com/dustin-lehmann/BILBO.git",
        folder_path='/software/robot/software/TWIPR-Software/utils/',
        destination='/home/admin/test_checkout/'
    )
