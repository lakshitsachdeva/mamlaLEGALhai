# RegulaTrace: what to say and what to click

This is a **10-minute talk**. Read the **Say** paragraphs aloud. The **Understand** lines are for you; you do not need to read them to the audience. For a shorter talk, use [the five-minute script](QUICK_PRESENTATION_GUIDE.md).

## Before people arrive

1. From the repository folder, run `sh ./start-regulatrace.sh`.
2. Open `http://127.0.0.1:8000/#executive` and check that the API is connected.
3. Click **Load demo data** and wait for the success message. This prepares the example analysis, comparison, version changes, and synthetic checks.
4. Keep the [modality score figure](../paper/regulatrace-preprint/figures/deontic_proxy_scores.png) and [regulatory-function score figure](../paper/regulatrace-preprint/figures/regulatory_binary_scores.png) ready.
5. You can click **Present** to make the app cleaner on a projector. Version compare and Contradiction Lab use fictional examples.
6. If demonstrating InLegalBERT, install `requirements-neural.txt` and run the neural check once before presenting; the first use downloads model weights. Keep **Run Z3 only** as a reliable fallback.

## 0:00–1:00 — The problem

**Show:** The **Presentation** screen.

**Say:** “Regulations often specify who must do something, what they must do, and when. If software gives us only a confident summary, we cannot easily check whether it got those details right. RegulaTrace starts with a simpler goal: propose a duty, then keep the exact source text beside it so a person can verify it.”

**Understand:** A duty record is a small form with fields such as actor, action, deadline, and source quote. The quote can be found in the supplied document. That does not prove that the document is official or that every proposed field is correct.

## 1:00–3:00 — One proposed duty

**Click:** **Obligation Lab** → open one record. Point to the source quote, then the proposed actor, action, and timing. If comfortable, click **Correct fields**, change one field, save it, and show the review history. You can open **Evidence Graph** to show the source-to-record-to-review path.

**Say:** “Here is the text we supplied. The app splits it into clauses and uses explicit wording, such as ‘must’ or ‘shall,’ to propose a record. We can see who it thinks must act, what action it found, and the exact words behind that suggestion. If I correct a field, the app keeps a record of the change. A human still needs to interpret the rule.”

**Understand:** Live extraction is mainly rule based. The paper's SVM and logistic regression models do not fill these fields. The Evidence Graph is a visual audit path, not a Neo4j database.

## 3:00–4:00 — A changed policy

**Click:** **Version compare**. Read one old/new pair.

**Say:** “This is a fictional policy revision. Account reviews change from every 90 days to every 60 days. Evidence retention changes from 12 to 24 months. The app flags those edits so a reviewer knows where to look. It does not automatically know why the policy changed or what a regulator intended.”

**Understand:** This view compares wording and proposes review signals. Any explanation of the reason for a change is an inference, not verified legislative intent.

## 4:00–5:00 — A conditional conflict

**Click:** **Contradiction Lab** → **Load example**. Review the quotes and fields, tick the confirmation box, then click **Run InLegalBERT + Z3**. Point first to the relatedness score, then to the separate `UNSAT` result. If the optional model is unavailable, click **Run Z3 only**.

**Say:** “In this fictional example, the same records team is required to delete a test record and forbidden to delete it during the same period. InLegalBERT gives us a rough signal that the two passages are related. That score cannot tell us whether they contradict. After we check the structured fields, Z3 separately shows that these two entered requirements cannot both hold. A person must still check that the fields accurately represent the source text.”

**Understand:** InLegalBERT is a pretrained encoder, not a trained contradiction classifier. Its cosine score is uncalibrated. `UNSAT` is a mathematical result about manually structured inputs. Neither is a legal ruling or measured contradiction-detection accuracy.

## 5:00–7:30 — The research result

**Show:** The [modality figure](../paper/regulatrace-preprint/figures/deontic_proxy_scores.png), then the [regulatory-function figure](../paper/regulatrace-preprint/figures/regulatory_binary_scores.png).

**Say:** “We tested the rules on two different published sentence-label datasets. The first asks whether wording expresses an obligation, permission, prohibition, right, or power. Our rules scored 92.2% accuracy. But the dataset contains many obligations, and the macro F1 was only 0.543. Macro F1 checks performance across the different labels instead of letting the largest class dominate.”

**Say:** “The second dataset asks a harder, different question: does a sentence actually place a regulatory duty on someone, or does it describe how a legal system works? Words such as ‘shall’ appear in both kinds of sentence. Our rules scored only 41.9% mean accuracy. A simple word-based SVM scored 85.2% on this same second task. So spotting obligation-sounding words is not enough to understand what a legal sentence is doing.”

**Understand:** These percentages are **not** scores for the whole app or for extracting complete duties. Do not compare the 92.2% and 85.2% as if they came from the same exam. The SVM is a separate paper experiment, not the engine behind the live extraction.

## 7:30–9:00 — What is missing

**Say:** “The clear failure is useful. Rules based on words like ‘shall’ can find candidate duties, but they also flag statements that do not assign an actionable duty. The current app can merge two actions from one clause, and it can miss meaning that depends on another section. Showing the source text makes those mistakes easier to inspect.”

**Say:** “The next study needs experts to mark the exact duty passages and fields in documents we have not used for development. Then we can test whether reviewers using RegulaTrace are faster or more accurate than reviewers without it. We have not measured that yet.”

**Understand:** The in-app **16/16** challenge suite contains examples we wrote. It checks that those cases run; it does not estimate performance on unseen laws. The external datasets label sentences, not every duty field or reviewer outcome.

## 9:00–10:00 — Finish

**Say:** “RegulaTrace is a research prototype for reviewable regulatory analysis. It proposes duties, preserves their source text, records corrections, and can check a carefully stated rule conflict. Our experiments show where simple rules work and where they fail. The aim is to make each result easy to question and the next research claim measurable.”

Stop there. Leave **Obligation Lab** or **Presentation** visible for questions.

## Likely questions — short answers

**Is 92.2% the accuracy of the product?** No. It is accuracy on one sentence-label task. We have not measured end-to-end extraction accuracy on independently annotated documents.

**Why is 41.9% low?** The rules called almost every sentence regulatory because modal words appeared in both classes. That is a documented failure.

**What is macro F1?** A score that balances precision and recall for each label, then averages across labels. It helps reveal weak minority classes.

**Does Z3 prove real laws contradict?** No. It checks whether the two structured rules we entered can coexist under their stated assumptions.

**Are InLegalBERT, DSPy, or Neo4j in this build?** The optional InLegalBERT encoder now scores quote relatedness before the reviewer-guided Z3 check. DSPy and Neo4j are not implemented. The paper's classifier scores are separate experiments.

**Does the app certify compliance?** No. It helps a qualified reviewer inspect possible duties and their evidence.

## Backup numbers — use only if asked

| Experiment | Data | Rules | Other result |
| --- | --- | --- | --- |
| Five-class modality | 566 distinct texts; 3 similarity-grouped folds | 92.2% accuracy; 0.543 macro F1 | Word TF-IDF logistic regression: 0.499 macro F1 |
| Regulatory versus constitutive | 5,831 distinct sentences from 379 acts; 3 act-grouped folds | 41.9% mean accuracy; 0.588 regulatory F1 | Word TF-IDF linear SVM: 85.2% mean accuracy; 0.810 regulatory F1 |

The 41.9% is the mean of three fold accuracies; pooling predictions gives 42.8%. The [paper source](../paper/regulatrace-preprint/main.tex) and [experiment README](../research/experiments/README.md) give the full method. The PDF in `output/pdf/` is an older export; use the current paper source/editor preview for these results.
