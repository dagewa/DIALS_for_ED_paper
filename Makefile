
name=DIALS_for_ED_v3

default: $(name).pdf

$(name).pdf: $(name).tex $(name).bib
	pdflatex $(name).tex
	bibtex $(name).aux
	pdflatex $(name).tex
	pdflatex $(name).tex
	pdflatex $(name).tex

clean:
	rm -vf $(name).aux
	rm -vf $(name).log
	rm -vf $(name).dvi
	rm -vf $(name).pdf
	rm -vf $(name).out
	rm -vf $(name).bbl
	rm -vf $(name).blg
