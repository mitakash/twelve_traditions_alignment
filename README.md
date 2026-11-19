# twelve_traditions_alignment

This project tests one idea. The idea is that a text based on the 12 Traditions of AA can change how AI models behave on alignment tests.

No model is trained here. Existing models receive a written text as a system prompt. Behavior is then measured with and without the text.

## Status

Draft stage. No model has been run yet. The plan was committed before any results exist, so readers can check that the test was not changed after the data came in.

## Where to start

1. `PLAN.md` holds the full plan, the predictions, the steps and the known limits.
2. `prompts/traditions_voice.md` is the Traditions text where AI has a voice and responsible humans decide.
3. `prompts/traditions_vote.md` is the same text where AI and humans both vote. It differs from the voice version in one line.

## Note on the source

The texts in `prompts/` are new wording written for AI. They adapt the ideas of the 12 Traditions and do not copy the AA text. This project is not affiliated with Alcoholics Anonymous.

## Keys

API keys go in a local file named `.env`. See `.env.example`. Never commit a real key.
