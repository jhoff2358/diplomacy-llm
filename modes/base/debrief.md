You are playing as {country}.

{if:first_season}
**DEBRIEF PHASE** — A new game begins.

Study the board. Where are your units? Who are your neighbors? What opportunities and threats do you see?
{endif}

{if:not_first_season}
**DEBRIEF PHASE** — What happened last season?

Review the game history. Did anything surprise you? Did any of your orders fail? Did anyone break a promise or act unexpectedly?
{endif}

If there's anything worth remembering, write it to a file(s):

<FILE name="<filename>.md" mode="append">...</FILE>

You can use any filename. These files persist across seasons.

---

{context}
