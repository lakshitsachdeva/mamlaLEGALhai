# mamlaLEGALhai: five-minute script

**Main point:** mamlaLEGALhai suggests what a rule requires and shows the exact text behind that suggestion so a person can check it.

Before presenting, run `sh ./start-mamlaLEGALhai.sh`, open `http://127.0.0.1:8000/#executive`, and click **Load demo data**. Version compare and Contradiction Lab use fictional examples.

1. **Presentation (30 seconds).** “Regulatory language is easy to summarize incorrectly. We want a proposed duty with its source text attached.”
2. **Obligation Lab (60 seconds).** Open a record. “The app proposes who must act, what they must do, and when. Here are the exact words it used. A reviewer can correct a mistake, and that correction is saved.”
3. **Version compare (45 seconds).** “In this fictional example, account reviews change from 90 to 60 days and evidence retention from 12 to 24 months. This flags edits for a person to inspect.”
4. **Contradiction Lab (60 seconds).** Click **Load example**, review the fields, tick the confirmation box, then **Run InLegalBERT + Z3**. “InLegalBERT gives a rough relatedness score for the quotes. Z3 separately checks the rules we entered. `UNSAT` means those rules cannot both hold under the shown assumptions; it does not prove real laws conflict.” If the optional model is unavailable, use **Run Z3 only**.
5. **Results (90 seconds).** Click **Research notes** in the left menu → **Read current paper** → **Jump to measured results**. Show the charts, then click **← mamlaLEGALhai research notes** at the top to return. “Our rules got 92.2% accuracy on a task that labels obligation-like wording, but only 41.9% mean accuracy on a different task that asks whether a sentence actually imposes a regulatory duty. A simple word-based SVM got 85.2% on that second task. Spotting words like ‘shall’ is not enough.”
6. **Close (15 seconds).** “This is a reviewable research prototype. We still need expert-labeled full documents and a reviewer study before claiming end-to-end accuracy or practical benefit.”

**Remember:** The percentages measure sentence-label experiments, not the accuracy of the whole app. Live extraction mainly uses rules; the SVM is a separate paper experiment. InLegalBERT quote similarity is uncalibrated, and Z3 uses manually structured inputs. The built-in 16/16 suite uses examples written by the team.

For the longer talk and likely questions, use [the full speaker notes](SPEAKER_NOTES.md). The [current paper PDF](../dist/docs/mamlaLEGALhai_Preprint.pdf) and [project report](../dist/docs/mamlaLEGALhai_Project_Report.pdf) are also linked on the website.
