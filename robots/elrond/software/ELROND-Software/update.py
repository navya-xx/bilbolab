from utils.github import download_folder_from_github, download_file_from_github


if __name__ == '__main__':
    download_folder_from_github(
        repo_url="https://github.com/dustin-lehmann/BILBO.git",
        folder_path='/software/robot/software/TWIPR-Software/utils/',
        destination='~/test_checkout/'
    )