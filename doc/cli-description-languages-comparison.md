# Comparison of Command Line Interface description languages

## Compared languages

* Galaxy: https://github.com/galaxyproject/galaxy/blob/dev/lib/galaxy/tools/xsd/galaxy.xsd
* CTD: https://github.com/WorkflowConversion/CTDSchema/blob/master/CTD.xsd
* CWL: https://github.com/common-workflow-language/common-workflow-language/blob/master/v1.0/CommandLineTool.yml


## Comparison table

|Galaxy information   |Optional   |CTD information   |Opti onal  |CWL information   |Optional   |
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