#!/usr/bin/env cwl-runner
  
class: CommandLineTool
id: Example tool 
label: Example tool 
cwlVersion: v1.0 
doc: |
    An example tool demonstrating metadata. Note that this is an example and the metadata is not necessarily consistent.  

requirements:
  - class: ShellCommandRequirement

inputs:
  bam_input:
    type: File
    doc: The BAM file used as input
    format: http://edamontology.org/format_2572
    inputBinding:
      position: 1

stdout: output.txt

outputs:
  report:
    type: File
    format: http://edamontology.org/format_1964
    outputBinding:
      glob: "*.txt"
    doc: A text file that contains a line count

baseCommand: ["wc", "-l"]

$namespaces:
  s: https://schema.org/

$schemas:
- http://dublincore.org/2012/06/14/dcterms.rdf
- http://xmlns.com/foaf/spec/20140114.rdf
- https://schema.org/docs/schema_org_rdfa.html

s:author:
  - class: s:Person
    s:id: https://orcid.org/0000-0002-6130-1021
    s:email: dyuen@oicr.on.ca
    s:name: Denis Yuen

s:contributor:
  - class: s:Person
    s:id: http://orcid.org/0000-0002-7681-6415
    s:email: briandoconnor@gmail.com
    s:name: Brian O'Connor
  - class: s:Person
    s:id: https://orcid.org/0000-0002-6130-1021
    s:email: dyuen@oicr.on.ca
    s:name: Denis Yuen


s:citation: https://figshare.com/articles/Common_Workflow_Language_draft_3/3115156/2
s:codeRepository: https://github.com/common-workflow-language/common-workflow-language
s:dateCreated: "2016-12-13"
s:license: https://www.apache.org/licenses/LICENSE-2.0

