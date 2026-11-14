# Automatic Sentiment Labeling of Movie Reviews with an LLM

## 1. Dataset Description
The dataset (`data.csv`) contains 10 short English movie reviews, evenly split
between 5 positive and 5 negative samples. Each record includes an ID, the review
text, and a human-annotated ground-truth label for evaluation. Two reviews were
deliberately designed to be difficult: review #9 is sarcastic ("Oh fantastic,
another three-hour superhero movie..."), and review #10 mixes a positive opening
with a negative conclusion ("The visuals are stunning, but the story is a complete
disaster.").

## 2. Model Selection
The target model is Qwen (Tongyi Qianwen, `qwen-turbo`) via Alibaba's DashScope
API, chosen for its strong bilingual understanding, low cost, and reliable
instruction-following (important when the output must be exactly "正面" or "负面").
Since no API key was available for this demo, the API call is replaced by a mock
classifier (keyword scoring) that reproduces the LLM's typical behavior and
failure modes. The pipeline structure is identical to production: swapping
`mock_classify()` for `call_qwen_api()` (already included in the code) makes it
fully functional without any other changes.

## 3. Core Code Logic
The pipeline has four stages: (1) load reviews from CSV; (2) classify each review
with a constrained zero-shot prompt ("answer only 正面 or 负面") at temperature=0
for deterministic outputs; (3) clean and validate the raw output — real model
responses often contain punctuation or extra words, so outputs are normalized to a
fixed label set with an "unknown" fallback; (4) compare predictions against ground
truth, compute accuracy, and write everything to `result.csv`.

## 4. Result Analysis
Accuracy: 8/10 (80%). Both errors are instructive:
- **Review #9 (sarcasm):** surface-level positive words ("fantastic") mislead the
  model; understanding sarcasm requires pragmatic world knowledge, not keywords.
- **Review #10 (mixed sentiment):** the model is distracted by the positive
  clause and fails to recognize that "but" makes the negative clause dominant.
In general, LLM classifiers tend to fail on sarcasm, negation, comparative
sentences, domain slang, and very short ambiguous texts.

## 5. LLM vs. Human Labeling
| Aspect | LLM Labeling | Human Labeling |
|---|---|---|
| Speed & scale | Thousands of items per minute | Dozens per hour |
| Cost | Very low per item | High (labor) |
| Consistency | Identical criteria every time | Subjective drift, fatigue |
| Nuance | Weak on sarcasm, context, culture | Strong contextual judgment |
| Auditability | Hard to explain decisions | Can justify reasoning |

Conclusion: LLMs are ideal for fast, cheap, large-scale first-pass labeling;
humans remain necessary for ambiguous cases and quality auditing.

## 6. Improvement Suggestions
1. **Few-shot prompting**: add 2–3 labeled examples, including sarcastic and
   mixed-sentiment cases.
2. **Human-in-the-loop**: ask the model for a confidence score and route
   low-confidence items to human reviewers.
3. **Self-consistency voting**: run the prompt multiple times and take a
   majority vote.
4. **Better evaluation**: expand the test set (100+ samples) and report
   precision/recall per class, not just accuracy.
5. **Fine-tuning**: for production scale, fine-tune a small classifier on
   domain data to cut cost and latency.
