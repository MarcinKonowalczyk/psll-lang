#! /usr/bin/make
# Sigbovik 2021 psll paper makefile
#
# Written by Marcin Konowalczyk
# Feel free to adapt without attribution (CC0)
#
# I know there is 'latexmk' which probably does much better job than this
# but for a simple project it might be better to have ones own makefile.
# *I*'ve had fun making it anyway. ;)

# All image files + extensions
# In principle could scan the tex for \includegraphics{...} with awk.
IMAGES = test.pdf
NAME = sigbovik-psll # tex file name (without extension)
IMAGES_DIR = img

##################################################

VPATH = $(IMAGES_DIR) # Make searches for files in VPATH

# Spam filter for latex outputs
# Filter out only selected lines, and add a space before the print for more readable output
TEX_FILTER = | awk '{if (
TEX_FILTER += /Class/ || (/Warning/ && !/Font shape declaration/) ||
TEX_FILTER += /Failed/ || /Rerun to get/ ||
TEX_FILTER += /entering/ || /LaTeX2e/ || /Output/ || /Transcript/ ||
TEX_FILTER += /Document Class/ || /For additional/
TEX_FILTER += ) { print " " $$0 } }' # Closing of the awk command

BIB_FILTER = | awk '{if (/BibTeX/ || /Database/) { print " " $$0 } }'
DEV_NULL = > /dev/null

NAME := $(strip $(NAME))

TEX_FLAGS = -halt-on-error # -interaction=nonstopmode
INKSCAPE_FLAGS = --export-text-to-path --export-type=pdf

.PHONY: pdf bib clean open

default: pdf

pdf: $(NAME).pdf
bib: $(NAME).bbl

clean:
	@ rm -f $(NAME).aux $(NAME).log $(NAME)Notes.bib $(NAME).blg $(NAME).bbl
    # Also remove files in the image directory which have a corresponding .svg counterpart
	@ for file in $(IMAGES_DIR)/*; do\
	    if [ "$${file##*.}" == "pdf" ]; then\
	        [[ -f $${file%.*}.svg ]] && rm -f $$file;\
	    fi;\
	done

clean_pdf: clean
	@ rm -rf $(NAME).pdf

# TODO: open recompiles because aux is newer
open: $(NAME).pdf
	open $(NAME).pdf

## Recipies

%.pdf: %.svg
	@ echo "$(notdir $@) <- $(notdir $<)"
	@ inkscape $(INKSCAPE_FLAGS) --export-filename=$(IMAGES_DIR)/$@ $<

$(NAME).pdf: $(NAME).tex bib $(IMAGES)
	@ echo "$(notdir $@) <- $(notdir $<)"
	@ while : ; do\
	    echo "======= PDFLaTeX =======";\
	    pdflatex $(TEX_FLAGS) $< $(TEX_FILTER);\
	    grep --quiet "Rerun to get" $(NAME).log || break;\
	done;

# Compiled bibliography file
$(NAME).bbl: $(NAME).aux $(NAME).bib
	@ echo "$(notdir $@) <- $(notdir $<)"
	@ bibtex $(NAME) $(BIB_FILTER);

# (Re)Compile aux, log and Notes.bib
# Run pdflatex if .tex is newer (-nt flag) that the log file or the aux file
$(NAME).aux $(NAME).log $(NAME)Notes.bib: $(NAME).tex $(IMAGES)
	@ echo "$(notdir $@) <- $(notdir $<)"
	@ if [ $< -nt $(NAME).aux -o $< -nt $(NAME).log ]; then \
	    pdflatex $(TEX_FLAGS) $< $(DEV_NULL); \
	    [[ $$? -eq 0 ]] || ( egrep "^!" sigbovik-psll.log && exit 1 ); \
	fi;
    # We dont want the pdf file from this compilation. Try to delete it even when
    # pdflatex above doesn't run, becasue we don't expect it to exist at this point
	@ rm -f $(NAME).pdf;