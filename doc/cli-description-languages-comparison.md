# Comparison of Command Line Interface description languages

## Compared languages

* Galaxy: 
* CTD: https://github.com/WorkflowConversion/CTDSchema/blob/master/CTD.xsd
* CWL: https://github.com/common-workflow-language/common-workflow-language/blob/master/v1.0/CommandLineTool.yml


## Comparison table

|Galaxy information   |Mandatory   |CTD information   |Mandatory   |CWL information   |Mandatory   |
|---|---|---|---|---|---|
|*description*   |X   |description   |X   |label   |X   |
|*help*   |X   |*manual*   |X   |*doc*   |X   |
|*citation*   |X   |*citation* (for the underlying tool, DOI or doc URL)   |X   |*SoftwareRequirement.name.specs* (URI)   |X  |
|   |   |*ExecutableName* (overrides the name attribute)   |X   |*SoftwareRequirement.name.baseCommand[0]* |X  |
|   |   |*ExecutablePath* (specific path to the executable)  |X   | | |
|*command*+*argument* under parameter |  |*CLItype* list of input commands with elements mapping   |X | *arguments* and/or *inputBindings*  |X   |

