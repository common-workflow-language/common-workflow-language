Common Workflow Language, Draft 2
=================================

Authors:
* Peter Amstutz <peter.amstutz@curoverse.com>, Curoverse
* Nebojsa Tijanic <nebojsa.tijanic@sbgenomics.com>, Seven Bridges Genomics

# Abstract

A Workflow is an analysis task which uses a directed graph to represent a
sequence of operations that transform an input data set to output.  This
specification defines the Common Workflow Language (CWL), a vendor-neutral
standard for representing Workflows intended to be portable across multiple
analytical computing platforms.  This specification defines two concrete
workflow operations, the Comand Line Tool, for invoking a command line program
(optionally within an operating system container) and capturing the output, and
the Expression Tool, for applying ECMAScript functions to the data set.

# Status of This Document

This document is the product of the [Common Workflow Language working
group](https://groups.google.com/forum/#!forum/common-workflow-language).  The
latest version of this document is available in the "specification" directory at
https://github.com/common-workflow-language/common-workflow-language

The products of the CWL working group (including this document) are made available
under the terms of the Apache License, version 2.

# Table of Contents

1. [Introduction](#introduction)
  1. [Introduction to draft 2](#introduction-to-draft-2)
  2. [Purpose](#purpose)
  3. [Dependencies on Other Specifications](#dependencies-on-other-specifications)
  4. [Requirements](#requirements)
  5. [Scope](#scope)
  6. [Terminology](#terminology)
2. [Concepts](#concepts)
3. [Syntax](#syntax)
4. [Data model](#data-model)
  1. [Parameters](#parameters)
  2. [Files](#files)
5. [Execution model](#execution-model)
6. [Process types](#process-types)
  1. [Workflow](#workflow)
  2. [CommandLineTool](#commandlinetool)
  3. [ExpressionTool](#expressiontool)

# Introduction

## Introduction to draft 2

## Purpose

## Dependencies on Other Specifications

## Requirements

## Scope

## Terminology

# Concepts

# Syntax

# Data model

## Parameters

## Files

# Execution model

# Workflow processes

# Command line tool processes

## Executing tools in Docker

# Expression tool processes
