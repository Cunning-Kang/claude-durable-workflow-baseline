# Native Task Translation

> **Status: Reference Only** — Superpowers 任务执行路径已覆盖此文档的核心功能。此文件保留作为架构说明，不再作为强制操作面。

## Goal
Translate one durable task into a small, session-safe native task list.

## Translation rule
For one durable task file, extract only:
- goal
- scope
- acceptance
- immediate blocker, if any
- evidence requirements

Then create the minimum native session tasks needed to move it forward.

## Good translation
Durable task:
- one durable outcome

Native tasks:
- inspect required files
- implement bounded change
- run verification
- update durable status if milestone changed

## Bad translation
- copy the entire durable task file into native tasks
- create a second long-lived backlog
- mirror every status field
- keep native tasks after the session as authoritative state
