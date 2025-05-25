import os

DATA_FOLDER = "test_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

def generate_file(file_path, size_mb):
    if not os.path.exists(file_path):
        print(f"Membuat file {file_path} sebesar {size_mb}MB...")
        with open(file_path, "wb") as f:
            f.write(os.urandom(size_mb * 1024 * 1024))
    else:
        print(f"File {file_path} sudah ada, dilewati.")

generate_file(os.path.join(DATA_FOLDER, "file10MB.bin"), 10)
generate_file(os.path.join(DATA_FOLDER, "file50MB.bin"), 50)
generate_file(os.path.join(DATA_FOLDER, "file100MB.bin"), 100)

