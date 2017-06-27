# Comparison of Command Line Interface description languages

## Compared languages

* Galaxy v17.05: https://github.com/galaxyproject/galaxy/blob/release_17.05/lib/galaxy/tools/xsd/galaxy.xsd
* CTD v1.7.0 : https://github.com/WorkflowConversion/CTDSchema/blob/Version_1_7_0/CTD.xsd
* CWL v1.0: http://www.commonwl.org/v1.0/CommandLineTool.html / https://github.com/common-workflow-language/common-workflow-language/blob/master/v1.0/CommandLineTool.yml

## Summary

### Tool description
CTD reflects the perspective of a tool author targetting the KNIME processing unit approach ("nodes"), whereas 
Galaxy reflects the perspective of a platform centered around non-developer users interacting with a graphical interface.

### Parameters description

### Data/parameter types
The typing system for parameters in CTD itself is simpler than the other two, providing mainly support for simple types and input/output files, but excluding arrays/lists and complex types. Galaxy adds GUI specific features (`select`, `drill_down`), domain specific features (`color`, `genome_build`, `data_column`), configuration of web services (`base_url`), and tighter integration with workbench internal data management (`library_data`).

### Command line generation
All of the specifications include a flexible set of possibilities for the generation of command lines, reflecting the effective heterogeneity of the bioinformatics tools ecosystem ;)

## Comparison table

### Tool level

|Galaxy information   |Optional   |CTD information   |Optional  |CWL information   |Optional   |
|---|---|---|---|---|---|
|*description*   |X   |description   |X   |label   |X   |
|*help*   |X   |*manual*   |X   |*doc*   |X   |
|*citation*   |X   |*citation* (for the underlying tool, DOI or doc URL)   |X   |*SoftwareRequirement.name.specs* (URI)   |X  |
|   |   |*ExecutableName* (overrides the name attribute)   |X   |*SoftwareRequirement.name.baseCommand[0]* |X  | 
|   |   |*ExecutablePath* (specific path to the executable)  |X   | | |
|*command*+*argument* under parameter |  |*CLItype* list of input commands with elements mapping   |X | *arguments* and/or *inputBindings*  |X   |
| | |*logs* (retrospective on execution information - if so probably out of scope)|X | | |
|*tool/outputs/data/@from_work_dir* (name of file to consume)  |X |*relocators* (list of parameters, path pairs)|X |*outputBinding* |X |
|*@version* (version of wrapper)  |X |*@version* (apprarently version of the tool itself)| |*SoftwareRequirements.name.version* (list of known compatible versions of the underlying tool |X |
|*@name* (just an identifier, not used to build the command itself)||*@name* (also used to build the command itself, unlesss *ExecutableName* is provided)| |baseCommand[0]|X|
|often part of the *help* text|X|*docURL* (URL to documentation)||||
|*edam_topics* and *edam_operations* - categories are external to tool definition, in per-server config (toolconf.xml)|X|*category* (any string)|X|can use EDAM or other 3rd party annotation or derive via identifier from external registry or datatype|
|(often part of help text)|X|*tags*|X|||

### Parameter level 

**Important remark** The structure of the CTD file is slightly different, because it explicitely allows the definition of "sub-tools" through a nested structure of NODE/ITEM elements. A node is a subgroup of parameters, and ITEM is a parameter.
Therefore, to focus on Parameter-level information, we consider only the ITEM element here for parameter description in CTD.

|Galaxy information   |Optional   |CTD information   |Optional  |CWL information   |Optional   |
|---|---|---|---|---|---|
| *param* or *data* |  | *ITEM* |  | *inputs[n]* or *outputs[n]*  |  |
|*@name*||*@name*||key of *inp|uts* or *outputs* entry||
|*@type*||*@type* (Defines the possible types available in the type attribute of ITEM and ITEMLIST.)||type||

