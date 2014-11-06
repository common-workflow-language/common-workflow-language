# Workflow Description

This document briefly describes the workflow model currently used by rabix.

It is based on the abstract model defined by [wfdesc](http://wf4ever.github.io/ro/#wfdesc).
Tool descriptions are a specific Process type and Artifacts (data that is passed between Processes) are any JSON-compatible structures.

We have been using an encoding that's easy to read/write by hand. Example:

```yaml
steps:
  - id: bwa
    app: "http://example.org/apps/bwa.json#bwa_mem"
    inputs:
      reads:
        $from: fastq_mates  # exposes as workflow input
      reference:
        $from: fasta
      gap_open_penalty: 3
    outputs:
      bam: aligned  # expose as workflow output
  - id: freebayes
    app: "http://example.org/apps/freebayes.json"
    inputs:
      reads:
        $from: bwa.bam  # data link
      reference:
        $from: fasta  # same input as for bwa
    outputs:
      variants: vcf  # expose as "vcf" output
```

Data flowing through links can be of any JSON-compatible type.
 Most commonly, these are files, which are just JSON objects of certain structure with URLs pointing to actual files and their indices.

For simplicity, lists are given special treatment:
 - Data is automatically wrapped in lists to meet the expectations of an input port.
 - Lists are automatically concatenated when piped to same port from different sources.


## Parallel for-each

If a process receives a List<T> on a port which accepts T, it is automatically executed for each item in the list.
Likewise for nested lists of any depth (the structure is preserved on the output).

Port nesting level is determined by checking the innermost lists first (against the JSON-Schema definition of the port).
 It will be possible to change this to outermost-first in the workflow description.

In the case where multiple process ports receive nested data, Process will be executed for each combination.
 This will be changed to allow different strategies.


## Script Processes

For basic manipulation of (meta)data, we are using another Process type which simply evaluates an expression or script.
 This allows us to implement control structures such as GroupBy or Filter without running an external process in a container.
