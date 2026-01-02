You are playing as {country}.

**REFLECT PHASE** — Organize your thoughts and finalize orders.

You've done your analysis in debrief and submitted preliminary orders in react. Now finalize everything.

**ORGANIZE YOUR COUNTRY FOLDER:**
Review your {scratchpad_file} scratchpad and structure the important insights into permanent files:
- **strategy.md** - Your current strategic plan and priorities
- **threats.md** - Key threats and how to address them
- **observations.md** - What you've learned about other powers

Use mode="edit" to replace file contents, mode="append" to add to existing files, or mode="delete" to remove outdated files.

<FILE name="strategy.md" mode="edit">Your strategy here...</FILE>

**FINALIZE YOUR ORDERS:**
Review and update your {orders_file} if needed.

**BEFORE SUBMITTING:** Check your {lessons_file} if it exists. Don't repeat mistakes.

<FILE name="{orders_file}" mode="edit">Your orders here...</FILE>

**NO MESSAGING:** Gunboat mode - no communication allowed.

---

{context}

---

Organize your files, then finalize your orders to {orders_file}.

{block:order_format}

{if:wipe_void}
**NOTE:** Your {scratchpad_file} will be cleared after this response. Make sure to save anything important to your other files before it's wiped.
{endif}
