def read_file(directory, file_name):
    start_page = directory / file_name

    with open(start_page, "r") as file:
        html = file.read()

    return html
