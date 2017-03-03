cwlVersion: v1.0
class: Workflow

inputs: []

outputs:
  classout:
    type: File
    outputSource: compile/classout

requirements:
  - class: SubworkflowFeatureRequirement

steps:
  compile:
    run: 1st-workflow.cwl
    in:
      inp:
        source: create-tar/tar
      ex:
        default: "Hello.java"
    out: [classout]

  create-tar:
    requirements:
      - class: InitialWorkDirRequirement
        listing:
          - entryname: Hello.java
            entry: |
              public class Hello {
                public static void main(String[] argv) {
                    System.out.println("Hello from Java");
                }
              }
    in: []
    out: [tar]
    run:
      class: CommandLineTool
      requirements:
        - class: ShellCommandRequirement
      arguments:
        - shellQuote: false
          valueFrom: |
            date
            tar cf hello.tar Hello.java
            date
      inputs: []
      outputs:
        tar:
          type: File
          outputBinding:
            glob: "hello.tar"
