# NETRA: understand a website without the jargon

NETRA is an outside checkup of a website. It reads selected public records, explains the observed protections, and helps you plan practical improvements. It does not enter private accounts or try to break into the website.

See [every workspace panel explained](WORKSPACE_PANELS.md), including the new Google search assistant, evidence review, accuracy lab and backup workflow. The same explanations are available inside **Workspace guide**.

## Start in three steps

1. Open http://127.0.0.1:8001. If the app is stopped, run `python run_netra.py` from the project folder.
2. Enter a website name such as `example.com`, or paste its full address, and choose **Check website**. For a network-free demonstration, choose **Try example**.
3. Read the **Website checkup** summary, then open **My action plan** to decide who should handle each next step.

The example is fictional and is labeled as example data. It is not a real organization’s security result.

## Read the result correctly

- **Higher is better:** the score starts at 100, then subtracts points for specific observed gaps. A score of 70 does not mean a 70% chance of safety. Even 100 does not mean a website is completely secure.
- **Looks as expected:** the configured check observed the expected control or condition. The check has a limited scope.
- **Needs attention:** evidence supports a gap in one of the checked settings.
- **Worth reviewing:** an advisory item that does not remove points. For example, certificate-issuer rules may be inherited from a parent domain.
- **Could not check:** a source was unavailable or there was not enough evidence. An unanswered check is not counted as a security failure.
- **Checks observed:** how many of NETRA’s configured checks had usable information. Full coverage is not a full audit of the website.

Click one of the four result-count cards to filter the explanations. Choose **All checks** to see the full list. Each card explains the check with an everyday comparison, describes why it matters, and suggests what to do. Technical names and evidence are inside an expandable detail section.

## Turn the result into action

Open **My action plan**. For each observed gap:

1. Name the person or team to ask.
2. Set the progress to **To do**, **In progress**, or **Ready to recheck**.
3. Add a note and choose **Save action**.

These notes are saved on this computer with the checkup. They do not notify anyone or change the measured score. **Download action checklist** creates a text file you can share yourself. After changes have been made, use **Check this website again** and compare the new result with the earlier one.

## Explore what is public

**Public information** shows matching social/code links and document links in the sampled homepage. It also offers guided search queries for indexed pages, PDFs, spreadsheets, login pages, code references, and privacy information.

NETRA does not automatically run these searches. Opening a Google search shares that query and domain with Google. Public links may be intentional, and a link or search suggestion is not proof of a leak, ownership, or vulnerability. Fictional example links are displayed as text rather than opened.

## Compare and revisit results

**Past checkups** lets you search saved website names and reopen their results. **Compare results** compares the current checkup with an earlier one of the same domain and the same real/example mode.

A comparison calls out observed improvements, newly observed gaps, and checks that need another measurement. A numeric score change is shown only when both checkups use the same rules and have complete evidence for their configured checks.

**Multiple websites** accepts up to 10 website names, typed directly or imported from a text file or single-column CSV. Each website gets its own saved checkup. The summary is a local portfolio metric, not an industry ranking.

## Explain NETRA to an audience

1. Choose **Try example** and keep the fictional-data label visible.
2. Explain the headline and the distinction between a score and evidence coverage.
3. Choose **Present to an audience** for the six-step presentation. Use the buttons or left/right arrow keys; Escape closes it. Expand **Speaker notes** for talking points.
4. Show a finding, its everyday analogy, and the team who can help.
5. Save an action and explain that a plan is not proof of a completed fix.
6. Choose **Create improved demo**, then **Compare results** and select the earlier example. Both are fictional scenarios.
7. Use **Download audience handout** for a standalone HTML report. Open it in a browser and use Print / Save as PDF if needed.

Each checkup also includes a **60-second explanation** and a searchable **Translate the jargon** section. The explanation works without an AI key.

## When you need more detail

Expand **Advanced details** for the technical overview, recorded evidence, connection map, and technical fixes. The normal checkup and action plan are sufficient for a non-technical presentation.

Optional Gemini explanations require server configuration. AI explains the recorded findings; it does not decide the score. No independent exploit verification or compliance certification is provided.
