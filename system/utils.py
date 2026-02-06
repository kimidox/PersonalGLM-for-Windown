
def get_project_path():
    import pathlib
    return pathlib.Path(__file__).parent.parent


if  __name__ == '__main__':
    project_pathe=get_project_path()

    print(project_pathe)