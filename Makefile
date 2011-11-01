INPUT_FILE_NAME = zorp_tutorial_en.asciidoc
OUTPUT_FILE_BASENAME = zorp_tutorial_en
ICONS_DIR = images/icons

HTML_ATTRIBUTES = --attribute toc2 --attribute data-uri --attribute numbered
HTML_THEME = flask

PDF_ATTRIBUTES = --attribute docinfo

pdf:
	asciidoc --backend docbook --doctype book $(PDF_ATTRIBUTES) --out-file $(OUTPUT_FILE_BASENAME).xml $(INPUT_FILE_NAME)
	dblatex --type pdf --quiet --fig-path $(ICONS_DIR) --output $(OUTPUT_FILE_BASENAME).pdf $(OUTPUT_FILE_BASENAME).xml

html:
	asciidoc --backend html --theme $(HTML_THEME) $(HTML_ATTRIBUTES) --out-file $(OUTPUT_FILE_BASENAME).html $(INPUT_FILE_NAME)

html5:
	asciidoc --backend html5 --theme $(HTML_THEME) $(HTML_ATTRIBUTES) --out-file $(OUTPUT_FILE_BASENAME).html $(INPUT_FILE_NAME)

check: html html5 pdf
