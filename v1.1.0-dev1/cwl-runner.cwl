#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0

doc: |
 Generic interface to run a Common Workflow Language tool or workflow from the
 command line. To be implemented by each CWL compliant execution platform for
 testing conformance to the standard and optionally for use by users.

inputs:
 outdir:
   type: string?
   doc: |
    Output directory, defaults to the current directory
   inputBinding:
    prefix: "--outdir"

 quiet:
   type: boolean?
   doc: no diagnostic output
   inputBinding:
    prefix: "--quiet"

 toolfile:
   type: File?
   doc: |
    The tool or workflow description to run. Optional if the jobfile has a
    `cwl:tool` field to indicate the tool or workflow description to run.
   inputBinding:
    position: 1

 jobfile:
   type: File
   doc: The input job document.
   inputBinding:
    position: 2

 no-container:
   type: boolean?
   doc: |
    Do not execute jobs in a Docker container, even when listed as a Requirement
   inputBinding:
    prefix: "--no-container"

 tmp-outdir-prefix:
   type: string?
   doc: |
    Path prefix for temporary directories. Useful for OS X so that boot2docker
    writes to /Users
   inputBinding:
    prefix: "--tmp-outdir-prefix"

 tmpdir-prefix:
   type: string?
   doc: |
    Path prefix for temporary directories
   inputBinding:
    prefix: "--tmpdir-prefix"

baseCommand: cwl-runner

stdout: cwl.output.json  # The CWL output document
