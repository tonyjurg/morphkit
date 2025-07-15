[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept) 

<img src="images/morphkit.png" width=250 height=250>

A Python toolkit for Greek morphological analysis and tag similairity comparison, leveraging the [Betacode library](https://github.com/perseids-tools/beta-code-py), the API of Morpheus (e.g., running in a [Docker virtualisation environment](https://hub.docker.com/r/perseidsproject/morpheus-api)) and the [Sandborg-Petersen morphological decoder](https://github.com/tonyjurg/Sandborg-Petersen-decoder).

## API features

The following API features are exposed to the end-user:

#### High level functions

* `analyze_word_with_morpheus(word_beta, api_endpoint[, debug])`: Sends a Betacode–encoded word to a Morpheus server and returns a comprehensive analysis, including:
   - The raw response text
   - Individual output blocks
   - Parsed dictionaries of morphological data (including POS and morphologicial Tag)

* `compare_tags(known_tag, generated_tag[, debug])`: Calculates a feature-by-feature similarity between two Sandborg-Petersen morphological tags and produces:
  - A single weighted similarity value (0.0–1.0)
  - Detailed scores for each morphological feature
  
* `annotate_and_sort_analyses(full_analysis, reference_morph, reference_lemma [, various optional arguments] )`: It returns annotated and sorted analyses in a morphkit-compatible structure, grouping by base lemma while appending homonym and pl-suffixes. The sorting is relative to the provided reference lemma and ordered by morph functional similarity.

#### Low level functions

* `get_word_blocks(word_beta, api_endpoint [,language] [,output] [, debug])`: Fetches the raw “block” output from Morpheus for a given word, suitable for downstream parsing.

* `parse_word_block(block [, language] [, debug])`:   Converts one Morpheus output block into a list of parse dictionaries, each containing core morphological fields.

* `analyze_pos(parse[, debug])`: Inspects a parse dictionary’s flags and fields to classify its part of speech (e.g., noun, verb, adverb).

* `analyze_morph_tag(parse[, debug])`: Constructs a Sandborg-Petersen morphological tag (for example, `V-PAI-3S` or `N-NSM`) from the contents of a parse dictionary.

* `decode_tag(tag_input[, debug])`: Breaks down an SP tag string into its human-readable components — such as part of speech, case, number, gender, tense, voice, mood, person, and any suffixes.

* `split_into_raw_blocks(raw_text [,debug])`: Split (full) Morpheus output into analytic blocks.
  
## Installation

Since this not a 'normal package' (yet), you need to import it by adding the relative path to the location where the **directory** /morphkit can be found to the path-search (using `sys.path.insert`). After this, your notebook will be able to load morphkit. 

```python
import sys
sys.path.insert(0, "..")    # the relative path for the morphkit directory to your notebook dir
import morphkit
```

Also install its [dependencies](https://github.com/tonyjurg/morphkit/blob/main/morphkit/requirements.txt):
* [beta-code-py](https://pypi.org/project/beta-code-py/) (for Beta Code ↔ Unicode conversion)
* [requests](https://pypi.org/project/requests/) (for API calls using HTTP to Morpheus)

You will need access to a Morpheus service (see **Usage** below). A Morpheus server can be set up locally (e.g. via the [perseidsproject/morpheus-api Docker image](https://hub.docker.com/r/perseidsproject/morpheus-api)).

## Usage

Some basic usecases for morphkit are:

#### Analyze a Greek word using Morpheus 

```python
import beta_code                             # required lib for morphkit (see requirements.txt)
api_endpoint = "localhost:1315"              # Morpheus API service IP&port

# convert unicode greek to betacode
beta_word_to_decode=beta_code.greek_to_beta_code(u'του') 

# run the analysis on the betacode word
result = morphkit.analyze_word_with_morpheus(beta_word_to_decode, api_endpoint)

# show the part of interest. result["analyses"] is now a list of parse dicts
print(result)      # canonical Beta code form of the word
for parse in result["analyses"]:
    print(parse["lemma_unicode"], parse["sp_morph_tag"])
>>> word=του
>>> result=1: lemma=ὁ  pos='article'  morph=T-GSM/T-GSN
>>> result=2: lemma=τίς  pos='proper noun indeclinable'  morph=N-PRI
>>> result=3: lemma=τις  pos='indefinite pronoun'  morph=X-GS
```
#### Obtain raw Morpheus analytic block

For example the Morpheus analytic block for διακατηλέγχετο ('diakathle/gxeto'; Acts 18:28) shows two prepostions (δια and κατα).
```python
print(morphkit.get_word_blocks('diakathle/gxeto', api_endpoint))
>>> :raw diakathle/gxeto
>>> 
>>> :workw diakathle/gxeto
>>> :lem diakatele/gxomai
>>> :prvb dia/,kata/				
>>> :aug1 e)>h)				
>>> :stem e)legx	 ind			w_stem,reg_conj
>>> :suff 				
>>> :end eto	 imperf ind mp 3rd sg			w_stem

```

#### Decode an SP morphological tag into its parts

```python
morphkit.decode_tag("V-PAI-3S")
>>> {'Part of Speech': 'Verb',
>>> 'Tense': 'Present',
>>> 'Voice': 'Active',
>>> 'Mood': 'Indicative',
>>> 'Person': 'Third Person',
>>> 'Number': 'Singular'}
```

Notes:

 - The function `decode_tag` is an extended version of the online [Sandborg-Petersen-decoder](https://tonyjurg.github.io/Sandborg-Petersen-decoder/).
 - When using the `debug` option elements like `Warning` and 'Error' are added to the returned datastructure (see also section [debug](#debug)).

#### Determine similairity between two SP morphological tags

```
score = morphkit.compare_tags('N-NSN-ATT', 'N-ASM-ATT')
print(f"Similarity: {score['overall_similarity']}")
>>> Similarity: 0.76
print(f"Detailed compare case: {score['details']['Case']}")
>>> Detailed compare case: {'tag1': 'Nominative', 'tag2': 'Accusative', 'similarity': 0.2, 'weight': 4}
```
Note that the algoritm used to determine tag similarity can be reviewed by examining the weights and matrixes found in [init_compare_tags.py](https://github.com/tonyjurg/morphkit/tree/main/morphkit/init_compare_tags.py).

## API Reference

See the detailed docstrings in each module for full parameter and output descriptions.

API | Function
---|---
[morphkit.analyze_word_with_morpheus()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/analyze_word_with_morpheus.py) | *High-level*:  fetch and parse all Morpheus analyses for a Beta-code word, returning a dict with the normalized word and a list of analyses.
[morphkit.parse_word_block()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/parse_word_block.py) | arse one block of Morpheus output (a list of lines with `:raw`, `:stem`, etc.) into a structured parse dictionary (and computes POS and tag).
[morphkit.analyze_pos()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/analyze_pos.py) | Determine the part of speech string from a Morpheus parse dict (based on Morpheus morph codes and flags).
[morphkit.analyze_morph_tag()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/analyze_morph_tag.py) | Generate the SP tag for one parse result from Morpheus (using its features like tense, mood, case).
[morphkit.decode_tag()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/decode_tag.py) | Decode an SP tag string into a dict of features (Part of Speech, Case, Number, etc.).
[morphkit.compare_tags()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/init_compare_tags.py) | **High-level** Similarity evaluator with customizable feature weights and matrices.
[morphkit.get_word_blocks()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/get_word_blocks.py) | Retrieve the raw text output from Morpheus for a Beta-code word.
[morphkit.annotate_and_sort_analyses()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/annotate_and_sort_analyses.py) | sort the analysis blocks according to similairity with provided reference lemma and morph tag.
[morphkit.split_into_raw_blocks()](https://github.com/tonyjurg/morphkit/tree/main/morphkit/split_into_raw_blocks.py) | Split the raw detailed output from Morpheus into blocks that can be anylyzed individual.

## Debug

Each function accepts an optional `debug` flag that allows for printing its internal steps. This flag is automatically passed along to any Morphkit functions invoked internally, so calling the top-level analyze_word_with_morpheus(betacodeWord, baseURL, debug=True) ensures that every routine it calls also emits debug output. This unified trace makes it easy to follow the entire analysis flow from start to finish.

Setting the `debug` flag for `decode_tag` not only prints debug statemnts during function execution, but also adds additonal elements to the returened structure. These additional fields allow for automated validation of decodability of a set of tags.

An example Jupyter Notebook can be [found here (TBA)](TBA).

## Acknowledgements

* Conversion code between Unicode and Betacode available at GitHub repository [perseids-tools/beta-code-py](https://github.com/perseids-tools/beta-code-py).
* [Morpheus Greek Morphological Analyzer](https://github.com/perseids-tools/morpheus/) provided by the Perseus Digital Library.
* [Sandborg-Petersen decoder](https://github.com/tonyjurg/Sandborg-Petersen-decoder)

## Tools used

The standard set of tools ([Python documentation](https://www.python.org/doc/), tech sites like [stackoverflow](https://stackoverflow.com/), and Python syntax checkers like [Pythonium](https://pythonium.net/linter)) were used to create this package. Furthermore, the [Anaconda Assistant](https://www.anaconda.com/capability/anaconda-assistant) (using [OpenAI](https://openai.com/) as backend) and [GitHub Copilot](https://github.com/features/copilot) in Visual Studio were used to debug and/or optimize certain parts of the code.

## Licence

Nog toe te voegen
