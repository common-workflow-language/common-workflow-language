cwlVersion: v1.0
class: CommandLineTool
hints:
  ResourceRequirement:
    ramMin: 8
requirements:
  SchemaDefRequirement:
    types: 
      - name: vcf2maf_params
        type: record
        fields:
          species:
              - "null"
              - type: enum
                symbols: [homo_sapiens, mus_musculus]
          ncbi_build:
              - "null"
              - type: enum
                symbols: [GRCh37, GRCh38, GRCm38]
inputs:
  first: vcf2maf_params
baseCommand: echo
arguments:
  - prefix: species
    valueFrom: $(inputs.first.species)
  - prefix: ncbi_build
    valueFrom: $(inputs.first.ncbi_build)
outputs:
  result: stdout

