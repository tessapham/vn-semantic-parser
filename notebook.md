02/27/2020

- Wrote `parse.py` script to parse SGML files into Vietnamese texts, English texts, and word alignments in TSV and TXT formats.
- Created Vietnamese and English TXT files in `evbc` folder.

02/28/2020

How to get a parse for a sentence:
- Get a Passage object from XML file.
- Convert Passage object to sentences, each sentence will now become a Passage object.

```
>>> from ucca import convert, visualization
>>> passage = convert.file2passage('N0001_en_0.xml')
>>> sentences = convert.split2sentences(passage)
>>> type(sentences)
<class 'list'>
>>> type(sentences[0])
<class 'ucca.core.Passage'>
>>> visualization.draw(sentences[0])
```

BUT, we won't convert from a paragraph or a whole text to sentences. To avoid dependencies on other sentences (which result in implicit nodes that affect the accuracy of the parse), each Passage will now be one sentence only.

- TODO: Edit `parse.py` script to save each sentence into a separate TXT file.
- Run the TUPA parser on all TXT files:

```
python3 -m tupa *.txt -m models/ucca-bilstm
```
