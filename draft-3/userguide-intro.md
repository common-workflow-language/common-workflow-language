# A Gentle Introduction to the Common Workflow Language

Hello!

This guide will introduce you to writing tool wrappers and workflows using the
Common Workflow Language (CWL).  This guide describes the current stable
specification, draft 3.

## What is CWL?

CWL is a standard way to describe command line tool and connect them together
to create workflows.  CWL enables you to write portable tools and workflows
that can run in a variety of platforms that support the CWL standard.

CWL has roots in "make" and many similar tools that determine order of
execution based on dependencies between tasks.  Unlike "make", CWL provides
strong isolation between tasks and requires that you list all your inputs and
outputs explicitly.  This allows CWL tools to be portable across different
platforms and makes CWL well suited for describing large-scale workflows in
cluster and cloud environments where many tasks are scheduled in parallel
across many nodes.

## Wrapping Command Line Tools
