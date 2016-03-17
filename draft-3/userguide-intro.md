# A Gentle Introduction to the Common Workflow Language

Hello!

This guide will introduce you to writing tool wrappers and workflows using the
Common Workflow Language (CWL).  This guide describes the current stable
specification, draft 3.

<!--ToC-->

# Introduction

CWL is a way to describe command line tools and connect them together to create
workflows.  Because CWL is a specification and not a specific piece of
software, tools and workflows described using CWL are portable across a variety
of platforms that support the CWL standard.

CWL has roots in "make" and many similar tools that determine order of
execution based on dependencies between tasks.  However unlike "make", CWL
tasks are isolated and you must list all your inputs and outputs explicitly up
front.  This allows CWL implementations to take advantage of technologies such
as Docker containers makes CWL well suited for describing large-scale workflows
in cluster, cloud and high performance computing environments where tasks are
scheduled in parallel across many nodes.

# Wrapping Command Line Tools
