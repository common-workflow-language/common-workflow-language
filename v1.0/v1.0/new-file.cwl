cwlVersion: v1.0
class: CommandLineTool
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing: |
       ${
          var arr = [];
          var inputfile = {"class": "File",
                          "basename": "input.txt",
                          "contents": "hello world"};
          arr.push(inputfile);
          return arr;
        }
inputs: []
stdout: output.txt
outputs:
  out: stdout
baseCommand: [cat, input.txt]