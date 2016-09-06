How to make a new draft version of the CWL spec

1. Duplicate prior directory to "vNewVersion-dev1" or "vExistingVersion-devN+1'
   in a branch
2. Update references to the new draft name.
3. Pull in the latest metaschema, where `schema_salad_repo` is the remote
   repository for the schema salad tool.
     
     git fetch --all
     git subtree add -P v1.1.0-dev1/salad schema_salad_repo/master

4. In the reference implementation (cwltool): make a new branch, and update the
   subtree checkout of the spec:
  
     git subtree merge --squash -P cwltool/schemas/ cwl_repo/v1.1.0-dev1
   
   Where `cwl_repo` is the remote repository for the CWL specifications.
4. In the reference implementation, teach it about the new draft version:

  a. Edit `cwltool/update.py`: append a new entry to the updates dictionary and
     change the previous last version to point to an update function
  b. Edit `cwltool/process.py`: update `get_schema` to look in the new
     directory
  c. Edit `setup.py` to include the new schemas in the `package_data` stanza
