import tomlkit


def get_project_meta(file):
    with open(file) as pyproject:
        file_contents = pyproject.read()

    return tomlkit.parse(file_contents)["tool"]["poetry"]
