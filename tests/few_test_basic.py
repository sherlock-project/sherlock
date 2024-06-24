import sherlock_project

#from sherlock.sites import SitesInformation
#local_manifest = data_file_path=os.path.join(os.path.dirname(__file__), "../sherlock/resources/data.json")

def test_username_via_message():
    sherlock_project.__main__("--version")
