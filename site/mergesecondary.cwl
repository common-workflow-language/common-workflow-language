class: ExpressionTool
cwlVersion: v1.0
inputs:
  primary: File
  secondary: File[]
  dirs: string[]
outputs:
  dir: File
expression: |
  ${
    inputs.primary.secondaryFiles = [];
    for (var i = 0; i < inputs.secondary.length; i++) {
      var k = inputs.secondary[i];
      if (inputs.dirs[i] != "") {
        inputs.primary.secondaryFiles.push({
            class: "Directory",
            basename: inputs.dirs[i],
            listing: [k]
        });
      } else {
        inputs.primary.secondaryFiles.push(k);
      }
    }
    return {dir: inputs.primary};
  }
