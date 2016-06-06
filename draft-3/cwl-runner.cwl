#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: "cwl:draft-3"

description: |
 Generic interface to run a Common Workflow Language tool or workflow from the
 command line. To be implemented by each CWL compliant execution platform for
 testing conformance to the standard and optionally for use by users.

inputs:
 - id: outdir
   type: string
   default: outdir
   description: |
    Output directory, defaults to the current directory
   inputBinding:
    prefix: "--outdir"

 - id: quiet
   type: boolean
   description: no diagnostic output
   inputBinding:
    prefix: "--quiet"

 - id: toolfile
   type: [ "null", File ]
   description: |
    The tool or workflow description to run. Optional if the jobfile has a
    `cwl:tool` field to indicate the tool or workflow description to run.
   inputBinding:
    position: 1

 - id: jobfile
   type: File
   inputBinding:
    position: 2

 - id: conformance-test
   type: boolean
   inputBinding:
    prefix: "--conformance-test"

 - id: basedir
   type: string
   inputBinding:
    prefix: "--basedir"

 - id: no-container
   type: boolean
   description: |
    Do not execute jobs in a Docker container, even when listed as a Requirement
   inputBinding:
    prefix: "--no-container"

 - id: tmp-outdir-prefix
   type: string
   description: |
    Path prefix for temporary directories. Useful for OS X so that boot2docker
    writes to /Users
   inputBinding:
    prefix: "--tmp-outdir-prefix"

 - id: tmpdir-prefix
   type: string
   description: |
    Path prefix for temporary directories
   inputBinding:
    prefix: "--tmpdir-prefix"

baseCommand: cwl-runner

stdout: output-object.json

outputs:
 - id: output-object
   type: File
   outputBinding:
     glob: output-object.json
