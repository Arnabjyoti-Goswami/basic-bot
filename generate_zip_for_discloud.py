import os
import zipfile


def create_zip(zip_file_name: str, files_to_zip: list[str]) -> None:
    with zipfile.ZipFile(zip_file_name, "w") as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
                print(f"Added {file_path} to {zip_file_name}")
            else:
                print(f"Warning: {file_path} does not exist.")


if __name__ == "__main__":
    current_script_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(current_script_path)

    discloud_config_file = os.path.join(root_dir, "discloud.config")
    bot_file = os.path.join(root_dir, "src", "bot.py")
    utils_file = os.path.join(root_dir, "src", "utils.py")
    env_file = os.path.join(root_dir, ".env")
    requirements_file = os.path.join(root_dir, "requirements.txt")
    files_to_zip = [
        discloud_config_file,
        bot_file,
        utils_file,
        env_file,
        requirements_file,
    ]

    zip_file_name = "bot_archive.zip"

    create_zip(os.path.join(root_dir, zip_file_name), files_to_zip)
