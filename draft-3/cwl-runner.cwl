#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: "cwl:draft-3"

description: |
 Generic interface to run a Common Workflow Language tool or workflow from the
 command line. To be implemented by each CWL implementation for use by users
 and for testing conformance to the standard.

inputs:
 - id: outdir
   type: string
   default: outdir
   inputBinding:
    - prefix: "--outdir"

 - id: quiet
   type: bool
   inputBinding:
    - prefix: "--quiet"

 - id: toolfile
   type: File

 - id: jobfile
   type: File

 - id: conformance-test
   type: bool
   inputBinding:
    - prefix: "--conformance-test"

 - id: basedir
   type: string
   inputBinding:
    - prefix: "--basedir"

 - id: no-container
   type: bool
   inputBinding:
    - prefix: "--no-container"

 - id: tmp-outdir-prefix
   type: string
   inputBinding:
    - prefix: "--tmp-outdir-prefix"

 - id: tmpdir-prefix
   type: string
   inputBinding:
    - prefix: "--tmpdir-prefix"

baseCommand: cwl-runner

