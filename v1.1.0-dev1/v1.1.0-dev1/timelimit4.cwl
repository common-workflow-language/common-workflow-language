class: CommandLineTool
cwlVersion: v1.1.0-dev1
inputs: []
outputs: []
requirements:
  InlineJavascriptRequirement: {}
  TimeLimit:
    timelimit: $(1+2)
baseCommand: [sleep, "15"]
