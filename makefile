# Sigbovik PSLL paper makefile
# Written by Marcin Konowalczyk

IMAGES = logo2.pdf cat.jpg
NAME = sigbovik-psll # tex file name (without extension)
IMAGES_DIR = img

##################################################

VPATH = $(IMAGES_DIR) # Make searches for files in VPATH

# Spam filter for latex outputs
# Filter out only selected lines, and add a space before the print for more readable output
TEX_FILTER = | awk '{if (
TEX_FILTER += /Class/ || (/Warning/ && !/Font shape declaration/) ||
TEX_FILTER += /Failed/ || /Rerun/ ||
TEX_FILTER += /entering/ || /LaTeX2e/ || /Output/ || /Transcript/ ||
TEX_FILTER += /Document Class/ || /For additional/
TEX_FILTER += ) { print " " $$0 } }' # Closing of the awk command

BIB_FILTER = | awk '{if (/BibTeX/ || /Database/) { print " " $$0 } }'
DEV_NULL = > /dev/null

NAME := $(strip $(NAME))

TEX_FLAGS = -halt-on-error # -interaction=nonstopmode

.PHONY: pdf bib clean open

default: pdf

pdf: $(NAME).pdf
bib: $(NAME).bbl

## Recipies

%.pdf: %.svg
	@ echo "PDF <- SVG $@"
	@ inkscape --export-text-to-path --export-type=pdf --export-filename=$(IMAGES_DIR)/$@ $<

clean:
	@ rm -vf $(NAME).aux $(NAME).log $(NAME)Notes.bib $(NAME).pdf $(NAME).blg $(NAME).bbl

open: $(NAME).pdf
	open $(NAME).pdf

$(NAME).pdf: $(NAME).tex $(NAME).bbl $(IMAGES)
	@ echo "$@ <- $<"
	@ while : ; do\
	    echo "======= PDFLaTeX =======";\
	    pdflatex $(TEX_FLAGS) $< $(TEX_FILTER);\
	    grep --quiet "Rerun to get" $(NAME).log || break;\
	done;

# Compiled bibliography file
# Run pdflatex if .tex is newer (-nt flag) that the log file
$(NAME).bbl: $(NAME).aux $(NAME).bib
	@ echo "$@ <- $?"
	@ bibtex $(NAME) $(BIB_FILTER);

# (Re)Compile aux, log and Notes.bib
$(NAME).aux $(NAME).log $(NAME)Notes.bib: $(NAME).tex $(IMAGES)
	@ echo "$@ <- $<"
	@ if [ $< -nt $(NAME).aux -o $< -nt $(NAME).log ]; then \
	    pdflatex $(TEX_FLAGS) $< $(DEV_NULL); \
	    [[ $$? -eq 0 ]] || ( egrep "^!" sigbovik-psll.log && exit 1 ); \
	fi;
    # We dont want the pdf file from this compilation. Try to delete it even when
    # pdflatex above doesn't run, becasue we don't expect it to exist at this point
	@ rm -f $(NAME).pdf;