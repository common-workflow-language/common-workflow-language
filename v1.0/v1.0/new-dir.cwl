cwlVersion: v1.0
class: CommandLineTool
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing: |
       ${
          var samplename = null;
          var arr = [];
          var bam = RegExp('.*\\.bam$')
          for (var i in inputs.input.listing) {
            if (!(samplename)) {
              if (inputs.input.listing[i].basename.match(bam)) {
                samplename = inputs.input.listing[i].basename.split('.')[0];
              }
            }
          }
          var inputdir = {"class": "Directory",
                          "basename": samplename,
                          "listing": inputs.input.listing};
          arr.push(inputdir)
          return arr;
        }
inputs:
  input: Directory
stdout: output.txt
outputs:
  out: stdout
  outdir:
    type: Directory
    outputBinding:
      glob: sample1
baseCommand: [ls, sample1/]