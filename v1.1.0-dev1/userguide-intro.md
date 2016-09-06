# A Gentle Introduction to the Common Workflow Language

Hello!

This guide will introduce you to writing tool wrappers and workflows using the
Common Workflow Language (CWL).  This guide describes the current development
specification, version 1.1.0-dev1.

Note: This document is a work in progress.  Not all features are covered, yet.

<!--ToC-->

# Introduction

CWL is a way to describe command line tools and connect them together to create
workflows.  Because CWL is a specification and not a specific piece of
software, tools and workflows described using CWL are portable across a variety
of platforms that support the CWL standard.

CWL has roots in "make" and many similar tools that determine order of
execution based on dependencies between tasks.  However unlike "make", CWL
tasks are isolated and you must be explicit about your inputs and outputs.  The
benefit of explicitness and isolation are flexibility, portability, and
scalability: tools and workflows described with CWL can transparently leverage
technologies such as Docker, be used with CWL implementations from different
vendors, and is well suited for describing large-scale workflows in cluster,
cloud and high performance computing environments where tasks are scheduled in
parallel across many nodes.
