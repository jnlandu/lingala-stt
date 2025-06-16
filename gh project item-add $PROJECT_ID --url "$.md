gh project item-add $PROJECT_ID --url "$ISSUE_URL"
``` :contentReference[oaicite:2]{index=2}  

You can keep the CSV under version control so the import script is idempotent.

---

## 3  Structure work the GitHub-native way

| Roadmap element | How it maps in GitHub |
|-----------------|-----------------------|
| **Epic** (“Core Authentication & User Management”) | A top-level **issue** labelled `Epic`. Turn each *User Story* into a **sub-issue** so progress rolls up automatically. :contentReference[oaicite:3]{index=3} |
| **User Story**  | Standard issue, `Type=User Story`, inside the epic. |
| **Technical tasks** | Keep as a **task-list** inside the story’s body. GitHub shows a real-time progress bar. :contentReference[oaicite:4]{index=4} |
| **Acceptance criteria** | Add to the story description or link to a Markdown file; no extra field needed. |
| **Phase** (Sprint window) | Use the **Phase** field you created or a label such as `phase:foundation`. |
| **Sprint** | Use the **Iteration** field or classic **Milestones** if you prefer. |

---

## 4  Track progress & assignments

* **Checkboxes** in task-lists give a visual bar on the epic & show progress in the Project table.  
* **Assignees** column comes for free in every Project row. Use `gh issue edit --add-assignee` for bulk ops. :contentReference[oaicite:5]{index=5}  
* Create a saved **Board view** grouped by **Iteration → Status** to run daily stand-ups.  
* Use labels like `backend`, `priority:p0`, `blocked` for quick filters.

---

## 5  Sprint milestones & deadlines

* If you stick to Milestones: `gh milestone create "Sprint 1" --due 2025-06-28`.  
* With **Iterations** you set the cadence once; new sprints appear automatically and items roll over when you drag them. (You can also add an automation rule that moves “Done” items to the archive at sprint end.) :contentReference[oaicite:6]{index=6}  

---

## 6  Link code to work items

* In a PR description add `Fixes #123`, `Closes #456`. The issue auto-closes when the PR merges, and both the issue and the PR stay linked in your Project. :contentReference[oaicite:7]{index=7}  
* `gh pr create --fill --add-project "$PROJECT_ID" --add-label backend` pushes the PR straight into the board.

---

## 7  Automations worth enabling

| Automation | Effect |
|------------|--------|
| **Status = In Progress** when first PR linked | Keeps board accurate without manual moves. |
| **Status = Done → Archive** after 2 days | Keeps the view lean. |
| **If story’s task-list 100 %** → prompt to close issue | Encourages hygiene. |

---

## 8  Day-to-day checklist for the team

1. **Sprint planning**: Drag backlog items into the upcoming iteration, set assignees & estimates.  
2. **During sprint**: Developers open PRs with `Fixes …`, tick off sub-tasks, and keep labels up-to-date.  
3. **Daily stand-up**: Filter board to `iteration:@current` → talk through blockers.  
4. **Sprint review**: Close any stray issues; mark the iteration complete; start the next one.  
5. **Retrospective**: Export the view as TSV if you need retrospective stats. :contentReference[oaicite:8]{index=8}  

---

